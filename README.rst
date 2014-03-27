****************
 IRMA - Frontend
****************

========
Overview
========


This package handles scan submission to the brain. Keep track of scanned files results and provides the web graphical user interface.

-----------------------

============
Installation
============

*clone from github*

.. code-block:: bash

    $ git clone https://github.com/quarkslab/irma-frontend.git irma

*pip install into <path>*

For detailed instructions about setting up a local pypi server please see `brain_install`_.

.. code-block:: bash

    $ pip install --install-option="--install-purelib=<path>" --install-option="--install-scripts=<scriptpath>" -i http://<pypi-mirror>/pypi irma-frontend

For detailed instructions, please see `install.rst`_.

======
Config
======

irma-admin configuration file:

+----------------+-------------+------------+-----------+
|     Section    |      Key    |    Type    |  Default  |
+================+=============+============+===========+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|  mongodb       |     port    |``integer`` |   27017   |
|                +-------------+------------+-----------+
|                |    dbname   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |  scan_info  | ``string`` |           |
|                +-------------+------------+-----------+
|                | scan_results| ``string`` |           |
| collections    +-------------+------------+-----------+
|                |  scan_files | ``string`` |           |
|                +-------------+------------+-----------+
|                | scan_file_fs| ``string`` |           |
+----------------+-------------+------------+-----------+
|celery_brain    |    timeout  | ``integer``|   10(sec) |
+----------------+-------------+------------+-----------+
|celery_frontend |    timeout  | ``integer``|   10(sec) |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |   5672    |
|                +-------------+------------+-----------+
|   broker       |     vhost   | ``string`` |           |
|   brain        +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
|                +-------------+------------+-----------+
|                |     queue   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |   5672    |
|                +-------------+------------+-----------+
|   broker       |     vhost   | ``string`` |           |
|   frontend     +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
|                +-------------+------------+-----------+
|                |     queue   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|  backend brain |     port    |``integer`` |   6379    |
|                +-------------+------------+-----------+
|                |      db     |``integer`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |    21     |
|  ftp brain     +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |clean_db_scan| ``integer``|  2592000  |
|                |_info_max_age|            | (30 days) |
|                +-------------+------------+-----------+
|                |clean_db_scan| ``integer``|   172800  |
|                |_file_max_age|            |  (2 days) |
|                +-------------+------------+-----------+
| cron_frontend  |clean_db_cron| ``integer``|     0     |
|                |_hour        |            |           |
|                +-------------+------------+-----------+
|                |clean_db_cron| ``integer``|     0     |
|                |_minute      |            |           |
|                +-------------+------------+-----------+
|                |clean_db_scan| ``integer``|     \*    |
|                |_day_of_week |            |           |
+----------------+-------------+------------+-----------+

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/frontend.ini``

=======
Licence
=======

Please see `LICENSE`_.

------------

.. _install.rst: /install/install.rst
.. _brain_install: /../../../irma-brain/blob/master/install/install.rst
.. _LICENSE: /LICENSE

