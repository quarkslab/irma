Installation Checks
-------------------

Celery Workers
``````````````

Before going further, you should check that the python application manages to
communicate with the RabbitMQ server and the Redis server through Celery. To
ensure that, from the installation directory, execute the Celery worker:

On GNU/Linux:

.. code-block:: bash

    $ celery worker --app=frontend.tasks:frontend_app

     -------------- celery@frontend v3.1.13 (Cipater)
    ---- **** -----
    --- * ***  * -- Linux-3.2.0-4-amd64-x86_64-with-debian-7.6
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         frontend.tasks:0x1e18750
    - ** ---------- .> transport:   amqp://probe:**@brain:5672/mqfrontend
    - ** ---------- .> results:     disabled
    - *** --- * --- .> concurrency: 1 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> brain            exchange=celery(direct) key=brain

    [2014-08-20 15:28:58,745: WARNING/MainProcess] celery@frontend ready.

If your Celery worker does not output something similar to the above output,
you should check twice the parameters in the application configuration file you
are using. Let us note that the Celery worker gives us useful information on
the analyzer that are enabled.

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

    $ curl http://localhost/_api/probe/list
    {"msg": "success", "code": 0, "probe_list": ["ClamAV", "ComodoCAVL", "EsetNod32", "FProt", "Kaspersky", "McAfeeVSCL", "NSRL", "StaticAnalyzer", "VirusTotal"]}
    $ sudo cat /var/log/uwsgi/app/frontend-api.log
    Wed Aug 20 17:51:33 2014 - *** Starting uWSGI 1.2.3-debian (64bit) on [Wed Aug 20 17:51:33 2014] ***
    Wed Aug 20 17:51:33 2014 - compiled with version: 4.7.2 on 06 July 2013 12:20:09
    Wed Aug 20 17:51:33 2014 - detected number of CPU cores: 4
    Wed Aug 20 17:51:33 2014 - current working directory: /
    Wed Aug 20 17:51:33 2014 - writing pidfile to /run/uwsgi/app/frontend-api/pid
    Wed Aug 20 17:51:33 2014 - detected binary path: /usr/bin/uwsgi-core
    Wed Aug 20 17:51:33 2014 - setgid() to 33
    Wed Aug 20 17:51:33 2014 - setuid() to 33
    Wed Aug 20 17:51:33 2014 - your memory page size is 4096 bytes
    Wed Aug 20 17:51:33 2014 - detected max file descriptor number: 1024
    Wed Aug 20 17:51:33 2014 - lock engine: pthread robust mutexes
    Wed Aug 20 17:51:33 2014 - uwsgi socket 0 bound to UNIX address /run/uwsgi/app/frontend-api/socket fd 3
    Wed Aug 20 17:51:33 2014 - Python version: 2.7.3 (default, Mar 13 2014, 11:26:58)  [GCC 4.7.2]
    Wed Aug 20 17:51:33 2014 - *** Python threads support is disabled. You can enable it with --enable-threads ***
    Wed Aug 20 17:51:33 2014 - Python main interpreter initialized at 0x264e120
    Wed Aug 20 17:51:33 2014 - your server socket listen backlog is limited to 100 connections
    Wed Aug 20 17:51:33 2014 - *** Operational MODE: preforking ***
    Wed Aug 20 17:51:33 2014 - mounting ./frontend/web/api.py on /_api
    Wed Aug 20 17:51:33 2014 - WSGI app 0 (mountpoint='/_api') ready in 0 seconds on interpreter 0x264e120 pid: 7860 (default app)
    Wed Aug 20 17:51:33 2014 - *** uWSGI is running in multiple interpreter mode ***
    Wed Aug 20 17:51:33 2014 - spawned uWSGI master process (pid: 7860)
    Wed Aug 20 17:51:33 2014 - spawned uWSGI worker 1 (pid: 7892, cores: 1)
    Wed Aug 20 17:51:33 2014 - spawned uWSGI worker 2 (pid: 7893, cores: 1)
