Running Frontend applications at startup
----------------------------------------

We have ensured that the freshly installed Frontend is ready to be integrated to
your IRMA platform. Now, we can go a step further and make it launch
automatically all daemons when the system starts up so you will not need to
relaunch them manually every time.

We are using systemd to manage our celery daemons. Systemd is enabled by
default in most of modern Linux distributions (Archlinux, Debian, Ubuntu, RHEL,
CentOS, etc.). If your distribution does not provide  systemd, brace yourself
and install it or manage your daemons in your own way.

We will create two new units called irma.frontend_app.service and
irma.frontend_api.service.

Configure Frontend APP
**********************


Create a file called ``irma.fontend_app.service`` located at
``/etc/systemd/system/`` with the following content:

.. code-block:: ini

    # /etc/systemd/system/irma.fontend_app.service
    [Service]
    ExecStart=/opt/irma/irma-frontend/current/venv/bin/python -m api.tasks.frontend_app
    User=irma
    WorkingDirectory=/opt/irma/irma-frontend/current
    ProtectSystem=full
    SyslogIdentifier=[irma.frontend]
    StandardOutput=syslog
    StandardError=syslog


Configure Frontend API
**********************

Create a file called ``irma.fontend_api.service`` located at
``/etc/systemd/system/`` with the following content:

.. code-block:: ini

    # /etc/systemd/system/irma.fontend_api.service
    [Service]
    ExecStart=/opt/irma/irma-frontend/current/venv/bin/uwsgi -s 127.0.0.1:8081 --disable-logging --master --workers 4 --need-app --chdir /opt/irma/irma-frontend/current --home /opt/irma/irma-frontend/current/venv
    User=irma
    ProtectSystem=full
    SyslogIdentifier=[irma.frontend.api]


Manage IRMA with systemd
************************

There are two ways to enable IRMA in systemd
 1. Make all IRMA services wanted by the already setup multi-user.target.
 2. Create a new target irma.target for IRMA units and ask your system to reach
    this target (performed by the automated installation).


Attach to multi-user.target
+++++++++++++++++++++++++++

Advertise every IRMA unit to attach to multi-user.target. Simply add the
following line to every IRMA unit file.

.. code-block:: ini

    # ...
    WantedBy=multi-user.target


Create irma.target
++++++++++++++++++

Create a new file ``/etc/systemd/system/irma.target`` containing

.. code-block:: ini

    # /etc/systemd/system/irma.target
    [Unit]
    Description=IRMA target
    Requires=multi-user.target
    After=multi-user.target

Then, link every IRMA service to the IRMA target. Finally reload the systemd
configuration and launch IRMA.

.. code-block:: console

    $ sudo mkdir /etc/systemd/system/irma.target.wants
    $ for unit in /etc/systemd/system/irma.*.service; do sudo ln -sf "$unit" /etc/systemd/system/irma.target.wants/"$unit"; done
    $ sudo systemctl set-default irma.target
    $ sudo systemctl daemon-reload
    $ sudo systemctl isolate irma.target
