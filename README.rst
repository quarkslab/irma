************
IRMA - Brain
************

========
Overview
========

This package handles the dispatch of the meta scan job to the probes. Deals with accounting and collecting results to send them back to frontend.


============
Installation
============


Quick install
-------------

Add Quarkslab stable repository address. See `here`_ for instructions.
Then install Meta package:

.. code-block:: bash

    sudo apt-get update && sudo apt-get install irma-brain

Do not forget to change parameters according to your settings (See ``Config`` paragraph).

Get the code
------------

clone from github

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-brain.git irma-brain

For post-install instructions see `install.rst`_ for:

     * ftps accounts
     * rabbitmq accounts
     * redis config
     * sqlite user db creation

======
Config
======

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/brain.ini``. Default ``IRMA_INSTALL_DIR`` is ``/opt/irma/irma-brain``.

irma-brain configuration file:

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

=======
Licence
=======

Licensed under Apache v2.0 license. Please see `LICENSE`_.


.. _here: http://apt.quarkslab.com/readme.txt
.. _install.rst: /install/install.rst
.. _LICENSE: /LICENSE

