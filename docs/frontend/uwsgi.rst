Installing and configuring uWSGI
--------------------------------

The restful API is served by an uWSGI application server. This section will
explain how to install an uWSGI server and configure it for the **Frontend**.

Installation
````````````

On Debian, installing uWSGI to serve a python application is pretty
straightforward:

.. code-block:: bash

    $ cd /opt/irma/irma-frontend/current
    $ ./venv/bin/pip install https://projects.unbit.it/downloads/uwsgi-lts.tar.gz
    [...]

Please refer to the documentation of your preferred distribution to install
an uWSGI server on it.
