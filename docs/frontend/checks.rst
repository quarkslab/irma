Installation Checks
-------------------

Celery Workers
``````````````

Before going further, you should check that the python application manages to
communicate with the RabbitMQ server and the Redis server through Celery. To
ensure that, from the installation directory, execute the Celery worker:

On GNU/Linux:

.. code-block:: bash

    $ cd /opt/irma/irma-frontend/current
    $ ./venv/bin/python -m api.tasks.frontend_app

     -------------- celery@frontend v3.1.23 (Cipater)
    ---- **** -----
    --- * ***  * -- Linux-3.2.0-4-amd64-x86_64-with-debian-7.6
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         frontend.tasks:0x1e18750
    - ** ---------- .> transport:   amqp://probe:**@brain:5672/mqfrontend
    - ** ---------- .> results:     disabled
    - *** --- * --- .> concurrency: 2 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> frontend            exchange=celery(direct) key=frontend

    [2014-08-20 15:28:58,745: WARNING/MainProcess] celery@frontend ready.

If your Celery worker does not output something similar to the above output,
you should check twice the parameters in the application configuration file you
are using. Let us note that the Celery worker gives us useful information on
the analyzer that are enabled.

SFTP accounts
`````````````

Defaut File Transport Protocol since v1.4.0 is now SFTP, you can check whether the configured account is valid.

.. code-block:: bash

    $ sftp <user>@<hostname of the brain>


FTP-TLS accounts
````````````````

Additionnally, if you have configured IRMA to use FTP-TLS, you can check
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
    Name (brain:root): frontend-ftp
    500 This security scheme is not implemented
    234 AUTH TLS OK.
    [SSL Cipher DHE-RSA-AES256-GCM-SHA384]
    200 PBSZ=0
    200 Data protection level set to "private"
    331 User probe OK. Password required
    Password: frontend-ftp-password
    230 OK. Current directory is /
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp>


Restful API
```````````

One can verify that the restful API is up and running by querying a specific
route on the web server or by checking the system logs:

.. code-block:: bash

    $ curl http://localhost/api/v1.1/probes
    {"total": 9, "data": ["ClamAV", "ComodoCAVL", "EsetNod32", "FProt", "Kaspersky", "McAfeeVSCL", "NSRL", "StaticAnalyzer", "VirusTotal"]}

    $  sudo cat /var/log/supervisor/frontend_api.log
    [...]
    added /opt/irma/irma-frontend/current/venv/ to pythonpath.
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI master process (pid: 3943)
    spawned uWSGI worker 1 (pid: 3944, cores: 1)
    spawned uWSGI worker 2 (pid: 3945, cores: 1)
    spawned uWSGI worker 3 (pid: 3946, cores: 1)
    spawned uWSGI worker 4 (pid: 3947, cores: 1)
    mounting frontend/api/base.py on /api
    mounting frontend/api/base.py on /api
    mounting frontend/api/base.py on /api
    mounting frontend/api/base.py on /api
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3945 (default app)
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3946 (default app)
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3944 (default app)
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3947 (default app)

