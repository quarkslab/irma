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

Add Quarkslab public GPG key

.. code-block:: bash

    $ wget -O - http://www.quarkslab.com/qb-apt-key.asc | sudo apt-key add  -


Add Quarkslab's repository source


.. code-block:: bash

    echo 'deb http://apt.quarkslab.com/pub/debian stable main' | sudo tee /etc/apt/sources.list.d/quarkslab.list


Install Meta package

.. code-block:: bash

    sudo apt-get update && sudo apt-get install irma-frontend

Do not forget to change parameter according to your setting (See ``Config`` paragraph).

Get the code
------------

Two possibilities:

* if you have a pypi server of your own (1)
* if you don't (2)

**1. pip install into <path>**

For detailed instructions about setting up a local pypi server please see `brain_install`_.

.. code-block:: bash

    $ pip install --install-option="--install-purelib=<path>" --install-option="--install-scripts=<scriptpath>" -i http://<pypi-mirror>/pypi irma-frontend


**2. clone from github**

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-frontend.git irma


Detailed Installation
---------------------

For detailed instructions, please see `install.rst`_.


======
Config
======

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/frontend.ini``. Be sure to create it.

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

Please see `LICENSE`_.

------------

.. _install.rst: /install/install.rst
.. _brain_install: /../../../irma-brain/blob/master/install/install.rst
.. _LICENSE: /LICENSE

