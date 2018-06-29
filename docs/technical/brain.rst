Brain
=====

The **Brain** is a python-based application that only dispatches analysis
requests from different frontends [#]_ to the available **Probes**. Analyses
are scheduled by the **Brain** on **Probes** through Celery, an open source
task.

.. rubric:: Footnotes

.. [#] This feature is not ready yet, we are currently working on its
       implementation.

Installation
------------

The **Brain** must be installed on a GNU/Linux distribution. With some efforts,
it should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

This section describes how to get the source code of the application for the
**Brain** and to install it.

Architecture
------------

Let us recall first the inner architecture of the **Brain**. It uses multiple
technologies with a specific purpose each:

* a Celery worker that handles scan requests from **Frontends** and results
  returned by the **Probes**.
* a RabbitMQ server used by Celery as a backend and as a broker for task queues
  and job queues used to schedule tasks for
  **Probes** (for scan jobs) and the **Frontend** (for scan results).
* an SFTP server where files to be scanned are uploaded by
  **Frontends** and downloaded by **Probes**,

Nginx
-----

In the **Frontend**, we use a nginx web server to serve the uWSGI application
and the static web site that query the API in order to get results of scanned
files and to present them to the user.

SQL server
----------

The Frontend relies on a PostgreSQL database to keep track of all scans info.
