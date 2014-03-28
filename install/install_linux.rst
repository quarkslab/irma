*****************
 IRMA Probe linux
*****************

**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none

------------
Requirements
------------

packages:

* python27
* pip

with pip install:

* celery
* redis
* irma-probe

(see FAQ 'install all requirements with pip')

extra package:

- NSRL:

* leveldb

- VirusTotal:

* requests

- Static Analyzer:

* pefile

**celery**

edit ``install/celery/celeryd.probe.defaults`` according to your install

.. code-block::
    
    # Where to chdir at start.
    CELERYD_CHDIR="/home/irma/irma/"
   
copy ``celeryd.probe.defaults`` config file to ``/etc/default/celeryd``
copy ``celeryd`` init script file to ``/etc/init.d``
launch celery

.. code-block:: bash

    $ sudo chmod +x /etc/init.d/celeryd
    $ sudo service celeryd start


===
FAQ
===

**Install a python package with pip**

.. code-block:: bash
  
   $ pip install <package-name>

--------------------

**Update a python package with pip**

.. code-block:: bash

   $ pip install --upgrade <package-name>

--------------------

**Install a specific version of a python package with pip**

.. code-block:: bash

   $ pip install <package-name>==<version>

--------------------

**install all requirements with pip**

.. code-block:: bash

   $ pip install -r requirements.txt


--------------------

**Install a custom python package with custom install path (e.g. irma packages install)**

.. code-block:: bash

   $ pip install --install-option='--install-purelib=<custom path>' --install-option='--install-scripts=<scripts path>' -i http://<custom pkg server>/pypi <package-name>


--------------------

**Start a service at boot**

.. code-block:: bash

    $ sudo /usr/sbin/update-rc.d <service-name> defaults

--------------------


=======
Support
=======

Feeling lost ? need support ? irc: #irma-qb@chat.freenode.net 

----------------------

.. _simplepypi: https://github.com/steiza/simplepypi

   
