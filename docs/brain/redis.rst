Installing and Configuring Redis
--------------------------------

Celery relies on a Redis server and a RabbitMQ server to work. The following
explains how to install and configure Redis for your setup.

Install Redis
`````````````

Redis server can be installed with this command on Debian:

.. code-block:: bash

    $ sudo apt-get install redis-server

Configuring Redis
`````````````````

Redis serves all components of IRMA platform. Thus, you will have to make it to
listen on all interfaces. For that, edit ``/etc/redis/redis.conf`` and comment
the ``bind`` parameter if necessary. You should have something similar to the
following in your configuration file:

.. code-block:: bash

    $ cat /etc/redis/redis.conf
    [...]
    # If you want you can bind a single interface, if the bind option is not
    # specified all the interfaces will listen for incoming connections.
    #
    # bind 127.0.0.1
    [...]

.. note:: Disclaimer

    Please ensure that only trusted sources can communicate with your redis
    server, by setting up firewall rules for instance, as your redis server may
    be exposed to Internet.

Restarting the service
``````````````````````

As the configuration has been modified, you must restart the service so it can
take into account the modifications:

.. code-block:: bash

    $ sudo invoke-rc.d redis-server restart
