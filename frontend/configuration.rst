.. _frontend-app-configuration:

Configuration
-------------

The configuration file is located at ``config/frontend.ini`` in the installation
directory.

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

    > Do you want to enable syslog logging? (experimental) (y/N)
    > What is the hostname of your mongodb server? [127.0.0.1]
    > What is the port used by your mongodb server? [27017]
    > What is the sample storage path? [/var/irma/samples/]
    > What is the hostname of your RabbitMQ server? [brain.irma]
    > What is the vhost defined for the brain on your RabbitMQ server? mqbrain
    > What is the username for this vhost on your RabbitMQ server? brain-rmq-password
    > What is the password for this vhost on your RabbitMQ server? brain
    > What is the vhost defined for the frontend on your RabbitMQ server? mqfrontend
    > What is the username for this vhost on your RabbitMQ server? frontend
    > What is the password for this vhost on your RabbitMQ server? frontend-rmq-password
    > What is the hostname of your FTPs server? [brain.irma]
    > What is the username defined for the frontend on your FTP server? frontend
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
     |                |     port    |``integer`` |    27017       | port on which the mongodb server listens                |
     |  mongodb       +-------------+------------+----------------+---------------------------------------------------------+
     |                |    dbname   | ``string`` |    irma        | name of the database for IRMA                           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                | collections |            |                |                                                         |
     |                |  _prefix    | ``string`` |    irma        | prefix for mongodb collections                          |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |    dbms     | ``string`` |    sqlite      | dbapi engine                                            |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   dialect   | ``string`` |                | sqlalchemy dialect                                      |
     |  sqldb         +-------------+------------+----------------+---------------------------------------------------------+
     |                |  username   | ``string`` |                | database username                                       |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |  password   | ``string`` |                | database password                                       |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |    host     | ``string`` |                | database host                                           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   dbname    | ``string`` | /var/irma/db/  |                                                         |
     |                |             |            | frontend.db    | database name                                           |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |tables_prefix| ``string`` |                | database tables prefix                                  |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     | samples_storage|     path    | ``string`` | /var/irma/     |                                                         |
     |                |             |            | samples        | Samples storage path                                    |
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
     |                |     host    | ``string`` |                | hostname for the FTP server                             |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |     port    |``integer`` |    21          | port for the FTP server                                 |
     |  ftp_brain     +-------------+------------+----------------+---------------------------------------------------------+
     |                |   username  | ``string`` |                | username used by this frontend on the FTP server        |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |   password  | ``string`` |                | password used by this frontend on the FTP server        |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_file| ``integer``|     2          | remove file after X days                                |
     |                |_max_age     |            |                |                                                         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_cron| ``integer``|     0          | cron hour settings                                      |
     |                |_hour        |            |                |                                                         |
     |  cron_frontend +-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_cron| ``integer``|     0          | cron minute settings                                    |
     |                |_minute      |            |                |                                                         |
     |                +-------------+------------+----------------+---------------------------------------------------------+
     |                |clean_db_scan| ``integer``|     \*         | cron day of week settings                               |
     |                |_day_of_week |            |                |                                                         |
     +----------------+-------------+------------+----------------+---------------------------------------------------------+
