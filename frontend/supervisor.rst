Running Frontend applications at startup
----------------------------------------

We have ensured that the freshly installed Frontend is ready to be
integrated to your IRMA platform. Now, we can go a step further and make it launch automatically all daemons when the system starts up so you will not need to relaunch them manually every time.

We are using supervisor to manage our python daemons (uswgi for IRMA API and celery for IRMA frontend workers).

Installing Supervisor
*********************

Install it with apt:


.. code-block:: bash

    $ sudo apt-get install python-virtualenv python-dev
    $ sudo pip install supervisor

We will create two new applications called frontend_api and frontend_app.
Frontend_api is the python uwsgi server and frontend_app the frontend celery daemon.

Configure Frontend API
**********************


Create a file called ``frontend_api`` located at ``/etc/supervisor/conf.d`` with the following content:


.. code-block:: bash

    [program:frontend_api]

    numprocs = 1
    redirect_stderr = True
    stopwaitsecs = 600
    killasgroup = True
    stderr_logfile = /var/log/supervisor/frontend_api.log
    stopsignal = INT
    command = uwsgi -s 127.0.0.1:8081 --disable-logging --master --workers 4 --need-app --plugins python --chdir /opt/irma/irma-frontend --home /opt/irma/irma-frontend/venv --python-path /opt/irma/irma-frontend/venv --mount /api=frontend/api/base.py --lazy

    user = irma
    autostart = True
    stdout_logfile = /var/log/supervisor/frontend_api.log

Configure Frontend APP
**********************

Create a file called ``frontend_app`` located at ``/etc/supervisor/conf.d`` with the following content:


.. code-block:: bash

    [program:frontend_app]

    numprocs = 1
    stopwaitsecs = 600
    killasgroup = True
    stderr_logfile = /var/log/supervisor/frontend_app.log
    command = /opt/irma/irma-frontend/venv/bin/celery worker -A frontend.tasks:frontend_app --hostname=frontend_app.%%h --loglevel=INFO --without-gossip --without-mingle --without-heartbeat --soft-time-limit=60 --time-limit=300 --beat --schedule=/var/irma/frontend_beat_schedule
    user = irma
    autostart = True
    directory = /opt/irma/irma-frontend
    stdout_logfile = /var/log/supervisor/frontend_app.log

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
    frontend_api: stopped
    frontend_app: stopped
    frontend_app: started
    frontend_api: started
