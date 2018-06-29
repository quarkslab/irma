Probe configuration
===================
.. _app-configuration:

Configuration
-------------

The configuration file is ``config/probe.ini`` located in the installation
directory.

.. note:: We recall in the following the meaning of each field in ``config/probe.ini``:

     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |     Section    |        Key      |    Type    |  Default  | Description                                       |
     +================+=================+============+===========+===================================================+
     |                |      syslog     |``integer`` |     0     | enable rsyslog (experimental)                     |
     |   log          +-----------------+------------+-----------+---------------------------------------------------+
     |                |      prefix     |``string``  |irma-probe:| prefix to append to rsyslog entries               |
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
     |   broker       |      vhost      | ``string`` |           | virtual host configured for probes                |
     |   probe        +-----------------+------------+-----------+---------------------------------------------------+
     |                |     username    | ``string`` |           | username used for probes on the RabbitMQ server   |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     password    | ``string`` |           | password used for probes on the RabbitMQ server   |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       queue     | ``string`` |           | queue to poll new tasks on the RabbitMQ server    |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
     |                |       host      | ``string`` |           | hostname for the FTP server                       |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       port      |``integer`` |    21     | port for the FTP server                           |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |       auth      | ``string`` | "password"| SFTP authentication method ("password" or "key")  |
     |   ftp_brain    +-----------------+------------+----------------+----------------------------------------------+
     |                |     key_path    | ``string`` |           | sftp private key absolute path                    |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     username    | ``string`` |           | username used by probe on the FTP server          |
     |                +-----------------+------------+-----------+---------------------------------------------------+
     |                |     password    | ``string`` |           | password used by the probe on the FTP server      |
     +----------------+-----------------+------------+-----------+---------------------------------------------------+
