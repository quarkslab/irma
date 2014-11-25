Architecture
------------

Let us recall first the inner architecture of the **Frontend**. It uses
multiple technologies with each a specific purpose:

* A client through which an user submits a file and get the analysis results.
  There are two clients bundled in the repository: a web user interface and a
  command-line client.
* A python-based restful API, served by a nginx web server and a uWSGI
  application server. It gets the results of a file scan by querying a
  database.
* A worker that will handle scan submission to the **Brain** and store the
  results of analyzes scheduled by the **Brain**. The worker relies on Celery,
  a python-based distributed task queue.
* An hybrid database server (SQL/mongodb) is used to store results of analyzes
  made on each file submitted either by the web graphical interface or the CLI
  client.
