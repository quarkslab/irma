Installing and Configuring RabbitMQ
-----------------------------------

The following explains how to install and to setup RabbitMQ for your setup.

Install RabbitMQ
````````````````

RabbitMQ server can be installed with this command on Debian:

.. code-block:: bash

    $ sudo apt-get install rabbitmq-server

Configuring RabbitMQ
````````````````````

RabbitMQ serves all components of IRMA platform. Each component has their own
virtual host (i.e., message queue where to get data), a username and a
password.

To configure RabbitMQ for IRMA platform, you have to create users, vhosts and
add permissions for each user to corresponding vhost. To easily create virtual
hosts and users, we provide scripts in ``extras/`` directory:

.. code-block:: bash

    $ sh ./extras/scripts/rabbitmq/rmq_adduser.sh
    Usage: sudo rmq_adduser.sh <user> <password> <vhost>

For instance, to create 3 users with the following parameters, one can do:

========= ===================== ============ ===========================================================================================
Username  Password              Virtual Host Command
========= ===================== ============ ===========================================================================================
brain     brain-rmq-password    mqbrain      ``sudo ./extras/scripts/rabbitmq/rmq_adduser.sh brain brain-rmq-password mqbrain``
probe     probe-rmq-password    mqprobe      ``sudo ./extras/scripts/rabbitmq/rmq_adduser.sh probe probe-rmq-password mqprobe``
frontend  frontend-rmq-password mqfrontend   ``sudo ./extras/scripts/rabbitmq/rmq_adduser.sh frontend frontend-rmq-password mqfrontend``
========= ===================== ============ ===========================================================================================

The script simply execute the following three commands:

.. code-block:: bash

    $ sudo rabbitmqctl add_user <username> <password>
    $ sudo rabbitmqctl add_vhost <vhostname>
    $ sudo rabbitmqctl set_permissions -p <vhostname> <username> ".*" ".*" ".*"

.. warning:: Important

    Make sure to note down the username, the password and the virtual host you
    just defined. You will be asked to retype them on each application
    configuration file (brain, frontend and probe)

.. note:: Disclaimer

    Please ensure that only trusted sources can communicate with your RabbitMQ
    server, by setting up firewall rules for instance, as your RabbitMQ may
    be exposed to Internet.

Verifying RabbitMQ configuration
````````````````````````````````

We can verify that the RabbitMQ server has taken into account our modifications
with some commands:

Checking for vhosts
*******************

.. code-block:: bash

    $ sudo rabbitmqctl list_vhosts
    Listing vhosts ...
    mqbrain
    /
    mqfrontend
    mqprobe
    mqadmin
    ...done.

If the defined virtual host are not listed by the above command, please execute
once more the script.

Checking for users
******************

.. code-block:: bash

    $ sudo rabbitmqctl list_users
    Listing users ...
    probe   []
    brain   []
    guest   [administrator]
    frontend        []
    ...done.

If the defined users are not listed by the above command, please execute
once more the script.

Changing password
*****************

If you do not remember the password you just typed, you can change it with
``rabbitmqctl`` command:

.. code-block:: bash

    $ sudo rabbitmqctl change_password brain brain-rmq-password
    Changing password for user "brain" ...
    ...done.


Restarting the service
``````````````````````

You may want to restart the service. Thus, the following command can be done:

.. code-block:: bash

    $ sudo invoke-rc.d rabbitmq-server restart
