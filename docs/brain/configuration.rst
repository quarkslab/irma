.. _app-configuration:

Configuration
-------------

The configuration file is located at ``config/brain.ini`` in the installation
directory. 

From the package manager
````````````````````````

The debian package can show dialog boxes to the user and query for required
configuration values. To configure the python application installed with
``apt-get`` command, one can do:

.. code-block:: bash

    $ sudo dpkg-reconfigure irma-brain-app
    [...]

From the sources
````````````````

At the root of the installation directory, the script ``setup.py``
asks you questions to configure the application to your needs. To fit your
setup, you must provide the parameters configured previously on the RabbitMQ
server and the Pure-FTPd server.

For GNU/Linux systems:

.. code-block:: bash

    $ python setup.py configure --application
    running configure
    
    Welcome to IRMA brain application configuration script.
    
    The following script will help you to create a new configuration for
    IRMA frontend application.
    
    Please answer to the following questions so this script can generate the files
    needed by the application. To abort the configuration, press CTRL+D.
    
    > Do you want to enable syslog logging? (experimental) (y/N) 
    > What is the hostname of your RabbitMQ server? [localhost] 
    > What is the vhost defined for the brain on your RabbitMQ server? mqbrain
    > What is the username for this vhost on your RabbitMQ server? brain-rmq
    > What is the password for this vhost on your RabbitMQ server? brain-rmq-password
    > What is the vhost defined for the probes on your RabbitMQ server? mqprobe
    > What is the username for this vhost on your RabbitMQ server? probe-rmq
    > What is the password for this vhost on your RabbitMQ server? probe-rmq-password
    > What is the vhost defined for the frontend on your RabbitMQ server? mqfrontend
    > What is the username for this vhost on your RabbitMQ server? frontend-rmq
    > What is the password for this vhost on your RabbitMQ server? frontend-rmq-password
    > What is the hostname of your Redis server? [localhost] 
    > Which database id is used for brain on your Redis server? [0] 
    > Which database id is used for probes on your Redis server? [1] 
    > What is the hostname of your FTPs server? [localhost] 
    > What is the username defined for the probes on your FTP server? probe-ftp
    > What is the password defined for the probes on your FTP server? probe-ftp-password

When finished, one can note that the ``config/brain.ini`` file has been
modified with values we typed.

.. note:: We recall in the following the meaning of each field in ``config/brain.ini``:

     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |     Section    |      Key    |    Type    |  Default  | Description                                       |
     +================+=============+============+===========+===================================================+
     |                |   syslog    |``integer`` |     0     | enable rsyslog (experimental)                     |
     |   log          +-------------+------------+-----------+---------------------------------------------------+
     |                |   prefix    |``string``  |irma-brain:| prefix to append to rsyslog entries               |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the RabbitMQ server                  |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     port    |``integer`` |   5672    | port for the RabbitMQ server                      |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |  broker_brain  |     vhost   | ``string`` |           | virtual host configured for brain                 |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   username  | ``string`` |           | username used for brain on the RabbitMQ server    |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   password  | ``string`` |           | password used for brain on the RabbitMQ server    |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     queue   | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the Redis server                     |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |  backend_brain |     port    |``integer`` |   6379    | port for the Redis server                         |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |      db     |``integer`` |           | id of the database to use on Redis                |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the RabbitMQ server                  |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     port    |``integer`` |   5672    | port for the RabbitMQ server                      |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |   broker_probe |     vhost   | ``string`` |           | virtual host configured for probes                |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   username  | ``string`` |           | username used for probes on the RabbitMQ server   |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   password  | ``string`` |           | password used for probes on the RabbitMQ server   |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     queue   | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the Redis server                     |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |  backend_probe |     port    |``integer`` |   6379    | port for the Redis server                         |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |      db     |``integer`` |           | id of the database to use on Redis                |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the RabbitMQ server                  |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     port    |``integer`` |   5672    | port for the RabbitMQ server                      |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |broker_frontend |     vhost   | ``string`` |           | virtual host configured for frontend              |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   username  | ``string`` |           | username used for frontend on the RabbitMQ server |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   password  | ``string`` |           | password used for frontend on the RabbitMQ server |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     queue   | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     engine  | ``string`` |sqlite:/// | hostname for the FTP server                       |
     |  sql_brain     +-------------+------------+-----------+---------------------------------------------------+
     |                |     dbname  |``string``  | quota.db  | port for the FTP server                           |
     +----------------+-------------+------------+-----------+---------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the FTP server                       |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |     port    |``integer`` |    21     | port for the FTP server                           |
     |  ftp_brain     +-------------+------------+-----------+---------------------------------------------------+
     |                |   username  | ``string`` |           | username used by probe on the FTP server          |
     |                +-------------+------------+-----------+---------------------------------------------------+
     |                |   password  | ``string`` |           | password used by the probe on the FTP server      |
     +----------------+-------------+------------+-----------+---------------------------------------------------+


Generate a SQLite database for scan tracking
````````````````````````````````````````````

You could easily generate the user database by running the following command.
The path of the database is taken from the configuration file and the folder
where the database is going to be stored must be created beforehand.

.. code-block:: bash

    $ python -m brain.objects 
    usage: brain/objects.py <username> <rmqvhost> <ftpuser> [quota]
          with <username> a string
               <rmqvhost> the rmqvhost used for the frontend
               <ftpuser> the ftpuser used by the frontend
               [quota] the number of file scan quota
    example: brain/objects.py test1 mqfrontend frontend

To create an entry in the database for the frontend named ``frontend-irma`` and
which uses the ``frontend-rmq`` virtual host on the RabbitMQ server, simply run
the following commands:

.. code-block:: bash

    $ python -m brain.objects frontend-irma frontend-rmq frontend-irma 0

The quota sets to ``0`` simply disable the quota system and you will be able to
launch as many analyses as you want.

.. note:: 

    There is a limitation due to SQLite. The folder where the database is
    stored, plus the database file must be writable by the user running the
    worker:

    .. code-block::

        $ sudo chown irma:irma quota.db
        $ sudo chmod a+w /opt/irma/irma-brain
