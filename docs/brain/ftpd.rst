Installing and configuring Pure-ftpd
====================================

A FTP server with TLS is used to store file to are uploaded by
**Frontends** and meant to be analyzed by **Probes**. We describe in the
following how to set up pure-ftpd. 

Installing pure-ftpd
````````````````````

.. code-block:: bash

    $ sudo apt-get install pure-ftpd

Creating FTP specific users and groups
``````````````````````````````````````

.. code-block:: bash

    $ sudo groupadd ftpgroup
    $ sudo useradd -g ftpgroup -d /dev/null -s /etc ftpuser

Configure pure-ftpd
```````````````````

We provide some template scripts to configure ``pure-ftpd`` in the
``extras/pure-ftpd`` directory. These templates should be copied as is in the
``pure-ftpd`` configuration folder.

.. code-block:: bash

    $ sudo cp ../extras/pure-ftpd/conf/* /etc/pure-ftpd/conf/
    $ sudo ln -s /etc/pure-ftpd/conf/PureDB /etc/pure-ftpd/auth/50puredb

Generate Certificate
````````````````````

So far, we have not set up support for TLS yet. To enable TLS, one must
generate a self signed certificate:

.. code-block:: bash

    $ sudo mkdir -p /etc/ssl/private/
    $ cd /etc/ssl/private/
    $ sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 -subj "/CN=$(hostname --fqdn)/" -keyout pure-ftpd.pem -out pure-ftpd.pem
    $ sudo chmod 600 pure-ftpd.pem

Create FTP accounts
```````````````````

The creation of virtual users (or FTP accounts) could be done through the
provided script in ``extras/scripts/pure-ftpd/ftpd-adduser.sh``:

.. code-block:: bash

    $ sudo extras/scripts/pure-ftpd/ftpd-adduser.sh 
    Usage: sudo ftpd-adduser.sh <user> <virtualuser> <chroot home>

The frontends need an account with ``/home/ftpuser/<frontend-name>`` as home
directory and a single account is shared between probes. The later needs to
access to all frontends, thus the associated home directory is simply
``/home/ftpuser/``. For instance, a frontend named ``frontend-irma``, execute
the following to create the directories:

.. code-block:: bash

    $ sudo mkdir -pv /home/ftpuser/frontend-irma
    mkdir: created directory `/home/ftpuser'
    mkdir: created directory `/home/ftpuser/frontend-irma'
    $ sudo chown -R ftpuser:ftpgroup /home/ftpuser

These commands create the accounts for this frontend first and secondly for
probes:

.. code-block:: bash

    $ sudo extras/scripts/pure-ftpd/ftpd-adduser.sh frontend-irma ftpuser /home/ftpuser/frontend-irma
    $ sudo extras/scripts/pure-ftpd/ftpd-adduser.sh probe ftpuser /home/ftpuser/

Checking your configuration
```````````````````````````

Listing your users should output something like this:

.. code-block:: bash

    $ sudo pure-pw list
    frontend-irma       /home/ftpuser/frontend-irma/./
    probe               /home/ftpuser/./

Restart the service
```````````````````

You may want to restart the service:

.. code-block:: bash

    $ sudo invoke-rc.d pure-ftpd restart
