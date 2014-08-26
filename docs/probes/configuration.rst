.. _app-configuration:

Configuration
-------------

The configuration file is ``config/probe.ini`` located in the installation
directory. 

From the package manager
````````````````````````

The debian package can show dialog boxes to the user and query for require
configuration values. To configure the python application installed with
``apt-get`` command, one can do:

.. code-block:: bash

    $ sudo dpkg-reconfigure irma-probe-app
    [...]

From the sources
````````````````

At the root of the installation directory, the script ``setup.py``
asks you questions to configure the application to your needs. To fit your
setup, you must provide the parameters configured on the **Brain**.

For Microsoft Windows systems:

.. code-block:: none

    $ C:\Python27\python.exe setup.py configure --application
    running configure
     
    Welcome to IRMA probe application configuration script.
     
    The following script will help you to create a new configuration for
    IRMA probe application.
     
    Please answer to the following questions so this script can generate the files
    needed by the application. To abort the configuration, press CTRL+D.

    > Do you want to enable syslog logging? (experimental) (y/N) N
    > Which name would you like to give to your probe? [irma-probe]           
    > What is the hostname of your RabbitMQ server? [brain.irma] brain.irma.qb
    > What is the vhost defined for probes on your RabbitMQ server? mqbrain
    > What is the username for this vhost on your RabbitMQ server? brain-rmq
    > What is the password for this vhost on your RabbitMQ server? brain-rmq-password
    > What is the hostname of your Redis server? [brain.irma] brain.irma.qb
    > Which database id is used for probes on your Redis server? [1] 
    > What is the hostname of your FTPs server? [brain.irma] brain.irma.qb
    > What is the username defined for probes on your FTP server? probe-ftp
    > What is the password defined for probes on your FTP server? probe-ftp-password


For GNU/Linux systems:

.. code-block:: bash

    $ python setup.py configure --application
    [...]

When finished, one can note that the ``config/probe.ini`` file has been
modified with values we typed.

.. note:: We recall in the following the meaning of each field in ``config/probe.ini``:

     +----------------+-------------+------------+-----------+-------------------------------------------------+
     |     Section    |      Key    |    Type    |  Default  | Description                                     |
     +================+=============+============+===========+=================================================+
     |                |   syslog    |``integer`` |     0     | enable rsyslog (experimental)                   |
     |   log          +-------------+------------+-----------+-------------------------------------------------+
     |                |   prefix    |``string``  |irma-probe:| prefix to append to rsyslog entries             |
     +----------------+-------------+------------+-----------+-------------------------------------------------+
     |   probe        |   name      |``string``  |           | name to give to the probe                       |
     +----------------+-------------+------------+-----------+-------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the RabbitMQ server                |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |     port    |``integer`` |   5672    | port for the RabbitMQ server                    |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |   broker       |     vhost   | ``string`` |           | virtual host configured for probes              |
     |   probe        +-------------+------------+-----------+-------------------------------------------------+
     |                |   username  | ``string`` |           | username used for probes on the RabbitMQ server |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |   password  | ``string`` |           | password used for probes on the RabbitMQ server |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |     queue   | ``string`` |           | queue to poll new tasks on the RabbitMQ server  |
     +----------------+-------------+------------+-----------+-------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the Redis server                   |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |  backend probe |     port    |``integer`` |   6379    | port for the Redis server                       |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |      db     |``integer`` |     1     | id of the database to use on Redis              |
     +----------------+-------------+------------+-----------+-------------------------------------------------+
     |                |     host    | ``string`` |           | hostname for the FTP server                     |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |     port    |``integer`` |    21     | port for the FTP server                         |
     |  ftp brain     +-------------+------------+-----------+-------------------------------------------------+
     |                |   username  | ``string`` |           | username used by probe on the FTP server        |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |   password  | ``string`` |           | password used by the probe on the FTP server    |
     +----------------+-------------+------------+-----------+-------------------------------------------------+
