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
