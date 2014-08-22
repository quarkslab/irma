Running Probes at startup
-------------------------

We have ensured that the freshly installed **Probe** is ready to be integrated
to your IRMA platform. Now, we can go a step further and make the python
application run automatically when the system starts up so you will not need to
relaunch manually the workers every time.

We provide several template scripts in the ``extras/`` repository located at
the root of the installation directory. We describe in the following how to
setup daemons on Microsoft Windows and GNU/Linux systems which roles is to run
the Celery worker at startup.

Daemon on GNU/Linux
```````````````````

At the moment, we only support daemonizing with ``init.d`` scripts. The
following describe the procedure to run make a service run Celery workers on
Debian distribution.

Installing the service
**********************

First, copy the scripts in ``extras/init.d/`` and ``extras/default``
respectively in ``/etc/init.d`` and ``/etc/defaults``.

.. code-block:: bash

    $ sudo cp extras/init.d/celeryd.probe /etc/init.d/celeryd.probe
    $ sudo cp extras/default/celeryd.probe /etc/default/celeryd.probe

Configuring the service
***********************

Update the service parameters in ``extras/default/celeryd.probe`` to match your
setup. In most cases, you should pay attention to the following fields:

================= ===================== ====================================
Fields            Default               Description
================= ===================== ====================================
``CELERYD_NODES`` probe                 Name given to the probe
``CELERYD_CHDIR`` /opt/irma/irma-probe/ Installation directory for the probe
``CELERYD_USER``  irma                  Username used to execute the Celery worker 
``CELERYD_GROUP`` irma                  Group used to execute the Celery worker
================= ===================== ====================================

Registering the service
***********************

Finally, fix the permission for the ``/etc/init.d/celeryd.probe`` script and
register the service:

.. code-block:: bash

    $ sudo chmod u+x /etc/init.d/celeryd.probe
    $ update-rc.d celeryd.probe defaults

You can check that the celery daemon is running properly by launching it and by
consulting the system logs:

.. code-block:: bash

    $ sudo invoke-rc.d celeryd.probe start
    $ sudo cat /var/log/celery/*.log
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker1@irma-probe ready.
    [...]
    [2014-04-30 13:35:04,205: WARNING/MainProcess] worker2@irma-probe ready.
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker3@irma-probe ready.

Daemon on Microsoft Windows
```````````````````````````

On Microsoft Windows, many solution exists to make the Celery worker run at
startup. The recommended way to perform that would be to register a Windows
service.

Pre-requisites
**************

For that purpose, you will need first to download and install the lastest build
of `pywin32 <http://sourceforge.net/projects/pywin32/files/pywin32/>`_ .

Configuring the service
***********************

Then, you will have to adapt the file located in ``extras/winsrv/service.ini``
to your installation. In particular, you should pay attention to the various
paths indicated in the configuration file. 

The default ``service.ini`` looks like the following. Let us recall that we
have installed the application in ``C:\irma\irma-probe``:

.. literalinclude:: ../../extras/winsrv/service.ini

The ``services`` section contains:

* The list of background commands to run (``celeryd``) in the run directive.
* The list of files to delete when refreshed or stopped in the clean directive.

The ``celeryd`` section contains the commands to run for the ``celeryd``
service that is going to be run:

* ``command`` specifies the command to run
* ``parameters`` specifies the arguments passed to the command.

This is equivalent to launching the following command from the CLI:

.. code-block:: none

    $ c:\Python27\python.exe -m celery worker --app=probe.tasks --workdir=c:\irma\irma-probe -f c:\irma\irma-probe\celery.log -l info

The ``log`` section defines a log file and logging level for the service process
itself.

Installing the service
**********************

You need to have administrator privileges to install the service in the Windows
Registry so that it is started each time the system boots:

.. code-block:: none

    $ C:\Python27\python.exe extras/winsrv/service.py --startup=auto install

The ``--startup=auto`` makes the service to start automatically when the system
boots. You can check that the service has been effectively installed by
consulting the list of Microsoft Windows Services.

Removing the service
********************

It can be removed with the following commands:

.. code-block:: none

    $ C:\Python27\python extras/winsrv/service.py remove

Starting and stopping the service
*********************************

The service can be manually started and stopped with the following commands:

.. code-block:: none

    $ C:\Python27\python.exe extras/winsrv/service.py start
    $ C:\Python27\python.exe extras/winsrv/service.py stop
