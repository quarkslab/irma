Installing and configuring nginx
--------------------------------

In the **Frontend**, we use a nginx web server to serve the uWSGI application
and the static web site that query the API in order to get results of scanned
files and present them to the user.

Installation
````````````

On Debian, installing nginx is done with few commands:

.. code-block:: bash

    $ sudo apt-get install nginx
    [...]

Please refer to the documentation of your preferred distribution to install
a uwsgi server on it.

Configuration
`````````````

We provide several template scripts in the ``extras/`` repository located at the
root of the installation directory. Templates for nginx are located in
``extras/nginx/``. Copy the file to ``sites-available`` in nginx folder:

.. code-block:: bash

    $ sudo cp extras/nginx/frontend /etc/nginx/sites-available/


The template is configured for a default installation of the frontend in
``/opt/irma/irma-frontend/``. You may need to edit it for you setup. In
particular, please ensure that the ``root`` directive points to the folder
``web/dist`` (for a production ready version of the web site) or ``web/app``
(for a development version of the web site) in your installation directory.

Activate the web site
`````````````````````

By default, all websites in ``apps-available`` are not activated. One can
enable the website described in ``frontend`` configuration file by creating a
soft-link into the ``sites-enabled`` folder:

.. code-block:: bash

    $ sudo ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/frontend

.. TODO: update the commands for HTTPs
.. note:: The case of HTTPs

    A template to set up a HTTPs server with nginx is also provided in the
    ``extras/nginx`` folder. Here is the way to setup it:

    .. code-block:: bash

        $ sudo cp extras/nginx/frontend-https /etc/nginx/sites-available/
        $ sudo ln -s /etc/nginx/sites-available/frontend-https /etc/nginx/sites-enabled/frontend-https
        $ sudo mkdir /etc/nginx/certificates/
        $ cd /etc/nginx/certificates/

    Generate the required Diffie Hellman Ephemeral Parameters:

    .. code-block:: bash

        $ sudo openssl dhparam -out dhparam.pem 4096
    
    Finally, generate a self signed certificate:

    .. code-block:: bash

        $ sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 -subj "/CN=$(hostname --fqdn)/" -keyout frontend.key -out frontend.crt


Relaunch the service
````````````````````

The final step is to relaunch the service:

.. code-block:: bash

    $ sudo invoke-rc.d nginx restart
