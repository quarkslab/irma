Frontend
========

The **Frontend** handles scan submission to the **Brain**, stores the results
of the scanned files. These results can be displayed through a web graphical
user interface or via the command line interface.

Installation
------------

The **Frontend** must be installed on a GNU/Linux system. With some efforts, it
should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

This section describes how to get the source code of the application and to
install it.


Architecture
------------

Let us recall first the inner architecture of the **Frontend**. It uses
multiple technologies with each a specific purpose:

* A client through which a user submits a file and get the analysis results.
  There are two clients bundled in the repository: a web user interface and a
  command-line client.
* A python-based restful API, served by a NGINX web server and a uWSGI
  application server. It gets the results of a file scan by querying a
  database.
* A worker that will handle scan submission to the **Brain** and store the
  results of analyzes scheduled by the **Brain**. The worker relies on Celery,
  a python-based distributed task queue.
* A database server (PostgreSQL) is used to store results of analyzes
  made on each file submitted either by the web graphical interface or the CLI
  client.
