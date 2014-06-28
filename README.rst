***************
IRMA - Frontend
***************

========
Overview
========

This package handles scan submission to the brain. Keep track of scanned files results and provides the web graphical user interface.


============
Installation
============

Quick install
-------------

Add Quarkslab public GPG key and stable repo. address. See `here`_ for instructions.
Then install Meta package:

.. code-block:: bash

    sudo apt-get update && sudo apt-get install irma-frontend

Do not forget to change parameters according to your settings (See ``Config`` paragraph).

Get the code
------------

clone from github

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-frontend.git irma


Detailed Installation
---------------------

For detailed instructions, please see `install.rst`_.


======
Config
======

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/frontend.ini``. Default ``IRMA_INSTALL_DIR`` is ``/opt/irma/irma-frontend``.

irma-frontend configuration file content:

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
|                |clean_db_scan| ``integer``|    100    |
|                |_info_max_age|            | (in days) |
|                +-------------+------------+-----------+
|                |clean_db_scan| ``integer``|     2     |
|                |_file_max_age|            | (in days) |
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

=======
Licence
=======

Licensed under Apache v2.0 license. Please see `LICENSE`_.

------------

.. _here: http://apt.quarkslab.com/readme.txt
.. _install.rst: /install/install.rst
.. _LICENSE: /LICENSE

