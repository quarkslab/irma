************
IRMA - Brain
************

========
Overview
========

This package handles the dispatch of the meta scan job to the probes. Deals with accounting and collecting results to send them back to frontend


============
Installation
============

Get the code
------------

Two possibilities:

* if you have a pypi server of your own (1)
* if you don't (2)

**1. pip install into <path>**

.. code-block:: bash

    $ pip install --install-option="--install-purelib=<path>" --install-option="--install-scripts=<scriptpath>" -i http://<pypi-mirror>/pypi irma-admin

**2. clone from github**

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-brain.git irma

Quick Installation
------------------

The following script installs IRMA's brain with default values. Do not
forget to change parameter according to your setting. For a more advanced
installation, see detailed installation section.

.. code-block:: bash

    #!/bin/bash

    ###########################################################
    # Parameters
    ###########################################################

    BRAIN_IP_ADDR="brain.irma.qb"

    ###########################################################
    # Install dependencies
    ###########################################################

    sudo apt-get install gdebi

    ###########################################################
    # Download packages
    ###########################################################

    curl -O https://github.com/quarkslab/irma-brain/releases/download/v1.0.2/irma-brain-celery_1.0.2-1_all.deb
    curl -O https://github.com/quarkslab/irma-brain/releases/download/v1.0.2/irma-brain-ftpd_1.0.2-1_all.deb
    curl -O https://github.com/quarkslab/irma-brain/releases/download/v1.0.2/irma-brain-rabbitmq_1.0.2-1_all.deb
    curl -O https://github.com/quarkslab/irma-brain/releases/download/v1.0.2/irma-brain-redis_1.0.2-1_all.deb

    ###########################################################
    # Install packages
    ###########################################################

    sudo gdebi irma-brain-redis_1.0.2-1_all.deb
    sudo gdebi irma-brain-rabbitmq_1.0.2-1_all.deb
    sudo gdebi irma-brain-ftpd_1.0.2-1_all.deb
    sudo gdebi irma-brain-celery_1.0.2-1_all.deb

    ###########################################################
    # Configuration
    ###########################################################

    # Redis configuration
    sudo sed -i "s/^bind 127.0.0.1/# bind 127.0.0.1/g" /etc/redis/redis.conf

    # RMQ configuration (see detailed configuration for explanations)
    sudo /opt/irma/irma-brain/install/rabbitmq/rmq_adduser.sh admin admin mqadmin
    sudo /opt/irma/irma-brain/install/rabbitmq/rmq_adduser.sh brain brain mqbrain
    sudo /opt/irma/irma-brain/install/rabbitmq/rmq_adduser.sh frontend frontend mqfrontend
    sudo /opt/irma/irma-brain/install/rabbitmq/rmq_adduser.sh probe probe mqprobe

    # Pure-FTPd configuration
    sudo groupadd ftpgroup
    sudo useradd -g ftpgroup -d /dev/null -s /etc ftpuser
    sudo sh -c 'echo "yes" > /etc/pure-ftpd/conf/CreateHomeDir'
    sudo sh -c 'echo "no" > /etc/pure-ftpd/conf/PAMAuthentication'
    sudo sh -c 'echo "2" > /etc/pure-ftpd/conf/TLS'
    sudo ln -s /etc/pure-ftpd/conf/PureDB /etc/pure-ftpd/auth/50puredb
    sudo mkdir -p /etc/ssl/private/
    sudo openssl req -x509 -nodes -days 7300 -newkey rsa:2048 -keyout /etc/ssl/private/pure-ftpd.pem -out /etc/ssl/private/pure-ftpd.pem
    sudo chmod 600 /etc/ssl/private/pure-ftpd.pem

    # Create ftp users
    echo -e "frontend\nfrontend\n" | sudo /opt/irma/irma-brain/install/pure-ftpd/ftpd-adduser.sh frontend ftpuser /home/ftpuser/frontend
    echo -e "probe\nprobe\n" | sudo /opt/irma/irma-brain/install/pure-ftpd/ftpd-adduser.sh probe ftpuser /home/ftpuser

    # Configure IRMA
    sudo sed -i "s/^host\s*=.*$/host = $BRAIN_IP_ADDR/" /opt/irma/irma-brain/config/brain.ini
    sudo mkdir /opt/irma/irma-brain/db
    cd /opt/irma/irma-brain/ && sudo python -m brain.objects dummy-user mqfrontend frontend && cd -

    ###########################################################
    # Restart services
    ###########################################################

    sudo /etc/init.d/redis-server restart
    sudo /etc/init.d/rabbitmq-server restart
    sudo /etc/init.d/pure-ftpd restart
    sudo /etc/init.d/celeryd.brain restart
    sudo /etc/init.d/celeryd.results restart



Detailed Installation
---------------------

For detailed instructions, please see `install.rst`_.

======
Config
======

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/brain.ini``. Be sure to create it.

irma-brain configuration file:

+----------------+-------------+------------+-----------+
|     Section    |      Key    |    Type    |  Default  |
+================+=============+============+===========+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |   5672    |
|                +-------------+------------+-----------+
|   broker       |     vhost   | ``string`` |           |
|   brain        +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
|                +-------------+------------+-----------+
|                |     queue   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |   5672    |
|                +-------------+------------+-----------+
|   broker       |     vhost   | ``string`` |           |
|   probe        +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
|                +-------------+------------+-----------+
|                |     queue   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |   5672    |
|                +-------------+------------+-----------+
|   broker       |     vhost   | ``string`` |           |
|   frontend     +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
|                +-------------+------------+-----------+
|                |     queue   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|  backend brain |     port    |``integer`` |   6379    |
|                +-------------+------------+-----------+
|                |      db     |``integer`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|  backend probe |     port    |``integer`` |   6379    |
|                +-------------+------------+-----------+
|                |      db     |``integer`` |           |
+----------------+-------------+------------+-----------+
|                |     engine  | ``string`` |           |
|   sql brain    +-------------+------------+-----------+
|                |    dbname   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |    21     |
|  ftp brain     +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
+----------------+-------------+------------+-----------+

You could easily generate the user database by running:

.. code-block:: bash

    # NOTE: the folder where the database is going to be stored must be created
    # beforehand. By default, create a folder ``db`` at the root of the project.

    $ python -m brain.objects

database path is taken from the config file.

=======
Licence
=======

Please see `LICENSE`_.

------------

.. _install.rst: /install/install.rst
.. _LICENSE: /LICENSE

