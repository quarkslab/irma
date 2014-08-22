.. _analyzer-configuration:

Enabling Analyzers
------------------

The python application auto-discovers available analyzers. As long as the
requirements are fulfilled for an analyzer, it is automatically discovered and
enabled. By default, no analyzers are available. The following enumerates the
requirements to enable each analyzer bundled with the application.

ClamAV - GNU/Linux
``````````````````

To enable ClamAV on Debian Stable distribution, one should install several
packages:

.. code-block:: bash

    $ sudo apt-get install clamav-daemon
    [...]
    $ sudo freshclam
    [...]
    $ sudo service restart clamav-daemon
    [...]

ComodoCAVL - GNU/Linux
``````````````````````

Comodo Antivirus for Linux can be downloaded from the `editor download page
<http://www.comodo.com/home/internet-security/antivirus-for-linux.php>`_. The
following instruction enable to install the Debian package. By default, the
binaries are installed in ``/opt/COMODO/`` directory.

.. code-block:: bash

    $ sudo dpkg -i cav-linux_1.1.268025-1_i386.deb
    [...]

Updates for the database can be performed with the following command:

.. code-block:: bash

    $ sudo /opt/COMODO/menu/comodo-updater
    [...]

.. note:: Dependencies to update the database

    To be able to update the database using the updater provided with Comodo
    Antivirus for Linux, some dependecies needed for the graphical interface
    may be missing from the distribution. On Debian Stable system, one can 
    install them with:

    .. code-block:: bash

        $ sudo apt-get install libqt4-sql libqt4-network

EsetNod32 - GNU/Linux
`````````````````````

One can request a trial version of Eset Nod32 Business Edition for Linux on the
`editor download page <http://www.eset.com/int/download//business/detail/family/69/>`_.

Once downloaded, the anti-virus can be installed with the following commands on
Debian. 

.. code-block:: bash

    $ sudo chmod u+x ueavbe.x86_64.en.linux
    $ sudo ./ueavbe.x86_64.en.linux
    [...]

Binaries should be installed in ``/opt/eset/esets`` directory. Updates are
performed from the GUI:

.. code-block:: bash

    $ sudo /opt/eset/esets/bin/esets_gui

.. note:: Disabling the antivirus daemon

    To avoid the anti-virus to protect your system at startup, we deliberately
    disabled the script used to launch the anti-virus early at boot:

    .. code-block:: bash

        $ sudo mv /etc/init.d/esets /etc/init.d/esets.disable

F-Prot - GNU/Linux
``````````````````

A copy of F-PROT anti-virus for Linux workstations is available on the
`editor download page
<http://www.f-prot.com/download/home_user/download_fplinux.html>`_.

The binaries should be installed in ``/usr/local/f-prot`` to make the python
application detect it automatically.

To launch an update, a configuration step is mandatory:

.. code-block:: bash

    $ sudo cp /usr/local/f-prot/f-prot.conf.default /etc/f-prot.conf

An update is launched with:

.. code-block:: bash

    $ sudo ./fpupdate
    ERROR: ld.so: object 'libesets_pac.so' from /etc/ld.so.preload cannot be preloaded: ignored.
    [...]

.. note:: Disclaimer

    The F-PROT anti-virus for Linux is free for home users, when used on
    personal workstations.

McAfeeVSCL -  GNU/Linux or Microsoft Windows
````````````````````````````````````````````

A free evaluation of McAfee VirusScan Command Line can be downloaded from the
`editor download page <http://www.mcafee.com/us/downloads/free-evaluations/>`_.

The binaries should be installed in ``/usr/local/uvscan/`` on GNU/Linux system
and must be installed in ``C:\VSCL`` on Windows Systems. Let us note that
updates must be performed manually. Anti-virus databases and engines can be
downloaded `here <http://www.mcafee.com/apps/downloads/security-updates/security-updates.aspx>`_.

Sophos - Microsoft Windows
``````````````````````````

A free evaluation of Sophos Endpoint Antivirus can be downloaded from the
`editor download page
<http://www.sophos.com/en-us/products/endpoint-antivirus/free-trial.aspx>`_.
It should be detected automatically if the anti-virus is installed in its
default installation directory.

Kaspersky - Microsoft Windows
`````````````````````````````

A free evaluation of Kaspersky Internet Security can be requested on the
`editor download page
<http://usa.kaspersky.com/downloads/free-home-trials/Internet-security>`_. It
should be detected automatically if the anti-virus is installed in its default
installation directory.

Symantec - Microsoft Windows
````````````````````````````

The procedure to install a trial version of Symantec Endpoint Protection is
particularly tedious. We will not document its installation.

VirusTotal - GNU/Linux or Microsoft Windows
```````````````````````````````````````````

The VirusTotal analyzer can be installed easily by downloading the python
packages it depends on and by modifying its configuration file. From the
installation directory, one can execute:

On GNU/Linux:

.. code-block:: none

    $ pip install -r modules/external/virustotal/requirements.txt
    [...]
    $ python setup.py configure --VirusTotal
    running configure

    Welcome to IRMA VirusTotal module configuration script.
    
    The following script will help you to create a new configuration for
    VirusTotal module on IRMA probe application.
    
    Please answer to the following questions so this script can generate the files
    needed by the application. To abort the configuration, press CTRL+D.
    
    > Do you want to use VirusTotal private API? (y/N) N
    > What is the apikey you would you like to use for VirusTotal? <api key here>
    
On Microsoft Windows:

.. code-block:: none

    $ C:\Python27\Scripts\pip.exe install -r modules/external/virustotal/requirements.txt
    [...]
    $ C:\Python27\python.exe setup.py configure --VirusTotal
    [...]

.. note:: Meaning of the fields in the configuration file

    +----------------+-------------+------------+-----------+--------------------------------------------------+
    | Section        | Option      | Type       | Default   | Description                                      |
    +----------------+-------------+------------+-----------+--------------------------------------------------+
    |                |   apikey    | ``string`` |           | api_key used to query VirusTotal API             |
    + VirusTotal     +-------------+------------+-----------+--------------------------------------------------+
    +                +   private   + ``boolean``+           + use private api (need a private api key)         |
    +----------------+-------------+------------+-----------+--------------------------------------------------+


NSRL - GNU/Linux
````````````````

The National Software Reference Library can be downloaded on the `NIST's web
page <http://www.nsrl.nist.gov/>`_. The provided files are stored in the RDS
(Reference Data Set) format. To use this analyzer, one must build first the
database. We use LevelDB as fast key-value storage library.

To build the dabatase, one must install first the dependencies:

.. code-block:: bash

    $ pip install -r modules/database/nsrl/requirements.txt

A (not optimized and very slow) helper script is provided to build the
database:

.. code-block:: bash

    $ python -m modules.database.nsrl.nsrl create -t os --filename NSRLOS.txt --database /home/irma/leveldb/os_db
    $ python -m modules.database.nsrl.nsrl create -t manufacturer --filename NSRLMfg.txt --database /home/irma/leveldb/mfg_db
    $ python -m modules.database.nsrl.nsrl create -t product --filename NSRLProd.txt --database /home/irma/leveldb/prod_db
    $ python -m modules.database.nsrl.nsrl create -t file --filename NSRLFile.txt --database /home/irma/leveldb/file_db

Finally, one must indicate to the analyzer where to find the files for the
database:

.. code-block:: none

    $ python setup.py configure --NSRL
    running configure

    Welcome to IRMA NSRL module configuration script.
 
    The following script will help you to create a new configuration for
    NSRL module on IRMA probe application.
 
    Please answer to the following questions so this script can generate the files
    needed by the application. To abort the configuration, press CTRL+D.
             
    > Where is located NSRL OS database? /home/irma/leveldb/os_db
    > Where is located NSRL MFG database? /home/irma/leveldb/mfg_db
    > Where is located NSRL PRODUCT database? /home/irma/leveldb/prod_db
    > Where is located NSRL FILE database? /home/irma/leveldb/file_db
     
The last command ask questions to the user for the configuration file
located at ``modules/database/nsrl/config.ini``.

.. note:: Meaning of the fields in the configuration file

    +----------------+-------------+------------+-----------+---------------------------------------+
    | Section        | Option      | Type       | Default   | Description                           |
    +----------------+-------------+------------+-----------+---------------------------------------+
    |                | nsrl_os_db  | ``string`` |           | location of the OS database           |
    |                +-------------+------------+-----------+---------------------------------------+
    |                | nsrl_mfg_db | ``string`` |           | location of the Manufacturer database |
    |     NSRL       +-------------+------------+-----------+---------------------------------------+
    |                | nsrl_file_db| ``string`` |           | location of the File database         |
    |                +-------------+------------+-----------+---------------------------------------+
    |                | nsrl_prod_db| ``string`` |           | location of the Product database      |
    +----------------+-------------+------------+-----------+---------------------------------------+

StaticAnalyzer - GNU/Linux or Microsoft Windows
```````````````````````````````````````````````

The PE File analyzer adapted from Cuckoo Sandbox can be installed easily. One
need to install the python packages it depends on. From the installation
directory, one can execute:

On GNU/Linux:

.. code-block:: bash

    $ pip install -r modules/metadata/pe_analyzer/requirements.txt
    [...]

On Microsoft Windows, you need cygwin to successfully install the requirements
(see `python-magic documentation
<https://github.com/ahupp/python-magic#dependencies>`_ for installation details):

.. code-block:: none

    $ C:\Python27\Scripts\pip.exe install -r modules/metadata/pe_analyzer/requirements.txt
    [...]
