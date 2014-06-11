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

The following script installs IRMA on a probe with default values. Do not
forget to change parameter according to your setting. For a more advanced
installation, see detailed installation section.

.. code-block:: bash

    #!/bin/bash

    ###########################################################
    # Parameters
    ###########################################################

    PROBE_NAME="multiprobe"
    BRAIN_IP_ADDR="brain.irma.qb"

    ###########################################################
    # Install dependencies
    ###########################################################

    sudo apt-get install gdebi

    ###########################################################
    # Download packages
    ###########################################################

    curl -O https://github.com/quarkslab/irma-probe/releases/download/v1.0.2/irma-probe_1.0.2-1_all.deb

    ###########################################################
    # Install packages
    ###########################################################

    sudo gdebi irma-probe_1.0.2-1_all.deb

    ###########################################################
    # Configuration
    ###########################################################

    sudo sed -i "s/^name\s*=.*$/name = $PROBE_NAME/" /opt/irma/irma-probe/config/probe.ini
    sudo sed -i "s/^host\s*=.*$/host = $BRAIN_IP_ADDR/" /opt/irma/irma-probe/config/probe.ini

    ###########################################################
    # Install probes & restart services
    ###########################################################

    sudo apt-get install clamav clamav-daemon  # For ClamAV probe
    sudo pip install requests    # For VirusTotal probe (need api key, see config)
    sudo pip install pefile python-magic  # For Cuckoo's Static Analyzer

    sudo /etc/init.d/celeryd restart


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

* Make an plugin-friendly interface for static modules
* Launch celery from a python script
* Add support for more Linux and Windows antiviruses
* Add different heuristics for antiviruses
* Add speed parameter for antiviruses

.. _windows: /install/install_win.rst
.. _linux: /install/install_linux.rst

