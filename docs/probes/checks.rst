Installation Checks
-------------------

Celery Workers
``````````````

Before going further, you should check that the python application manages to
communicate with the RabbitMQ server and the Redis server through Celery. To
ensure that, from the installation directory, execute the Celery worker:

On GNU/Linux:

.. code-block:: bash

    $ cd /opt/irma/irma-probe/current
    $ ./venv/bin/celery worker --app=probe.tasks
    $ celery worker --app=probe.tasks:app --workdir=/opt/irma/irma-probe/current
    WARNING:root: *** [plugin] Plugin failed to load: Kaspersky miss dependencies: win32 (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: Sophos miss dependencies: win32 (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: Symantec miss dependencies: win32 (PlatformDependency).
    WARNING:root: *** [plugin] Plugin failed to load: NSRL miss dependencies: leveldict (ModuleDependency). See requirements.txt for needed dependencies
    WARNING:root: *** [plugin] Plugin failed to load: VirusTotal miss dependencies: virus_total_apis (ModuleDependency). See requirements.txt for needed dependencies
    WARNING:root: *** [plugin] Plugin failed to load: StaticAnalyzer miss dependencies: pefile (ModuleDependency). See requirements.txt for needed dependencies

     -------------- celery@irma-probe v3.1.13 (Cipater)
    ---- **** -----
    --- * ***  * -- Linux-3.2.0-4-amd64-x86_64-with-debian-7.6
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         probe.tasks:0x1e18750
    - ** ---------- .> transport:   amqp://probe:**@brain:5672/mqprobe
    - ** ---------- .> results:     redis://brain:6379/1
    - *** --- * --- .> concurrency: 1 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> ClamAV           exchange=celery(direct) key=ClamAV
                    .> ComodoCAVL       exchange=celery(direct) key=ComodoCAVL
                    .> EsetNod32        exchange=celery(direct) key=EsetNod32
                    .> FProt            exchange=celery(direct) key=FProt
                    .> McAfeeVSCL       exchange=celery(direct) key=McAfeeVSCL

    [2014-08-19 18:25:06,469: WARNING/MainProcess] celery@irma-probe ready.

The equivalent command on Microsoft Windows is:

.. code-block:: none

    $ C:\Python27\Scripts\celery.exe worker --app=probe.tasks:app --workdir=C:\irma\irma-probe\current
    [...]

If your Celery worker does not output something similar to the above output,
you should check twice the parameters in the application configuration file you
are using. Let us note that the Celery worker gives us useful information on
the analyzer that are enabled. As each analyzer connects to a dedicated queue,
we can deduce, in this example, that the analyzers ``ClamAV``, ``ComodoCAVL``,
``EsetNod32``, ``FProt`` and ``McAfeeVSCL`` are enabled and ready to serve.


SFTP accounts
`````````````

Defaut File Transport Protocol since v1.4.0 is now SFTP, you can check whether the configured account is valid.

.. code-block:: bash

    $ sftp <user>@<hostname of the brain>


FTP-SSL accounts
````````````````

Additionnally, if you have configured IRMA to use FTP-ssl, you can check
whether the configured account is valid. On Debian, this can be done with the
``ftp-ssl`` package:

.. code-block:: bash

    $ sudo apt-get install ftp-ssl
    [...]
    $ ftp-ssl <hostname of the brain>
    Connected to brain.
    220---------- Welcome to Pure-FTPd [privsep] [TLS] ----------
    220-You are user number 1 of 50 allowed.
    220-Local time is now 18:55. Server port: 21.
    220-This is a private system - No anonymous login
    220-IPv6 connections are also welcome on this server.
    220 You will be disconnected after 15 minutes of inactivity.
    Name (brain:root): probe-ftp
    500 This security scheme is not implemented
    234 AUTH TLS OK.
    [SSL Cipher DHE-RSA-AES256-GCM-SHA384]
    200 PBSZ=0
    200 Data protection level set to "private"
    331 User probe OK. Password required
    Password: probe-ftp-password
    230 OK. Current directory is /
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp>
