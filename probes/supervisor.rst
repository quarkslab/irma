Running Probe applications at startup
-------------------------------------

We have ensured that the freshly installed Probe is ready to be
integrated to your IRMA platform. Now, we can go a step further and make it launch automatically all daemons when the system starts up so you will not need to relaunch them manually every time.

We are using supervisor to manage our python celery worker.

Installing Supervisor
*********************

Install it with apt:

    $ sudo apt-get install python-virtualenv python-dev
    $ sudo pip install supervisor

We will create one new application called probe_app.

Configure Probe APP
*******************


Create a file called ``probe_app`` located at ``/etc/supervisor/conf.d`` with the following content:


.. code-block:: bash

    [program:probe_app]

    numprocs = 1
    stopwaitsecs = 600
    killasgroup = True
    stderr_logfile = /var/log/supervisor/probe_app.log
    command = /opt/irma/irma-probe/venv/bin/celery worker -A probe.tasks:probe_app --hostname=probe_app.%%h --loglevel=INFO --without-gossip --without-mingle --without-heartbeat --soft-time-limit=60 --time-limit=300
    user = irma
    autostart = True
    directory = /opt/irma/irma-probe
    stdout_logfile = /var/log/supervisor/probe_app.log


Ensure supervisor will read our files by checking ``/etc/supervisor/supervisord.conf``  last lines should be:

.. code-block:: bash

    [...]
    [include]
    files = /etc/supervisor/conf.d/*


Restart supervisor:

    $ sudo service supervisor restart

Restart applications if needed (should be done automatically):

    $ sudo supervisorctl restart all
    probe_app: stopped
    probe_app: started
