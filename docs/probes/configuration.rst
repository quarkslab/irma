.. _app-configuration:

Configuration
-------------

The configuration file is ``config/probe.ini`` located in the installation
directory.

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
     |                |     host    | ``string`` |           | hostname for the FTP server                     |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |     port    |``integer`` |    21     | port for the FTP server                         |
     |  ftp brain     +-------------+------------+-----------+-------------------------------------------------+
     |                |   username  | ``string`` |           | username used by probe on the FTP server        |
     |                +-------------+------------+-----------+-------------------------------------------------+
     |                |   password  | ``string`` |           | password used by the probe on the FTP server    |
     +----------------+-------------+------------+-----------+-------------------------------------------------+
