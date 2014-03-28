*************
 IRMA - Brain
*************

========
Overview
========


This package handles the dispatch of the meta scan job to the probes. Deals with accounting and collecting results to send them back to frontend

-----------------------

============
Installation
============

------------
Get the code
------------

Two possibilities:

* if you have a pypi server of your own (1)
* if you don't (2)

**1. pip install into <path>**

.. code-block:: bash

    $ pip install --install-option="--install-purelib=<path>" --install-option="--install-scripts=<scriptpath>" -i http://<pypi-mirror>/pypi irma-admin

**2. clone from github**

.. code-block:: bash

    $ git clone https://github.com/quarkslab/irma-brain.git irma

------------
Installation
------------

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
|   probe        +-------------+------------+-----------+
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
|  backend probe |     port    |``integer`` |   6379    |
|                +-------------+------------+-----------+
|                |      db     |``integer`` |           |
+----------------+-------------+------------+-----------+
|                |     engine  | ``string`` |           |
|   sql brain    +-------------+------------+-----------+
|                |    dbname   | ``string`` |           |
+----------------+-------------+------------+-----------+
|                |     host    | ``string`` |           |
|                +-------------+------------+-----------+
|                |     port    |``integer`` |    21     |
|  ftp brain     +-------------+------------+-----------+
|                |   username  | ``string`` |           |
|                +-------------+------------+-----------+
|                |   password  | ``string`` |           |
+----------------+-------------+------------+-----------+

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/brain.ini``

You could easily generate the user database by running:

.. code-block:: bash

    $ python -m brain.objects

database path is taken from the config file.

=======
Licence
=======

Please see `LICENSE`_.

------------

.. _install.rst: /install/install.rst
.. _LICENSE: /LICENSE

