Verifying RabbitMQ configuration
================================

We can verify that the RabbitMQ server has taken into account our modifications
with some commands:

Checking for vhosts
*******************

.. code-block:: console

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

.. code-block:: console

    $ sudo rabbitmqctl list_users
    Listing users ...
    probe   []
    brain   []
    frontend        []
    ...done.

If the defined users are not listed by the above command, please execute
once more the script.

Changing password
*****************

If you do not remember the password you just typed, you can change it with
``rabbitmqctl`` command:

.. code-block:: console

    $ sudo rabbitmqctl change_password brain brain-rmq-password
    Changing password for user "brain" ...
    ...done.


Restarting the service
``````````````````````

You may want to restart the service. Thus, the following command can be done:

.. code-block:: console

    $ sudo invoke-rc.d rabbitmq-server restart
