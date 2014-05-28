********************************
 IRMA Brain - Installation guide
********************************

**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none

------------
Requirements
------------

packages:

* python2.7
* python-pip
* rabbitmq-server
* redis-server
* pure-ftpd 

python-pip packages (see ``install/requirements.txt`` for versions):

* celery
* redis
* sqlalchemy

-------------
Configuration
-------------

**redis**

edit ``/etc/redis/redis.conf`` to listen on all interfaces by commenting ``bind`` parameter.

.. code-block::

   # If you want you can bind a single interface, if the bind option is not
   # specified all the interfaces will listen for incoming connections.
   #
   #bind 127.0.0.1

**rabbitmq**

create users, vhosts and add permissions for each user to corresponding vhost.

*default configuration to set*

   ===========  ===========
    username       vhost 
   ===========  ===========
      admin       mqadmin
      brain       mqbrain
     frontend    mqfrontend
      probe       mqprobe
   ===========  ===========

passwords must be syncd with configuration files for admin, frontend, brain and probe modules.

Users creation could be done through the provided script ``IRMA_INSTALL_DIR\install\rabbitmq\rmq_adduser.sh``

.. code-block:: bash

   $ sudo rmq_adduser.sh <user> <password> <vhost>
 
or manually by entering:

.. code-block:: bash

   $ sudo rabbitmqctl add_user <username> <password>
   $ sudo rabbitmqctl add_vhost <vhostname>
   $ sudo rabbitmqctl set_permissions -p <vhostname> <username> ".*" ".*" ".*"
   
**celery**

edit both:
 * ``install/celery/celeryd.brain.defaults``
 * ``install/celery/celeryd.results.defaults``  
according to your install

.. code-block::
    
    # Where to chdir at start.
    CELERYD_CHDIR="/home/irma/irma/"
   
copy both ``.defaults`` config file to ``/etc/default/celeryd``

.. code-block::
    
    $ sudo celeryd.brain.defaults /etc/default/celeryd/celeryd.brain
    $ sudo celeryd.results.defaults /etc/default/celeryd/results.brain

copy ``celeryd.brain`` init script file to ``/etc/init.d/celeryd.brain``
copy ``celeryd.results`` init script file to ``/etc/init.d/celeryd.results``

.. code-block::
    
    $ sudo celeryd.brain /etc/init.d/celeryd.brain
    $ sudo celeryd.results /etc/init.d/results.brain

launch celery

.. code-block:: bash

    $ sudo chmod +x /etc/init.d/celeryd.brain
    $ sudo service celeryd.brain start

    $ sudo chmod +x /etc/init.d/celeryd.results
    $ sudo service celeryd.results start

.. WARNING:: 

    By default ``celery`` users and groups (configured in ``.defaults``) are not created.
    Celery fails if the configured users and groups are not defined. Additionnally, you
    must change permission for the ``/var/run/celery`` directory in order to allow celery 
    to create a lock file.
    
Make all services start at boot:

.. code-block:: bash

    $ sudo /usr/sbin/update-rc.d celeryd.brain defaults
    $ sudo /usr/sbin/update-rc.d celeryd.results defaults
    
Consult the logs at ``/var/log/celery/*.log`` to check the installation.

.. code-block:: bash

    $ cat /var/log/celery/*.log
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] brain@irma-brain ready.
    [...]
    [2014-04-30 13:35:04,205: WARNING/MainProcess] results@irma-brain ready.

**pure-ftpd**

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
   $ sudo ftpd-adduser.sh frontend ftpuser /home/ftpuser/frontend
   $ sudo ftpd-adduser.sh probe ftpuser /home/ftpuser/

launch pure-ftpd

.. code-block:: bash

    $ sudo service pure-ftpd restart

--------------------

==============================
Install a local pip pkg server
==============================

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

**Install a python package with pip**

.. code-block:: bash
  
   $ pip install <package-name>

--------------------

**Update a python package with pip**

.. code-block:: bash

   $ pip install --upgrade <package-name>

--------------------

**Install a specific version of a python package with pip**

.. code-block:: bash

   $ pip install <package-name>==<version>

--------------------

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

Feeling lost ? need support ? irc: #irma-qb@chat.freenode.net 

----------------------

.. _simplepypi: https://github.com/steiza/simplepypi

   
