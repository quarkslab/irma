Installation
------------

The **Frontend** must be installed on a GNU/Linux system. With some efforts, it
should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

This section describes how to get the source code of the application and to
install it.

Pre-requisites
++++++++++++++

We assume that you have a command line interface on your system with
the following tools installed:

* python 3.4.x and newer
* python3-pip (see `Install pip <https://pip.pypa.io/en/latest/installing.html>`_
  for the recommended way to install pip package manager)

Furthermore, we assume that you have created an user ``irma`` that will be used
to run the python application.

.. note:: On GNU/Linux, one can create the user (and the group) ``irma`` with:

    .. code-block:: bash

        $ sudo adduser --system --no-create-home --group irma


Installation on GNU/Linux
+++++++++++++++++++++++++

On GNU/Linux system, we will assume that the code for the **Frontend** will be
installed in ``/opt/irma/irma-frontend/current`` directory, which is the configured default
installation directory.

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``common`` that is a soft-link (``lib``), do not forget the ``dereference``
option of ``cp`` (``-L``):

.. code-block:: bash

    $ git clone https://github.com/quarkslab/irma /opt/irma/src
    $ cp -rL /opt/irma/src/frontend /opt/irma/irma-frontend/current

We need few dependencies for future steps:

    $ sudo apt-get install python3-virtualenv python3-dev


then, we need to install python dependencies manually in a virtualenv :

.. code-block:: bash

    $ virtualenv --system-site-packages /opt/irma/irma-frontend/current/venv
    $ /opt/irma/irma-frontend/current/venv/bin/pip install -r /opt/irma/irma-frontend/current/requirements.txt
    [...]

Building the web client
***********************

The first step that should be performed when installing the frontend from the
code source is to build the web client which is composed of static HTML files
mixed with javascript web framework (in particular, AngularJS).

One must install first some tools that are necessary to build the whole web
client:

.. code-block:: bash

    $ curl -sL https://deb.nodesource.com/setup | sudo bash -
    [...]
    $ sudo apt-get install -y nodejs
    [...]
    $ curl -sL https://www.npmjs.org/install.sh | sudo bash -
    [...]

Once the tools installed, you can build the static files for the web user
interface with the following commands, executed from the installation
directory:

.. code-block:: bash

    $ cd irma-frontend/current/web
    $ sudo npm install
    $ sudo node_modules/.bin/bower install --allow-root
    $ sudo node_modules/.bin/gulp dist

A new directory or an updated directory ``web/dist`` should appear now with
HTML and javascript files that have been minified and "obfuscated" by ``gulp``.
For more details on the web interface, please refer to the dedicated chapter.

If everything has gone well, you should have installed the python application
on your system. The next step is to configure it for your platform and to
install the other components it relies on.
