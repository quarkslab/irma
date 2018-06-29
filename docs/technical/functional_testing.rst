Functional Testing
------------------

**Only available on *dev* environments**

On the frontend, to launch the functionals tests:

.. code-block:: console

    $ cd /opt/irma/irma-frontend/current/web
    $ npm run functional-tests

It will launch the Javascript implementation of `Cucumber
<https://cucumber.io/>`_. Cucumber.js will take a file that contain test
scenarios, written using the `Gherkin language
<https://cucumber.io/docs/reference>`_).
For each steps of a scenario, an action is perform by Cucumber.js, like
accessing a web page and typing some texts in a form. In order to do that, IRMA
project uses `Puppeteer
<https://github.com/GoogleChrome/puppeteer>`_, a software that can launch and
control a `Chromium <https://www.chromium.org/>`_ instance in `headless
<https://chromium.googlesource.com/chromium/src/+/lkgr/headless/README.md>`_
mode.

IRMA scenarios can be found in ``frontend/web/tests/functionals/*.feature`` and
actions used to perform these steps are available in the file
``frontend/web/tests/functionals/support/steps.js``.

When an error occured, you will get a screenshot of the page where the scenario
ends. It will be available on the VM at ``frontend/web/error.jpeg``.


Debug
+++++

Using the headless mode of Chromium, it will be difficult to debug if an error
occured.

You can launch the test using a real Chromium instance on your host:
 - You'll need `NodeJS <https://nodejs.org/>`_ and `NPM
   <https://www.npmjs.com/>`_
 - Install IRMA web interface devDependencies on your host

   .. code-block:: console

       $ cd frontend/web
       $ npm install --only=dev

 - Update the ``ROOT_URL`` (see:
   ``frontend/web/tests/functionals/support/steps.js``) variable to the
   location of your IRMA web url (for example: ``const
   ROOT_URL="http://172.16.1.30"``) and toggle the ``HEADLESS`` variable to
   ``false`` (see: ``frontend/web/tests/functionals/support/hooks.js``)
 - Run the tests:

   .. code-block:: console

       $ npm run functional-tests


You can also use the power of X11 Forwarding through SSH to see a real browser
launching the tests on the VM and getting the result on the host, without
having to install NodeJS:

.. code-block:: console

    $ vagrant ssh # to connect as vagrant user/superuser
    $ sudo apt-get install xorg # to install a X11 server to launch Chromium
    $ sudo sed -i "s/^X11Forwarding .*/X11Forwarding yes/" /etc/ssh/sshd_config
    $ sudo systemctl restart sshd
    $ exit # disconnect from vagrant user
    $ vagrant ssh -- -l deploy -X # to connect as deploy with XForwarding enable
    $ cd /opt/irma/irma-frontend/current/web
    $ sed -i "s/^const HEADLESS = true;/const HEADLESS = false;/" tests/functionals/support/hooks.js
    $ npm run functional-tests

You should see an instance of a Chromium browser on your host machine, running
the tests.

Take a look at the argument pass to the ``puppeteer.launch()`` function in
``frontend/web/tests/functionals/support/hooks.js``. For example, by modifying
the ``SLOW_MOTION_DELAY`` you can force Puppeteer to slow down its operations.
