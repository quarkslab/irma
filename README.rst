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

    * Static Analyzer

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


**Install**

for a detailed windows probe install guide see `windows`_ install.
for a detailed linux probe install guide see `linux`_ install.

TODO
----

* Remove script folder and replace with our python script
* Add option to disable a probe from configuration file
* Add support for more Linux and Windows antiviruses. For command line options, see following links:
    - http://www.shadowserver.org/wiki/pmwiki.php/AV/Viruses
    - https://github.com/xchwarze/KIMS/tree/master/Data
    - https://github.com/joxeankoret/multiav
* Improve import from NRSL database
* Add different heuristics for antiviruses

.. _windows: /install/install_win.rst
.. _linux: /install/install_linux.rst

