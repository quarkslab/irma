How to migrate
--------------

.. note::
	If you need help to connect to your box through ssh, see vagrant FAQ

This part is only useful to someone willing to manually upgrade from an older version of IRMA.

Install alembic
+++++++++++++++

.. code-block:: bash

	$ sudo su deploy
	$ cd /opt/irma/irma-frontend/current
	$ ./venv/bin/pip install alembic
	$ export PYTHONPATH=.:$PYTHONPATH
	$ alembic history

	430a70c8aa21 -> eb7141efd75a (head), version 1.3.0
	2cc69d5c53eb -> 430a70c8aa21, version 1.2.1
	<base> -> 2cc69d5c53eb, DB revision creation


from 1.2.1 to 1.3.0
+++++++++++++++++++

Fix nginx configuration
^^^^^^^^^^^^^^^^^^^^^^^

Introducing multiversion API means python code should receive the api version parameter.
in file `/etc/nginx/sites-available/irma-frontend.conf` replace:

.. code-block:: bash

    rewrite ^/api/v1/(.+) /$1 break;

by:

.. code-block:: bash

	rewrite ^/api/(.+) /$1 break;

and restart nginx

Migrate Database
^^^^^^^^^^^^^^^^

First you should tell alembic you are at version 1.2.1:

.. code-block:: bash

	$ ./venv/bin/alembic stamp 430a70c8aa21

then upgrade model and data:


.. code-block:: bash

	$ ./venv/bin/alembic upgrade head


Regenerate IHM
^^^^^^^^^^^^^^

to regenerate IHM do the following:


.. code-block:: bash

	$ sudo su deploy
	$ cd /opt/irma/irma-frontend/current/web
	$ ./node_modules/.bin/bower update
	$ ./node_modules/.bin/gulp dist

Its done.




