Installing and configuring sftp
===============================

A SFTP server is used to transfer files
**Frontends** and meant to be analyzed by **Probes**. We describe in the
following how to set it up.

Installing sshd
````````````````````

sshd should already been installed but if not install it with:

.. code-block:: bash

    $ sudo apt-get install openssh-sftp-server

Creating FTP specific users and groups
``````````````````````````````````````

.. code-block:: bash

    $ sudo groupadd sftpusers
    $ sudo useradd -g sftpusers -M -s /etc <frontend username>
    $ sudo useradd -g sftpusers -Match -s /etc <probe username>
    $ sudo passwd frontend
        <enter frontend password>
    $ sudo passwd probe
        <enter probe password>

Configure sshd
``````````````

Edit ``/etc/sshd_config``

.. code-block:: bash

    Subsystem sftp internal-sftp
    Match User <frontend username>
      AllowTcpForwarding no
      ChrootDirectory /sftp/<frontend username>
      ForceCommand internal-sftp -u 2
      PermitTunnel no
      X11Forwarding no
    Match User <probe username>
      AllowTcpForwarding no
      ChrootDirectory /sftp
      ForceCommand internal-sftp -u 2
      PermitTunnel no
      X11Forwarding no


Create SFTP directories
```````````````````````

The frontends need an account with ``/sftp/<frontend-name>/uploads`` as home
directory and a single account is shared between probes ( ``uploads`` directory is needed
as in chrooted environment home is not writeable). The later needs to
access to all frontends, thus the associated home directory is simply
``/sftp/``. For instance, a frontend named ``frontend``, execute
the following to create the directories:

.. code-block:: bash

    $ sudo mkdir -pv /sftp/frontend/uploads
    mkdir: created directory `/sftp'
    mkdir: created directory `/sftp/frontend'
    mkdir: created directory `/sftp/frontend/uploads'
    $ sudo chown -R root:sftpusers /sftp
    $ sudo chmod  0750 /sftp
    $ sudo chmod  0750 /sftp/frontend
    $ sudo chown -R frontend:sftpusers /sftp/frontend/uploads
    $ sudo chmod -R 0775 /sftp/frontend/uploads


Restart the service
```````````````````

You may want to restart the service:

.. code-block:: bash

    $ sudo invoke-rc.d sshd restart
