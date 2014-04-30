***********************************
 IRMA Frontend - Installation guide
***********************************

--------------------


**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none

------------
Requirements
------------

**packages:**

* python2.7
* python-pip
* mongodb-server
* nginx
* uwsgi
* uwsgi-plugin-python
* ruby
* python-gridfs

**python packages:**

* celery
* pymongo
* redis
* bottle

**ruby packages:**

* see section `Web gui generation`_

**node.js packages:**

* see section `Web gui generation`_

-------------
Configuration
-------------

**mongodb**

edit ``/etc/mongodb.conf`` to listen only on loopback interface (add extra auth parameters).

.. code-block::

   bind_ip 127.0.0.1
   port = 27017
   
**nginx**

edit ``install/nginx/frontend`` according to your install

.. code-block::
    
   root /home/irma/irma/web/dist;
   
copy ``frontend`` config file to ``/etc/nginx/sites-available``
make a soft link into ``/etc/nginx/sites-enabled``
relaunch nginx

.. code-block:: bash

    $ cp install/nginx/frontend /etc/nginx/sites-available
    $ ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/frontend
    $ sudo service nginx restart

**uwsgi**

edit ``install/uwsgi/frontend-api.xml`` according to your install

.. code-block::
    
	<chdir>/home/irma/irma</chdir>
	<app mountpoint="/_api">
		<script>./frontend/web/api.py</script>
	</app>
   
copy ``frontend-api.xml`` config file to ``/etc/uwsgi/apps-available/``
make a soft link into ``/etc/uwsgi/apps-enabled/``
relaunch uwsgi

.. code-block:: bash

    $ cp install/uwsgi/frontend-api.xml /etc/uwsgi/apps-available/
    $ ln -s /etc/uwsgi/apps-available/frontend-api.xml /etc/uwsgi/apps-enabled/frontend-api.xml
    $ sudo service uwsgi restart
    
**celery**

edit ``install/celery/celeryd.frontend.defaults`` according to your install

.. code-block::
    
    # Where to chdir at start.
    CELERYD_CHDIR="/home/irma/irma/"
   
copy ``celeryd.frontend.defaults`` config file to ``/etc/default/celeryd``
copy ``celeryd`` init script file to ``/etc/init.d``
launch celery

.. code-block:: bash

    $ sudo cp install/celery/celeryd.frontend.defaults etc/default/celeryd
    $ sudo cp install/celery/celeryd etc/init.d/celeryd
    $ sudo chmod +x /etc/init.d/celeryd
    $ sudo service celeryd start

------------------
Web gui generation
------------------

Requirements: 

* npm
* bower
* grunt
* compass

**npm**

.. code-block:: bash

    $ cd /tmp
    $ wget https://raw.github.com/nicolargo/nodeautoinstall/master/nodeautoinstall.py
    $ sudo python ./nodeautoinstall.py -d
    $ export PATH=$PATH:/opt/node/bin
    $ export NODE_PATH=/opt/node:/opt/node/lib/node_modules

**bower**

.. code-block:: bash

    $ sudo npm install -g bower
    
**grunt**

.. code-block:: bash

    $ sudo npm install -g grunt
    $ sudo npm install -g grunt-cli

**compass**

.. code-block:: bash

    $ sudo gem install compass

**gui generation**

.. code-block:: bash

    $ cd <IRMA_INSTALL_DIR>/web
    $ npm install
    $ bower install
    $ cd app
    $ ln -s `pwd`/bower_components `pwd`/app/bower_components
    $ grunt build
    $ ln -s `pwd`/.tmp/styles `pwd`/dist/styles

--------------------

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



   
