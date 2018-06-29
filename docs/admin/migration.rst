Database migration
==================
IRMA uses `Alembic <https://alembic.readthedocs.org/en/latest/>`_ to manage and perform
databases migration.

.. note::

   Alembic is a useful tool to manage migration, but can't surpass local engine implementation
   of SQL. As ``SQLite`` doesn't manage schema modifications such as ``ALTER_COLUMN``, the
   whole migration system of IRMA won't support it. The preferred database engine is
   ``PostgreSQL``.

   You can still use SQLite, but you will be on your own for migrations.

.. warning::

   Please note that most of the manipulations on this can and sometimes will alter your data.
   If you are not sure about what you are doing, and even if you are sure, **make backup**.


Requirements
------------

- `Alembic package <https://pypi.python.org/pypi/alembic>`_


Content
-------

Database migrations are managed in the **frontend** and **brain** IRMA components.

The files/directories used are:

.. code-block:: none

     alembic.ini
     extras/migration/
       +- env.py
       +- script.py.mako
       +- versions/
            +- <revision_1>.py
            +- <revision_2>.py
            +- ...

.. note::

   All the commands below will assert to be executed on top of this file system,
   as Alembic needs the ``alembic.ini`` configuration file.

   You could also use the ``-c <path_to_conf_file>``.


Usage
-----

Alembic manage a 'revision' for each database evolution. These revisions are used to upgrade or
downgrade the database schema.

The command:

.. code-block:: console

   $ alembic current

... shows the current revision of the database.

The command to get the history of the latest alembic migrations is:

.. code-block:: console

   $ alembic history --verbose

Create database from scratch with Alembic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration and creating database
"""""""""""""""""""""""""""""""""""

Alembic will use the information in the ``[sqldb]`` section of the configuration files
(respectively ``config/frontend.ini`` or ``conf/brain.ini`` for the repositories of
the frontend or the brain components). Make sure they are accurate.


The database must already exist. This step is quite simple, the SQL command usually being:

.. code-block:: none

   sql$ CREATE DATABASE <db_name>;

Update your schema with Alembic
"""""""""""""""""""""""""""""""

If you use a virtualenv, activate it. Then enter:

.. code-block:: console

   $ alembic upgrade head

Alembic applies each revision one after the other. At the end of the process, if no error
occurs, your database should be updated.

.. note::

   You can update the database one revision at a time, or up to a specific revision. See the
   revisions_ section for further information.


If you already have a database WITHOUT Alembic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alembic stores its current revision number in database. If your database doesn't have this
information, you are very likely to encounter errors when using Alembic, as it will try to
create already existing tables.

The easiest solution is to destroy your database and go for a fresh install.

Although, if you don't want to lose your data, you could update the Alembic information
manually.

You will need to:

#. Get the exact current Alembic revision of your database. Each migration file has a
   ``Revision ID`` in its header. Investigate the successive revisions to know which one
   matches your current database state.
#. Once you known your Alembic revision, run:

   .. code-block:: console

      $ alembic stamp <your_alembic_revision_number>

#. Your database is now synchronized with Alembic! You should be able to use Alembic to
   upgrade/downgrade your database now. Be aware that if the revision number you provided is
   false, you could encounter massive errors while attempting to upgrade/downgrade your
   database.


Generating a new revision
^^^^^^^^^^^^^^^^^^^^^^^^^

Creating a new revision can be done with the command:

.. code-block:: console

    $ alembic revision -m <revision_message>

This command produces a new ``<hash>_<revision_message>.py`` file in the ``extras/migration/versions/``
directory. This file contains two functions ``upgrade`` and ``downgrade``, respectively used
to upgrade the database to the revision, or downgrade from it. These two functions are empty
and must be completed with the desired modifications (see the
`alembic documentation section ops <https://alembic.readthedocs.org/en/latest/ops.html>`_).

A revision could be produced automatically, from database metadata defined in the IRMA SQL
objects description through ``sqlalchemy``, with the command:

.. code-block:: console

    $ alembic revision --autogenerate -m <revision_message>

These SQL objects are defined in:

* ``frontend/models/sqlobjects.py`` for the frontend,
* ``brain/models/sqlobjects.py`` for the brain.

Alembic scripts in IRMA repositories are already configured to use metadata defined in these
files. You should be able to use the ``--autogenerate`` option without further modifications.

.. note::

   IRMA configuration allows to prefix table names through configuration. Our revision files
   use the function ``<frontend_or_brain>/config/parser.py:prefix_table_name`` to generate table
   names rather than keeping alembic-generated plain string names. A good practice would be
   to keep using this function in revision files.

.. warning::

   Alembic easily detects changes such as adding/removing columns, but could be blind on thin,
   inner modifications. Re-reading the auto-generated script is a strongly recommended step
   before actually performing the migration.

   See the  `alembic documentation section autogenerate   <https://alembic.readthedocs.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect>`_
   for more information.

.. warning::

   Database modifications using ``ALTER_COLUMN`` (such as changing the type of
   a column) can't be performed on ``SQLite`` databases. Be aware of this
   limitation if you **absolutely** want to use migration scripts with this SQL
   engine.


.. _revisions:

Migrating between revisions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the revision is properly described, the migration is performed with:

.. code-block:: console

   $ alembic upgrade head

Alembic allows to migrate the database to any revision, relatively to the current revision
or absolutely. Several examples:

.. code-block:: console

   $ alembic upgrade +4
   $ alembic downgrade base
   $ alembic upgrade <revision_number>+3


Tips and tricks
---------------

.. note::

  Don't trust Alembic too much. It is nothing more than a tool, without any comprehension
  on the code. Cautiously read the revision scripts it generates.

.. note::
   Database migration is hardly ever a painless step. Be sure to:

   1. save your data before performing a migration,
   2. test your application after the migration to ensure its  compatibility with the new data
      schemes.

.. note::

   With a ``PostgreSQL`` database, the ``Float`` type is tolerated but the real type name used
   by the database is ``Real``. It means that SQL objects described in ``sqlalchemy`` with
   ``Float`` columns will be properly applied in database, but at each autogenerate revision,
   ``alembic`` will see ``Real`` type in database, against ``Float`` type in the code metadata,
   and so will perform each time a useless ``alter_column`` from ``Real`` to ``Float``.
   This problem could be avoided (with ``PostgreSQL``) by declaring ``Real`` instead of ``Float``.

   See `this page <http://www.postgresql.org/docs/9.1/static/datatype-numeric.html>`_  for more
   information on ``PostgreSQL`` numeric types.

.. note::

   Alembic can't directly deal with many somehow complex operations, such as type migration
   with no trivial cast. In these cases, the operation must be manually described with a raw
   SQL command (which could be database-dependent).

   For instance, alembic can't perform the migration from ``real`` to ``datetime``:

   .. code-block:: python

       > alembic.alter_column('table', 'column',
                              existing_type=sqlalchemy.REAL(),
                              type_=sqlalchemy.DateTime(),
                              existing_nullable=False)

  ... because of an error ``a column "column" cannot be cast automatically to type timestamp
  with time zone``.

  A proper migration for ``PostgreSQL`` would be (in ``Python``):

  .. code-block:: python

     > alembic.execute('ALTER TABLE "table" ALTER COLUMN "column" TYPE TIMESTAMP WITHOUT TIME ZONE USING to_timestamp(column)')

  And the reverse code to downgrade the migration could be:

  .. code-block:: python

     > alembic.execute('ALTER TABLE "table" ALTER COLUMN "column" TYPE REAL USING extract(epoch from column)')


.. note::

   Rather than managing migrations directly with Alembic, we could generate SQL migration
   revision to be used directly on database with the command:

   .. code-block:: console

      $ alembic upgrade <revision> --sql > migration.sql

.. note::

   Deleting a revision *R* is simple:

   * downgrade the database to the revision before *R-1* the revision you want to delete;
   * if any, edit the script of the following revision *R+1* and update the ``down_revision``
     variable to match the revision number of revision *R-1*;
   * delete the script of the revision *R* you want to delete;
   * upgrade your database.

   The deleted revision want be applied any more.


..
   https://www.sqlite.org/datatype3.html

