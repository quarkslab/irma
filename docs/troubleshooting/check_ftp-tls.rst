FTP-TLS accounts
````````````````

Additionnally, if you have configured IRMA to use FTP-TLS, you can check
whether the configured account is valid. On Debian, this can be done with the
``ftp-ssl`` package:

.. code-block:: console

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
