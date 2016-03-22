SSL settings
------------

Making RabbitMQ running SSL
+++++++++++++++++++++++++++

Update server settings on brain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 Copy the RabbitMQ configuration template provided in "./extras/rabbitmq" to "/etc/rabbitmq"

 Restart RabbitMQ:

.. code-block:: bash

    $ sudo service rabbitmq-server restart


Allow irma to use SSL with RabbitMQ
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update PORT in brain.ini from 5672 to 5671. Except if you change the default port defined in the the RabbitMQ configuration template provided in the precedent paragraph.

Update activate_ssl switch in brain.ini:

.. code-block:: bash
   :emphasize-lines: 2

    [ssl_config]
    activate_ssl = yes
    ca_certs =
    keyfile =
    certfile =

Put the SSL certificates (``ca_cert``, ``key_file``, ``cert_file``) in ``<irma dir>/ssl``
Update ca_certs, keyfile and certfile in configuration file (config/{frontend,brain,probe}.ini)
according to the filenames in "./ssl"

.. code-block:: bash
   :emphasize-lines: 3-5

    [ssl_config]
    activate_ssl = yes
    ca_certs = <path to ca_cert>
    keyfile = <path to key_file>
    certfile = <path to cert_file>



.. note::

    If you are switching to ssl from an already running no_ssl version,
    please do the following on irma-brain RabbitMQ server:

    .. code-block:: bash

        $ sudo rabbitmqctl stop_app
        $ sudo rabbitmqctl reset
        $ sudo rabbitmqctl start_app
        # create again the RabbitMQ vhosts, usernames and passwords:
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh probe probe mqprobe
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh brain brain mqbrain
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh frontend frontend mqfrontend
