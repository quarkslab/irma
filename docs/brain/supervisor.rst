Running Brain applications at startup
-------------------------------------

We have ensured that the freshly installed Brain is ready to be
integrated to your IRMA platform. Now, we can go a step further and make it launch automatically all daemons when the system starts up so you will not need to relaunch them manually every time.

We are using supervisor to manage our celery daemons.

Installing Supervisor
*********************

Install it with apt:


.. code-block:: bash

    $ sudo apt-get install python-virtualenv python-dev
    $ sudo pip install supervisor

We will create two new applications called scan_app and result_app.

Configure Scan APP
**********************


Create a file called ``scan_app`` located at ``/etc/supervisor/conf.d`` with the following content:


.. code-block:: bash

    [program:scan_app]

    numprocs = 1
    stopwaitsecs = 600
    killasgroup = True
    stderr_logfile = /var/log/supervisor/scan_app.log
    command = /opt/irma/irma-brain/current/venv/bin/celery worker -A brain.scan_tasks --hostname=scan_app.%%h --loglevel=INFO --without-gossip --without-mingle --without-heartbeat --soft-time-limit=60 --time-limit=300 -Ofair
    user = irma
    autostart = True
    directory = /opt/irma/irma-brain/current
    stdout_logfile = /var/log/supervisor/scan_app.log


Configure Result APP
********************

Create a file called ``result_app`` located at ``/etc/supervisor/conf.d`` with the following content:


.. code-block:: bash

    [program:result_app]

    numprocs = 1
    stopwaitsecs = 600
    killasgroup = True
    stderr_logfile = /var/log/supervisor/result_app.log
    command = /opt/irma/irma-brain/current/venv/bin/celery worker -A brain.results_tasks --concurrency=1 --hostname=result_app.%%h --loglevel=INFO --without-gossip --without-mingle --without-heartbeat --soft-time-limit=60 --time-limit=300
    user = irma
    autostart = True
    directory = /opt/irma/irma-brain/current
    stdout_logfile = /var/log/supervisor/result_app.log


Ensure supervisor will read our files by checking ``/etc/supervisor/supervisord.conf``  last lines should be:

.. code-block:: bash

    [...]
    [include]
    files = /etc/supervisor/conf.d/*


Restart supervisor:


.. code-block:: bash

    $ sudo service supervisor restart


Restart applications if needed (should be done automatically):

.. code-block:: bash

    $ sudo supervisorctl restart all
    scan_app: stopped
    result_app: stopped
    scan_app: started
    result_app: started
