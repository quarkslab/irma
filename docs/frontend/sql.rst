Installing SQL server
---------------------

The Frontend relies on a SQL database to keep track of all scans info.
On Debian, one can install a SQL server in few commands:

in development environment, prefer sqlite server:

.. code-block:: bash

    $ sudo apt-get install sqlite3
    [...]

in production environment, prefer postgres server:

.. code-block:: bash

    $ sudo apt-get install postgresql
    [...]

For PostgreSQL, extra steps for configuring the database and a user is required.
Then adapt the frontend configuration file to allow frontend to connect to the SQL
database. The tables are automatically created on celery daemon / uwsgi startup.