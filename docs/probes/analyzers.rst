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
    $ sudo service clamav-daemon restart
    [...]

ComodoCAVL - GNU/Linux
``````````````````````

Comodo Antivirus for Linux can be downloaded from the `Comodo's download page
<http://www.comodo.com/home/internet-security/antivirus-for-linux.php>`_. The
following instruction enable to install the Debian package. By default, the
binaries are installed in ``/opt/COMODO/`` directory. As ComodoCAVL is not
packaged for the current Debian Stable distribution, we must install it
manually:

.. code-block:: bash

    $ sudo apt-get install binutils
    $ ar x cav-linux_1.1.268025-1_iXXX.deb
    $ sudo tar xvf ~/data.tar.gz -C /
    [...]

Updates for the database can be performed with the following command:

.. code-block:: bash

    $ XAUTHORITY="$HOME/.Xauthority" sudo /opt/COMODO/menu/comodo-updater
    [...]

.. note:: Dependencies to update the database

    To be able to update the database using the updater provided with Comodo
    Antivirus for Linux, some dependecies needed for the graphical interface
    may be missing from the distribution. On Debian Stable system, one can
    install them with:

    .. code-block:: bash

        $ sudo apt-get install libqt4-sql libqt4-network libqtgui4

EsetNod32 - GNU/Linux
`````````````````````

One can request a trial version of Eset Nod32 Business Edition for Linux on the
`Eset download page <http://www.eset.com/int/download/home/detail/family/71/>`_.
Once downloaded, the anti-virus can be installed with the following commands on
Debian. Just follow the typical installation on the GUI:

.. code-block:: bash

    $ sudo chmod u+x eset_nod32av_64bit_en.linux
    $ sudo apt-get install libgtk2.0-0 libc6-i386
    $ sudo ./eset_nod32av_64bit_en.linux
    [...]

Binaries should be installed in ``/opt/eset/esets`` directory. Updates are
performed from the GUI:

.. code-block:: bash

    $ XAUTHORITY="$HOME/.Xauthority" sudo /opt/eset/esets/bin/esets_gui

.. note:: Disabling the antivirus daemon

    To avoid the anti-virus to protect your system at startup, we deliberately
    disabled the script used to launch the anti-virus early at boot:

    .. code-block:: bash

        $ sudo service esets stop
        $ sudo mv /etc/init.d/esets /etc/init.d/esets.disable

F-Prot - GNU/Linux
``````````````````

A copy of F-PROT anti-virus for Linux workstations is available on the
`F-PROT download page
<http://www.f-prot.com/download/home_user/download_fplinux.html>`_.

The binaries should be installed in ``/usr/local/f-prot`` to make the python
application detect it automatically.

.. code-block:: bash

    $ sudo tar xvf fp-Linux.x86.32-ws.tar.gz -C /usr/local/

To launch an update, a configuration step is mandatory:

.. code-block:: bash

    $ sudo cp /usr/local/f-prot/f-prot.conf.default /etc/f-prot.conf

An update is launched with:

.. code-block:: bash

    $ sudo ./fpupdate
    ERROR: ld.so: object 'libesets_pac.so' from /etc/ld.so.preload cannot be preloaded: ignored.
    [...]

.. note:: Error

    If you see an error message like:

    .. code-block:: bash

        DownloadingWarning: Network - Connection failed (18), trying again...
        Downloading updateError: Update - Bad mergefile

    Just relaunch the script.

.. note:: Dependencies to update the database

    To be able to update the database using the updater provided with Comodo
    install them with:

    .. code-block:: bash

        $ sudo apt-get install libc6-i386


McAfeeVSCL -  GNU/Linux or Microsoft Windows
````````````````````````````````````````````

A free evaluation of McAfee VirusScan Command Line can be downloaded from the
`editor download page <http://www.mcafee.com/apps/downloads/free-evaluations/>`_.

The binaries should be installed in ``/usr/local/uvscan/`` on GNU/Linux system
and must be installed in ``C:\VSCL`` on Windows Systems. Let us note that
updates must be performed manually. Anti-virus databases and engines can be
downloaded `here <http://www.mcafee.com/apps/downloads/security-updates/security-updates.aspx>`_.

After downloading McAfee Virus Scan archive, create ``/usr/local/uvscan`` and
extract the archive in it:

.. code-block:: bash

    $ sudo mkdir /usr/local/uvscan
    $ sudo tar xvf vscl-XXX.tar.gz -C /usr/local/uvscan # replace using your values
    $ sudo chmod +x /usr/local/uvscan/uvscan

Extract also, using unzip program, the database:

.. code-block:: bash

    $ sudo unzip avvepo7536dat.zip -d /usr/local/uvscan
    $ cd /usr/local/uvscan
    $ sudo unzip avvdat-XXXX.zip

Sophos - GNU/Linux or Microsoft Windows
```````````````````````````````````````

A free evaluation of Sophos Endpoint Antivirus can be downloaded from the
`editor download page
<http://www.sophos.com/en-us/products/endpoint-antivirus/free-trial.aspx>`_.
You should receive by email a username and a password to authenticate for updates.

It should be detected automatically by IRMA if the anti-virus is installed in its
default installation directory.

On GNU/Linux:

- Download the archive for Linux, then execute:

.. code-block:: bash

    $ tar zxf sav-linux-9-i386.tgz
    $ ./sophos-av/install.sh /opt/sophos-av --acceptlicence --autostart=False --enableOnBoot=False --automatic --ignore-existing-installation
    $ /opt/sophos-av/bin/savconfig set EnableOnStart false
    $ /opt/sophos-av/bin/savconfig set PrimaryUpdateSourcePath "sophos:"
    $ /opt/sophos-av/bin/savconfig set PrimaryUpdateUsername "<your_username_from_email>"
    $ /opt/sophos-av/bin/savconfig set PrimaryUpdatePassword "<your_password_from_email>"
    $ /opt/sophos-av/bin/savupdate

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

G Data - Microsoft Windows
``````````````````````````

A trial version of G Data is available on the `editor download page
<https://www.gdata.de/kundenservice/downloads.html>`. It should be detected
automatically if the anti-virus is installed in its default installation
directory.

VirusTotal - GNU/Linux or Microsoft Windows
```````````````````````````````````````````

The VirusTotal analyzer can be installed easily by downloading the python
packages it depends on and by modifying its configuration file. From the
installation directory, one can execute:

On GNU/Linux:

.. code-block:: none

    $ pip install -r modules/external/virustotal/requirements.txt
    [...]

then update configuration file located at ``modules/external/virustotal/config.ini``.

.. note:: Meaning of the fields in the configuration file

    +----------------+-------------+-------------+-----------+--------------------------------------------------+
    |   Section      | Option      | Type        | Default   | Description                                      |
    +----------------+-------------+-------------+-----------+--------------------------------------------------+
    |   VirusTotal   |   apikey    | ``string``  |           | api_key used to query VirusTotal API             |
    +----------------+-------------+-------------+-----------+--------------------------------------------------+
    |   VirusTotal   |   private   | ``boolean`` |           | use private api (need a private api key)         |
    +----------------+-------------+-------------+-----------+--------------------------------------------------+


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

    $ mkdir /home/irma/leveldb
    $ python -m modules.database.nsrl.nsrl create -t os NSRLOS.txt /home/irma/leveldb/os_db
    $ python -m modules.database.nsrl.nsrl create -t manufacturer NSRLMfg.txt /home/irma/leveldb/mfg_db
    $ python -m modules.database.nsrl.nsrl create -t product NSRLProd.txt /home/irma/leveldb/prod_db
    $ python -m modules.database.nsrl.nsrl create -t file NSRLFile.txt /home/irma/leveldb/file_db

Finally, one must indicate to the analyzer where to find the files for the
database by filling the configuration file located at ``modules/database/nsrl/config.ini``.

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

.. note:: Error

    If you see an error message like:

    .. code-block:: bash

        fatal error: Python.h: No such file or directory

    Then you'll need to install python3-dev package (for Debian like systems).

.. note:: leveldb.LevelDBError: IO error: /home/irma/leveldb/file_db/LOCK: Permission denied

    If you encounter this problem, you likely have a problem with unix
    permissions. Please ensure that the folder is owned by the user
    running the probes. On ``supervisord``-based installation (default for
    vagrant/ansible scripts), the folder owner should be set to  ``nobody``.
    For ``init.d``-based installation, it should be ``irma`` instead.


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
(see `python3-magic documentation
<https://github.com/ahupp/python-magic#dependencies>`_ for installation details):

.. code-block:: none

    $ C:\Python27\Scripts\pip.exe install -r modules/metadata/pe_analyzer/requirements.txt
    [...]

Yara - GNU/Linux or Microsoft Windows
`````````````````````````````````````

Please refer to ``modules/metadata/yara/README.md`` file for the documentation.

Guide on Debian (credits to Carbonn)
++++++++++++++++++++++++++++++++++++

1. Installing dependencies

.. code-block:: bash

    $ sudo apt-get install libtool automake bison

2. Installing Yara python modules

.. code-block:: bash

    $ git clone https://github.com/plusvic/yara.git
    $ autoreconf -i --force
    $ ./configure
    $ make
    $ sudo make install
    $ python setup.py build
    $ sudo python setup.py install
    $ sudo ldconfig


3. Configuring for IRMA

.. code-block:: bash

    $ mkdir /opt/irma/yara_rules/
    $ cat /opt/irma/yara_rules/yara_rules.yar << EOF
    # Insert rule below inside the file

    rule silent_banker : banker
    {
        meta:
            description = "This is just an example"
            thread_level = 3
            in_the_wild = true

        strings:
            $a = {6A 40 68 00 30 00 00 6A 14 8D 91}
            $b = {8D 4D B0 2B C1 83 C0 27 99 6A 4E 59 F7 F9}
            $c = "UVODFRYSIHLNWPEJXQZAKCBGMT"

        condition:
            $a or $b or $c
    }
    EOF
