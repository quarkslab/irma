SSL settings
------------

Making RabbitMQ running SSL
+++++++++++++++++++++++++++

Certificates generation
^^^^^^^^^^^^^^^^^^^^^^^

See rabbitmq detailed guide on how to generate server and clients certificates `here <https://www.rabbitmq.com/ssl.html>`_


Update server settings on brain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 Copy the RabbitMQ configuration template provided in "./extras/rabbitmq" to "/etc/rabbitmq"

 Restart RabbitMQ:

.. code-block:: console

    $ sudo service rabbitmq-server restart


Allow IRMA to use SSL with RabbitMQ
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Frontend configuration file is ``<irma dir>/config/frontend.ini``

    Brain configuration file is ``<irma dir>/config/brain.ini``

    Probe configuration file is ``<irma dir>/config/probe.ini``


Update PORT in configuration file from 5672 to 5671. Except if you change the default port defined in the the RabbitMQ configuration template provided in the precedent paragraph.

.. code-block:: ini
   :emphasize-lines: 3

    [broker_xxxx]
    host = 127.0.0.1
    port = 5671


Update activate_ssl switch in configuration file:

.. code-block:: ini
   :emphasize-lines: 2

    [ssl_config]
    activate_ssl = yes
    ca_certs =
    keyfile =
    certfile =

Put the SSL certificates (``ca_cert``, ``key_file``, ``cert_file``) in ``<irma dir>/ssl``
Update ca_certs, keyfile and certfile in configuration file according to the filenames in "./ssl"

.. code-block:: ini
   :emphasize-lines: 3-5

    [ssl_config]
    activate_ssl = yes
    ca_certs = <ca_cert_filename>
    keyfile = <key_filename>
    certfile = <cert_filename>



.. note::

    If you are switching to ssl from an already running no_ssl version,
    please do the following on irma-brain RabbitMQ server:

    .. code-block:: console

        $ sudo rabbitmqctl stop_app
        $ sudo rabbitmqctl reset
        $ sudo rabbitmqctl start_app
        # create again the RabbitMQ vhosts, usernames and passwords:
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh probe probe mqprobe
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh brain brain mqbrain
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh frontend frontend mqfrontend
