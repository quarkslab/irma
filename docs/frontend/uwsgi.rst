Installing and configuring uWSGI
--------------------------------

The restful API is served by an uWSGI application server. This section will
explain how to install an uWSGI server and configure it for the **Frontend**.

Installation
````````````

On Debian, installing uWSGI to serve a python application is pretty
straightforward:

.. code-block:: bash

    $ sudo apt-get install uwsgi uwsgi-plugin-python
    [...]

Please refer to the documentation of your preferred distribution to install
an uWSGI server on it.

Configuration
`````````````

We provide several template scripts in the ``extras/`` repository located at the
root of the installation directory. Templates for uWSGI are located in
``extras/uwsgi/``. Copy the file to uWSGI ``app-available`` folder.

.. code-block:: bash

    $ sudo cp extras/uwsgi/frontend-api.xml /etc/uwsgi/apps-available/
    $ sudo vi /etc/uwsgi/apps-available/frontend-api.xml
    [...]

The template is configured for a default installation of the frontend in
``/opt/irma/irma-frontend``. You may need to edit it for you setup. In
particular, please ensure that the ``<chdir>`` tag points to your installation
directory.

.. literalinclude:: ../../extras/uwsgi/frontend-api.xml

Activate the application
````````````````````````

By default, all application in ``apps-available`` are not activated. One can
enable the application ``frontend-api.xml`` by creating a soft-link into the
``apps-enabled`` folder:

.. code-block:: bash

    $ sudo ln -s /etc/uwsgi/apps-available/frontend-api.xml /etc/uwsgi/apps-enabled/frontend-api.xml

Relaunch the service
````````````````````

The final step is to relaunch the service:

.. code-block:: bash

    $ sudo invoke-rc.d uwsgi restart
