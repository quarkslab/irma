***********************************
 IRMA Frontend - Installation guide
***********************************

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
    
   root <IRMA_INSTALL_DIR>/web/dist;
   
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
    
	<chdir><IRMA_INSTALL_DIR></chdir>
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
    CELERYD_CHDIR="<IRMA_INSTALL_DIR>"
   
copy ``celeryd.frontend.defaults`` config file to ``/etc/default/celeryd``
copy ``celeryd`` init script file to ``/etc/init.d``
launch celery

.. code-block:: bash

    $ sudo cp install/celery/celeryd.frontend.defaults etc/default/celeryd
    $ sudo cp install/celery/celeryd etc/init.d/celeryd
    $ sudo chmod +x /etc/init.d/celeryd
    $ sudo service celeryd start

===
FAQ
===


**install all requirements with pip**

.. code-block:: bash

   $ pip install -r requirements.txt



**Install a custom python package with custom install path (e.g. irma packages install)**

.. code-block:: bash

   $ pip install --install-option='--install-purelib=<custom path>' --install-option='--install-scripts=<scripts path>' -i http://<custom pkg server>/pypi <package-name>


**Detailed instructions for manual webui generation**

the default package is shipped with webui already generated. But if you
want to see how it is done see `webui`_ readme.



=======
Support
=======

Feeling lost ? need support ? irc: #qb_irma@freenode 



.. _webui: /web/README.rst
