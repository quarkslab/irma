********************************
 IRMA Brain - Installation guide
********************************

**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none

-----
Redis
-----

edit ``/etc/redis/redis.conf`` to listen on all interfaces by commenting ``bind`` parameter.

.. code-block::

   # If you want you can bind a single interface, if the bind option is not
   # specified all the interfaces will listen for incoming connections.
   #
   #bind 127.0.0.1

--------
Rabbitmq
--------

create users, vhosts and add permissions for each user to corresponding vhost.

*default configuration to set*

   ===========  ===========
    username       vhost 
   ===========  ===========
      brain       mqbrain
     frontend    mqfrontend
      probe       mqprobe
   ===========  ===========

passwords must be syncd with configuration files for frontend, brain and probe modules. (config/<module_name>.ini)

Users creation could be done through the provided script ``IRMA_INSTALL_DIR\install\rabbitmq\rmq_adduser.sh``

.. code-block:: bash

   $ sudo rmq_adduser.sh <user> <password> <vhost>
 
or manually by entering:

.. code-block:: bash

   $ sudo rabbitmqctl add_user <username> <password>
   $ sudo rabbitmqctl add_vhost <vhostname>
   $ sudo rabbitmqctl set_permissions -p <vhostname> <username> ".*" ".*" ".*"

---------
Pure-ftpd
---------

add ftpuser

.. code-block:: bash

    $ groupadd ftpgroup
    $ useradd -g ftpgroup -d /dev/null -s /etc ftpuser

config pure-ftpd

.. code-block:: bash

    $ echo "yes" > /etc/pure-ftpd/conf/CreateHomeDir
    $ echo "no" > /etc/pure-ftpd/conf/PAMAuthentication
    $ echo "2" > /etc/pure-ftpd/conf/TLS
    $ ln -s /etc/pure-ftpd/conf/PureDB /etc/pure-ftpd/auth/50puredb

generate certs

.. code-block:: bash

    $ mkdir -p /etc/ssl/private/
    $ openssl req -x509 -nodes -days 7300 -newkey rsa:2048 -keyout /etc/ssl/private/pure-ftpd.pem -out /etc/ssl/private/pure-ftpd.pem
    $ chmod 600 /etc/ssl/private/pure-ftpd.pem

virtual user creation could be done through the provided script ``IRMA_INSTALL_DIR\install\pure-ftpd\ftpd-adduser.sh``

.. code-block:: bash

   $ sudo ftpd-adduser.sh <user> <virtualuser> <chroot home>
   
The frontends need an account with ``/home/ftpuser/<frontend-name>`` as home directory and
a shared account is shared between probes. The later needs to access to all frontends, thus 
the associated home directory ``/home/ftpuser/``.

   e.g (for multiple frontends, change user and chroot home accordingly)

.. code-block:: bash

   $ sudo ftpd-adduser.sh frontend ftpuser /home/ftpuser/frontend
   $ sudo ftpd-adduser.sh probe ftpuser /home/ftpuser/

Test your config. Listing your users should output something like this:

.. code-block:: bash

    $ sudo pure-pw list
    frontend            /home/ftpuser/frontend/./
    probe               /home/ftpuser/./

launch pure-ftpd

.. code-block:: bash

    $ sudo service pure-ftpd restart

--------------------

You could easily generate the user database by running:

.. code-block:: bash

    # NOTE: the folder where the database is going to be stored must be created
    # beforehand. By default, create a folder ``db`` at the root of the project.

    $ python -m brain.objects

database path is taken from the config file.

========================================
Optional: Install a local pip pkg server
========================================

This is an optional way of distributing irma package on local machines.
There's a lot of custom pypi server, we used simplepipy.


.. code-block:: bash
    $ git clone https://github.com/steiza/simplepypi simplepypi
    $ cd simplepypi
    $ sudo python setup.py install

launch server (default configuration localhost:8000)

.. code-block:: bash
    $ sudo simplepypi

===
FAQ
===

**install all requirements with pip**

.. code-block:: bash

   $ pip install -r requirements.txt


--------------------

**Install a custom python package with custom install path (e.g. irma packages install)**

.. code-block:: bash

   $ pip install --install-option='--install-purelib=<custom path>' --install-option='--install-scripts=<scripts path>' -i http://<custom pkg server>/pypi <package-name>


--------------------

**Start a service at boot**

.. code-block:: bash

    $ sudo /usr/sbin/update-rc.d <service-name> defaults

--------------------


=======
Support
=======

Feeling lost ? need support ? irc: #qb_irma@chat.freenode.net

----------------------

.. _simplepypi: https://github.com/steiza/simplepypi

   
