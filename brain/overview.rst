Architecture
------------

Let us recall first the inner architecture of the **Brain**. It uses multiple
technologies with a specific purpose each:

* a Celery worker that handles scan requests from **Frontends** and results
  returned by the **Probes**.
* a RabbitMQ server used by Celery as a backend and as a broker for task queues
  and job queues used to schedule tasks for
  **Probes** (for scan jobs) and the **Frontend** (for scan results).
* a FTP server with TLS enabled where files to be scanned are uploaded by
  **Frontends** and downloaded by **Probes**,
