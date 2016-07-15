Installing SQL server
---------------------

.. note::

	Since version 1.5.0, IRMA required a postgreSQL server as we are using JSONB column.


The Frontend relies on a PostgreSQL database to keep track of all scans info.
On Debian, one can install a PostgreSQL server in few commands:

Install it with the following dependencies:

.. code-block:: bash

    $ sudo apt-get install postgresql-9.4 python-psycopg2
    [...]

You need to manually create the configured database and db user, the tables are automatically
created on celery daemon / uwsgi startup.