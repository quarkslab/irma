Brain configuration
===================

.. _brain-app-configuration:

Configuration
-------------

The configuration file is located at ``config/brain.ini`` in the installation
directory. Update it with your specific info.

.. note:: Detailed meaning of each field in ``config/brain.ini``:

     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |     Section    |        Key      |    Type    |  Default  | Description                                       |
     +================+=================+============+===========+===================================================+
     |                |     syslog      |``integer`` |     0     | enable rsyslog (experimental)                     |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     prefix      |``string``  |irma-brain:| prefix to append to rsyslog entries               |
     |   log          +-----------------+------------+-----------+---------------------------------------------------+
     |                |      debug      | ``boolean``|   False   | enable Debug log                                  |
     |                +-----------------+------------+----------------+----------------------------------------------+
     |                |    sql_debug    | ``boolean``|   False   | enable SQL debug log                              |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |   concurrency   |  `integer` |     0     | number of concurrent workers (0 means nb of cores)|
     |                +-----------------+------------+-----------+---------------------------------------------------+
     | celery_options | soft_time_limit | ``integer``|  300 (sec)| time limit before task soft interrupt             |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |    time_limit   | ``integer``| 1500 (sec)| time limit before task is killed                  |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |       host      | ``string`` |           | hostname for the RabbitMQ server                  |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       port      |``integer`` |   5672    | port for the RabbitMQ server                      |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |  broker_brain  |       vhost     | ``string`` |           | virtual host configured for brain                 |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     username    | ``string`` |           | username used for brain on the RabbitMQ server    |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     password    | ``string`` |           | password used for brain on the RabbitMQ server    |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       queue     | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |       host      | ``string`` |           | hostname for the RabbitMQ server                  |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       port      |``integer`` |   5672    | port for the RabbitMQ server                      |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |   broker_probe |       vhost     | ``string`` |           | virtual host configured for probes                |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     username    | ``string`` |           | username used for probes on the RabbitMQ server   |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     password    | ``string`` |           | password used for probes on the RabbitMQ server   |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       queue     | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |       host      | ``string`` |           | hostname for the RabbitMQ server                  |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       port      |``integer`` |   5672    | port for the RabbitMQ server                      |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |broker_frontend |       vhost     | ``string`` |           | virtual host configured for frontend              |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     username    | ``string`` |           | username used for frontend on the RabbitMQ server |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     password    | ``string`` |           | password used for frontend on the RabbitMQ server |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       queue     | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |      dbms       | ``string`` |  sqlite   | dbapi engine                                      |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     dialect     | ``string`` |           | sqlalchemy dialect                                |
     |  sqldb         +-----------------+------------+-----------+---------------------------------------------------+
     |                |    username     | ``string`` |           | database username                                 |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |    password     | ``string`` |           | database password                                 |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |      host       | ``string`` |           | database host                                     |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     dbname      | ``string`` |/var/irma/ |                                                   |
     |                |                 |            |db/brain.db| database name                                     |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |  tables_prefix  | ``string`` |           | database tables prefix                            |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |      ftp       |     protocol    | ``string`` |   "sftp"  | choose File Transfer Protocol ("sftp" or "ftps")  |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |       host      | ``string`` |           | hostname for the FTP server                       |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       port      |``integer`` |    21     | port for the FTP server                           |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       auth      | ``string`` | "password"| SFTP authentication method ("password" or "key")  |
     |   ftp_brain    +-----------------+------------+----------------+----------------------------------------------+
     |                |     key_path    | ``string`` |           | sftp private key absolute path                    |
     |                +-----------------+------------+----------------+----------------------------------------------+
     |                |     username    | ``string`` |           | username used by probe on the FTP server          |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     password    | ``string`` |           | password used by the probe on the FTP server      |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     | interprocess   |     path        | ``string`` |/var/run/  | Concurrency file lock                             |
     | _lock          |                 |            |lock/irma- |                                                   |
     |                |                 |            |brain.lock |                                                   |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |  activate_ssl   | ``boolean``|    False  | Enable RabbitMQ ssl                               |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |  ca_certs       | ``string`` |           | RabbitMQ SSL certs                                |
     |  ssl_config    +-----------------+------------+-----------+---------------------------------------------------+
     |                |  keyfile        | ``string`` |           | RabbitMQ SSL keyfile                              |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |  certfile       | ``string`` |           | RabbitMQ SSL certfile                             |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+


Generate a SQLite database for scan tracking
````````````````````````````````````````````

You could easily generate the user database by running the following command.
The path of the database is taken from the configuration file and the folder
where the database is going to be stored must be created beforehand.

.. note::

    The default path for the database is /var/irma/db/ make sure it exists before creating user database.

.. code-block:: console

    $ cd /opt/irma/irma-brain/current/
    $ ./venv/bin/python -m scripts.create_user
    usage: create_user <username> <rmqvhost> <ftpuser>
          with <username> a string
               <rmqvhost> the rmqvhost used for the frontend
               <ftpuser> the ftpuser used by the frontend
    example: create_user test1 mqfrontend frontend

To create an entry in the database for the frontend named ``frontend`` and
which uses the ``mqfrontend`` virtual host on the RabbitMQ server, simply run
the following commands:

.. code-block:: console

    $ ./venv/bin/python -m scripts.create_user frontend mqfrontend frontend


.. note::

    There is a limitation due to SQLite. The folder where the database is
    stored, plus the database file must be writable by the user running the
    worker:

    .. code-block:: console

        $ sudo chown irma:irma /var/irma/db/brain.db
        $ sudo chmod a+w /opt/irma/irma-brain
