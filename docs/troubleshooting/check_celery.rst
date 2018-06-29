Check Celery configuration
==========================
Celery Workers
``````````````

Before going further, you should check that the python applications manages to
communicate with the RabbitMQ server through Celery. To ensure that, from the
installation directory, execute both Celery workers:

On GNU/Linux:

.. code-block:: console

    $ cd /opt/irma/irma-brain/current
    $ ./venv/bin/python -m brain.scan_tasks


     -------------- celery@brain v3.1.23 (Cipater)
    ---- **** -----
    --- * ***  * -- Linux-3.16.0-4-amd64-x86_64-with-debian-8.2
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         scantasks:0x7fbd7ee4c350
    - ** ---------- .> transport:   amqp://brain:**@127.0.0.1:5672/mqbrain
    - ** ---------- .> results:     amqp://
    - *** --- * --- .> concurrency: 2 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> brain            exchange=celery(direct) key=brain


    [2016-07-15 15:00:36,155: WARNING/MainProcess] celery@brain ready.

This worker is responsible for splitting the whole scan job in multiples job
per probe per file.

.. code-block:: console

    $ cd /opt/irma/irma-brain/current
    $ ./venv/bin/python -m brain.results_tasks

     -------------- celery@brain v3.1.23 (Cipater)
    ---- **** -----
    --- * ***  * -- Linux-3.16.0-4-amd64-x86_64-with-debian-8.2
    -- * - **** ---
    - ** ---------- [config]
    - ** ---------- .> app:         resultstasks:0x7fa68f9aa590
    - ** ---------- .> transport:   amqp://probe:**@127.0.0.1:5672/mqprobe
    - ** ---------- .> results:     disabled://
    - *** --- * --- .> concurrency: 2 (prefork)
    -- ******* ----
    --- ***** ----- [queues]
     -------------- .> results          exchange=celery(direct) key=results

    [2016-07-15 14:59:01,799: WARNING/MainProcess] celery@brain ready.


And this worker is responsible for collecting and tracking results.

If your Celery worker does not output something similar to the above output,
you should check twice the parameters in the application configuration file you
are using.
