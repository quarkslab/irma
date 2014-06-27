************
IRMA - Probe
************

========
Overview
========

This package handles the scan job for one file.

Features
--------

Support for the following Linux Antiviruses:

    * Clam Antivirus
    * Comodo Antivirus
    * Eset Nod32 Business Edition
    * F-Prot
    * McAfee VirusScan Command Line Scanner
    * Sophos 

Support for the following Windows Antiviruses:

    * Kasperksy
    * MacAfee
    * Sophos
    * Symantec

External web info:

    * Virustotal (lookup by sha256, the file is not send)

Database info:

    * NSRL database

Others:

    * Static Analyzer (adapted from Cuckoo Sandbox)

=======
Install
=======

Quick Installation
------------------

Add Quarkslab public GPG key

.. code-block:: bash

    $ wget -O - http://www.quarkslab.com/qb-apt-key.asc | sudo apt-key add  -


Add Quarkslab's repository source


.. code-block:: bash

    echo 'deb http://apt.quarkslab.com/pub/debian stable main' | sudo tee /etc/apt/sources.list.d/quarkslab.list


Install Meta package

.. code-block:: bash

    sudo apt-get update && sudo apt-get install irma-probe

Do not forget to change parameters according to your settings (See ``Config`` paragraph).


Detailed Installation
---------------------

For a detailed windows probe install guide see `windows`_ install.

For a detailed linux probe install guide see `linux`_ install.


.. NOTE::

    With the default installation, no probe is available. One can easily set up
    the following probes for tests purposes:

         - ClamAV (on debian, ``apt-get install clamav``
         - VirusTotal (``pip install requests`` and add VirusTotal API key in config file)
         - StaticAnalyzer (``pip install python-magic pefile``)

    Then, one can see the detected probes with the following command from irma
    installation directory:

    .. code-block:: bash

        $ cd /opt/irma/irma-probe
        $ python -m probe/tasks


======
Config
======

irma-probe configuration file:

+----------------+-------------+------------+-----------+
|     Section    |      Key    |    Type    |  Default  |
+================+=============+============+===========+
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
|  backend probe |     port    |``integer`` |   6379    |
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

The default location of the configuration file is ``IRMA_INSTALL_DIR/config/probe.ini``

**optional configuration parameters**

- NSRL requires extra configuration (files path)

+----------------+-------------+------------+-----------+
|                | nsrl_os_db  | ``string`` |           |
|                +-------------+------------+-----------+
|                | nsrl_mfg_db | ``string`` |           |
|     NSRL       +-------------+------------+-----------+
|                | nsrl_file_db| ``string`` |           |
|                +-------------+------------+-----------+
|                | nsrl_prod_db| ``string`` |           |
+----------------+-------------+------------+-----------+

- VirusTotal needs an API key

+----------------+-------------+------------+-----------+
|   VirusTotal   |   api_key   | ``string`` |           |
+----------------+-------------+------------+-----------+


TODO
----

* Remove script folder and replace with our python script
* Add option to disable a probe from configuration file
* Add support for more Linux and Windows antiviruses. For command line options, see following links:
    - http://www.shadowserver.org/wiki/pmwiki.php/AV/Viruses
    - https://github.com/xchwarze/KIMS/tree/master/Data
    - https://github.com/joxeankoret/multiav
* Improve import from NRSL database
* Make an plugin-friendly interface for static modules
* Launch celery from a python script
* Add support for more Linux and Windows antiviruses
* Add different heuristics for antiviruses

.. _windows: /install/install_win.rst
.. _linux: /install/install_linux.rst

