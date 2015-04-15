Running Brain at startup
------------------------

We have ensured that the freshly installed **Brain** is ready to be integrated
to your IRMA platform. Now, we can go a step further and make the celery
worker to run automatically when the system starts up so you will not need to
manually relaunch it every time.

We provide several template scripts in the ``extras/`` repository located at
the root of the installation directory. We describe in the following how to
setup daemons on a GNU/Linux system.

Daemon on GNU/Linux
```````````````````

At the moment, we only support daemonizing with ``init.d`` scripts. The
following describes the procedure to make a service run Celery workers on
Debian distribution.

Installing the services
***********************

First, copy the scripts in ``extras/init.d/`` and ``extras/default``
respectively in ``/etc/init.d`` and ``/etc/defaults``.

.. code-block:: bash

    $ sudo cp extras/init.d/celeryd.brain /etc/init.d/celeryd.brain
    $ sudo cp extras/init.d/celeryd.results /etc/init.d/celeryd.results
    $ sudo cp extras/default/celeryd.brain /etc/default/celeryd.brain
    $ sudo cp extras/default/celeryd.results /etc/default/celeryd.results

Configuring the services
************************

Update the service parameters in ``/etc/default/celeryd.brain`` and
``/etc/default/celeryd.brain`` to match your setup. In most cases, you should
pay attention to the following fields:

================= ===================== ===========================================
Fields            Default               Description
================= ===================== ===========================================
``CELERYD_NODES``                       Name given to the worker
``CELERYD_CHDIR`` /opt/irma/irma-brain/ Installation directory for the worker
``CELERYD_USER``  irma                  Username used to execute the Celery worker
``CELERYD_GROUP`` irma                  Group used to execute the Celery worker
================= ===================== ===========================================

Registering the services
************************

Finally, fix the permission for the ``/etc/init.d/celeryd.brain`` and the
``/etc/init.d/celeryd.results`` scripts and register the two services:

.. code-block:: bash

    $ sudo chmod u+x /etc/init.d/celeryd.brain
    $ sudo chmod u+x /etc/init.d/celeryd.results
    $ update-rc.d celeryd.brain defaults
    $ update-rc.d celeryd.results defaults

You can check that the celery daemon is running properly by launching it and by
consulting the system logs:

.. code-block:: bash

    $ sudo invoke-rc.d celeryd.brain start
    $ sudo invoke-rc.d celeryd.results start
    $ sudo cat /var/log/celery/*.log
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker1@irma-brain ready.
    [...]
