Installation Checks
-------------------

Celery Workers
``````````````

Before going further, you should check that the python application manages to
communicate with the RabbitMQ server and the Redis server through Celery. To
ensure that, from the installation directory, execute the Celery worker:

On GNU/Linux:

.. code-block:: bash

    $ celery worker --app=brain.tasks:scan_app --workdir=/opt/irma/irma-brain

 
     -------------- celery@irma-brain v3.1.13 (Cipater)
    ---- **** ----- 
    --- * ***  * -- Linux-3.2.0-4-amd64-x86_64-with-debian-7.5
    -- * - **** --- 
    - ** ---------- [config]
    - ** ---------- .> app:         scantasks:0x1f4c2d0
    - ** ---------- .> transport:   amqp://brain:**@127.0.0.1:5672/mqbrain
    - ** ---------- .> results:     amqp://brain:brain@127.0.0.1:5672/mqbrain
    - *** --- * --- .> concurrency: 4 (prefork)
    -- ******* ---- 
    --- ***** ----- [queues]
     -------------- .> brain            exchange=celery(direct) key=brain
                    
    
    [2014-08-21 14:54:49,633: WARNING/MainProcess] celery@brain ready.


    $ celery worker --app=brain.tasks:results_app --workdir=/opt/irma/irma-brain
     
     -------------- celery@irma-brain v3.1.13 (Cipater)
    ---- **** ----- 
    --- * ***  * -- Linux-3.2.0-4-amd64-x86_64-with-debian-7.5
    -- * - **** --- 
    - ** ---------- [config]
    - ** ---------- .> app:         restasks:0x19fe0d0
    - ** ---------- .> transport:   amqp://probe:**@127.0.0.1:5672/mqprobe
    - ** ---------- .> results:     disabled
    - *** --- * --- .> concurrency: 4 (prefork)
    -- ******* ---- 
    --- ***** ----- [queues]
     -------------- .> results          exchange=celery(direct) key=results
                    
    
    [2014-08-21 14:55:59,079: WARNING/MainProcess] celery@irma-brain ready.

If your Celery worker does not output something similar to the above output,
you should check twice the parameters in the application configuration file you
are using.

FTP-SSL accounts
````````````````

Additionnally, if you have configured IRMA to use FTP-ssl, you can check
whether the configured account is valid. On Debian, this can be done with the
``ftp-ssl`` package:

.. code-block:: bash

    $ sudo apt-get install ftp-ssl
    [...]
    $ ftp-ssl localhost
    Connected to localhost.
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

    $ ftp-ssl localhost
    Connected to localhost.
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
