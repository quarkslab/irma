Running Frontend worker at startup
----------------------------------

We have ensured that the freshly installed Frontend worker is ready to be
integrated to your IRMA platform. Now, we can go a step further and make it run
automatically when the system starts up so you will not need to relaunch it
manually every time.

We provide several template scripts in the ``extras/`` repository located at
the root of the installation directory. We describe in the following how to
setup daemons on GNU/Linux systems, specifically Debian systems.

Daemon on GNU/Linux
```````````````````

At the moment, we only support daemonizing with ``init.d`` scripts. The
following describes the procedure to run make a service run Celery workers on
Debian distribution.

Installing the service
**********************

First, copy the scripts in ``extras/init.d/`` and ``extras/default``
respectively in ``/etc/init.d`` and ``/etc/defaults``.

.. code-block:: bash

    $ sudo cp extras/init.d/celeryd.probe /etc/init.d/celeryd.frontend
    $ sudo cp extras/default/celeryd.probe /etc/default/celeryd.frontend

Configuring the service
***********************

Update the service parameters in ``extras/default/celeryd.frontend`` to match
your setup. In most cases, you should pay attention to the following fields:

================= ======================== ==========================================
Fields            Default                  Description
================= ======================== ==========================================
``CELERYD_NODES`` frontend                 Name given to the probe
``CELERYD_CHDIR`` /opt/irma/irma-frontend/ Installation directory for the frontend
``CELERYD_USER``  irma                     Username used to execute the Celery worker
``CELERYD_GROUP`` irma                     Group used to execute the Celery worker
================= ======================== ==========================================

Registering the service
***********************

Finally, fix the permission for the ``/etc/init.d/celeryd.frontend`` script and
register the service:

.. code-block:: bash

    $ sudo chmod u+x /etc/init.d/celeryd.frontend
    $ update-rc.d celeryd.frontend defaults

You can check that the celery daemon is running properly by launching it and by
consulting the system logs:

.. code-block:: bash

    $ sudo invoke-rc.d celeryd.probe start
    $ sudo cat /var/log/celery/*.log
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker1@frontend ready.
    [...]
    [2014-04-30 13:35:04,205: WARNING/MainProcess] worker2@frontend ready.
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker3@frontend ready.
