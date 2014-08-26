.. _app-configuration:

Configuration
-------------

The configuration file is located at ``config/frontend.ini`` in the installation
directory. 

From the package manager
````````````````````````

The Debian package can show dialog boxes to the user and query for required
configuration values. To configure the python application installed with
``apt-get`` command, one can do:

.. code-block:: bash

    $ sudo dpkg-reconfigure irma-frontend-app
    [...]

From the sources
````````````````

At the root of the installation directory, the script ``setup.py``
asks you questions to configure the application for your needs. To fit your
setup, you must provide the parameters configured on the **Brain**.

For GNU/Linux systems:

.. code-block:: none

    $ python setup.py configure --application
    running configure
    
    Welcome to IRMA frontend application configuration script.
    
    The following script will help you to create a new configuration for
    IRMA frontend application.
    
    Please answer to the following questions so this script can generate the files
    needed by the application. To abort the configuration, press CTRL+D.
            
    > Do you want to enable syslog logging? (experimental) (y/N) N
    > What is the hostname of your mongodb server? [127.0.0.1] 
    > What is the port used by your mongodb server? [27017] 
    > What is the hostname of your RabbitMQ server? [brain.irma] brain.irma.qb
    > What is the vhost defined for the brain on your RabbitMQ server? mqbrain
    > What is the username for this vhost on your RabbitMQ server? brain-rmq
    > What is the password for this vhost on your RabbitMQ server? brain-rmq-password
    > What is the vhost defined for the frontend on your RabbitMQ server? mqfrontend
    > What is the username for this vhost on your RabbitMQ server? frontend-rmq
    > What is the password for this vhost on your RabbitMQ server? frontend-rmq-password
    > What is the hostname of your Redis server? [brain.irma] brain.irma.qb
    > Which database id is used for brain on your Redis server? [0]
    > What is the hostname of your FTPs server? [brain.irma] brain.irma.qb
    > What is the username defined for the frontend on your FTP server? frontend-ftp
    > What is the password defined for the frontend on your FTP server? frontend-ftp-password
    
    When finished, one can note that the ``config/frontend.ini`` file has been
    modified with values we typed.
    
.. note:: We recall in the following the meaning of each field in ``config/frontend.ini``:

     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |     Section    |      Key    |    Type    |  Default       | Description                                             |
     +================+=============+============+================+=========================================================+
     |                | syslog      | ``integer``| 0              | enable rsyslog (experimental)                           |
     |  log           +-------------+------------+----------------+---------------------------------------------------------+
     |                | prefix      | ``string`` | irma-frontend: | prefix to append to rsyslog entries                     |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |     host    | ``string`` |                | hostname of the mongodb server                          |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |  mongodb       |     port    |``integer`` |   27017        | port on which the mongodb server listens                |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |    dbname   | ``string`` | irma           | name of the database for IRMA                           |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |  scan_info  | ``string`` |                | name of the collection to store scan info               |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                | scan_results| ``string`` |                | name of the collection to store scan results            |
     | collections    +-------------+------------+----------------+---------------------------------------------------------+
     |                |  scan_files | ``string`` |                | name of the collection to store file metadata           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                | scan_file_fs| ``string`` |                | name of the collection used by gridfs to store files    |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |celery_brain    |    timeout  | ``integer``|  10 (sec)      | time before considering that the brain has timed-out    |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |celery_frontend |    timeout  | ``integer``|  10 (sec)      | time before considering that the frontend has timed-out |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |     host    | ``string`` |                |  hostname for the RabbitMQ server                       |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |     port    |``integer`` |   5672         |  port for the RabbitMQ server                           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |broker_brain    |     vhost   | ``string`` |                |  virtual host configured for brain                      |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   username  | ``string`` |                |  username used for brain on the RabbitMQ server         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   password  | ``string`` |                |  password used for brain on the RabbitMQ server         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |     queue   | ``string`` |                |  queue to poll new tasks on the RabbitMQ server         |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |     host    | ``string`` |                |  hostname for the RabbitMQ server                       |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |     port    |``integer`` |   5672         |  port for the RabbitMQ server                           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |broker_frontend |     vhost   | ``string`` |                |  virtual host configured for this frontend              |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   username  | ``string`` |                |  username used for this frontend on the RabbitMQ server |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   password  | ``string`` |                |  password used for this frontend on the RabbitMQ server |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |     queue   | ``string`` |                |  queue to poll new tasks on the RabbitMQ server         |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |     host    | ``string`` |                | hostname for the Redis server                           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |  backend_brain |     port    |``integer`` |   6379         | port for the Redis server                               |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |      db     |``integer`` |                | id of the database to use on Redis                      |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |     host    | ``string`` |                | hostname for the FTP server                             |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |     port    |``integer`` |    21          | port for the FTP server                                 |
     |  ftp_brain     +-------------+------------+----------------+---------------------------------------------------------+
     |                |   username  | ``string`` |                | username used by this frontend on the FTP server        |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   password  | ``string`` |                | password used by this frontend on the FTP server        |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_scan| ``integer``|    100         |                                                         |
     |                |_info_max_age|            | (in days)      |                                                         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_scan| ``integer``|     2          |                                                         |
     |                |_file_max_age|            | (in days)      |                                                         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     | cron_frontend  |clean_db_cron| ``integer``|     0          |                                                         |
     |                |_hour        |            |                |                                                         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_cron| ``integer``|     0          |                                                         |
     |                |_minute      |            |                |                                                         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_scan| ``integer``|     \*         |                                                         |
     |                |_day_of_week |            |                |                                                         |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
