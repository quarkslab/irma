*****************
 IRMA Probe Linux
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

* python2.7
* python-pip

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

Make all services start at boot:

.. code-block:: bash

    $ sudo /usr/sbin/update-rc.d celeryd defaults

launch celery

.. code-block:: bash

    $ sudo chmod +x /etc/init.d/celeryd
    $ sudo service celeryd start

===============
Troubleshooting
===============

Configuration and probes
------------------------

Probes have a "standalone" version which can be loaded from the command-line.
This standalone version is useful to troubleshoot some installation issues or 
to check all available probes. We assume that the file ``config/probe.ini`` 
has already been configured properly. In this output, only VirusTotal probe 
has been detected (each probe connects to a dedicated queue).

.. code-block:: bash

    $ python -m probes/tasks
    No module named leveldb
    No handlers could be found for logger "probes.database.nsrl"
    No module named leveldb

     -------------- celery@probe-0479a41b-8406-46bc-a74d-1659ae8ae2e8 v3.1.10 (Cipater)
     ---- **** -----
     --- * ***  * -- Linux-3.2.0-4-amd64-x86_64-with-debian-7.5
     -- * - **** ---
     - ** ---------- [config]
     - ** ---------- .> app:         probe.tasks:0x159c050
     - ** ---------- .> transport:   amqp://probe@irma-brain:5672/mqprobe
     - ** ---------- .> results:     redis://irma-brain:6379/1
     - *** --- * --- .> concurrency: 1 (prefork)
     -- ******* ----
     --- ***** ----- [queues]
     -------------- .> VirusTotal       exchange=celery(direct) key=VirusTotal
     
     
     [tasks]
       . probe.tasks.probe_scan
       
     [2014-04-30 13:51:57,161: INFO/MainProcess] Connected to amqp://probe@irma-brain:5672/mqprobe
     [2014-04-30 13:51:57,333: WARNING/MainProcess] celery@probe-0479a41b-8406-46bc-a74d-1659ae8ae2e8 ready.


Celery daemon
-------------

One can check if celery daemon run properly for probes by consultings the logs
located at ``/var/log/celery/*.log``

.. code-block:: bash

    $ cat /var/log/celery/*.log
    [...]
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker1@irma-probe ready.
    [...]
    [2014-04-30 13:35:04,205: WARNING/MainProcess] worker2@irma-probe ready.
    [...] 
    [2014-04-30 13:35:03,949: WARNING/MainProcess] worker3@irma-probe ready.

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

   
