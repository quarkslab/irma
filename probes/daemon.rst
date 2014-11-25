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

.. literalinclude:: service.ini

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

Starting and stopping the service
*********************************

Before starting the service, one should debug it to see if the service works
correctly. This can be done by launching the binary ``pythonservice.exe`` in
charge of launching the service. Let us note that the worker keeps on working
even if an error due to ``libmagic`` (see output below) is raised. This error
is not critical as long as we do not enable ``StaticAnalyzer`` probe. Please
check the documentation if you want to solve this issue and to enable the
``StaticAnalyzer`` probe on Microsoft Windows systems.

.. code-block:: none

    $ C:\Python27\Lib\site-packages\win32\pythonservice.exe -debug irma-service
    Debugging service irma-service - press Ctrl+C to stop.
    Info 0x400000FF - Initialization
    Info 0x400000FF - c:\irma\irma-probe\extras\winsrv\service.ini
    Info 0x400000FF - starting
    Info 0x400000FF - Spawned c:\Python27\python.exe -m celery worker --app=probe.tasks --workdir=c:\irma\irma-probe -f c:\irma\irma-probe\celery.log -l info
    Info 0x400000FF - Started. Waiting for stop
    No handlers could be found for logger "multiprocessing"
    starting command: c:\Python27\python.exe -m celery worker --app=probe.tasks --workdir=c:\irma\irma-probe -f c:\irma\irma-probe\celery.log -l info
    WARNING:root: *** [plugin] Plugin failed to load: ClamAV miss dependencies: linux (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: ComodoCAVL miss dependencies: linux (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: EsetNod32 miss dependencies: linux (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: FProt miss dependencies: linux (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: KasperskyPlugin: verify() failed because Kaspersky executable was not found.
    WARNING:root: *** [plugin] Plugin failed to load: McAfeeVSCLPlugin: verify() failed because McAfeeVSCL executable was not found.
    WARNING:root: *** [plugin] Plugin failed to load: SophosPlugin: verify() failed because Sophos executable was not found.
    WARNING:root: *** [plugin] Plugin failed to load: Unable to find Symantec executable
    WARNING:root: *** [plugin] Plugin failed to load: NSRL miss dependencies: leveldict (ModuleDependency). See requirements.txt for needed dependencies
    ERROR:root:failed to find libmagic.  Check your installation
    Traceback (most recent call last):
      File "c:\irma\irma-probe\lib\plugins\manager.py", line 58, in discover
        module = module_meta.load_module(pkg_name)
      File "c:\Python27\lib\pkgutil.py", line 246, in load_module
        mod = imp.load_module(fullname, self.file, self.filename, self.etc)
      File "c:\irma\irma-probe\modules\metadata\pe_analyzer\pe.py", line 20, in <module>
        from lib.common.mimetypes import Magic
      File "c:\irma\irma-probe\lib\common\mimetypes.py", line 20, in <module>
        import magic
      File "c:\Python27\lib\site-packages\magic.py", line 161, in <module>
        raise ImportError('failed to find libmagic.  Check your installation')
    ImportError: failed to find libmagic.  Check your installation
    WARNING:root: *** [plugin] Plugin failed to load: StaticAnalyzer miss dependencies: modules.metadata.pe_analyzer.pe (ModuleDependency).
     
     -------------- celery@irma-probe v3.1.13 (Cipater)
    ---- **** -----
    --- * ***  * -- Windows-7-6.1.7601-SP1
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         probe.tasks:0x2f08ff0
    - ** ---------- .> transport:   amqp://probe:**@brain:5672/mqprobe
    - ** ---------- .> results:     amqp://probe:**@brain:5672/mqprobe
    - *** --- * --- .> concurrency: 1 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> VirusTotal       exchange=celery(direct) key=VirusTotal
     
     
    [tasks]
      . probe.tasks.probe_scan

The service can be manually started and stopped with the following commands:

.. code-block:: none

    $ C:\Python27\python.exe extras/winsrv/service.py start
    $ C:\Python27\python.exe extras/winsrv/service.py stop

Removing the service
********************

It can be removed with the following commands:

.. code-block:: none

    $ C:\Python27\python extras/winsrv/service.py remove
