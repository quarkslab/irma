Installing MongoDB server
-------------------------

The Frontend relies on a MongoDB to store the results of all files scanned.
On Debian, one can install a mongodb server in few commands:

.. code-block:: bash

    $ sudo apt-get install mongodb-server
    [...]

Please refer to the documentation of your preferred distribution to install
a mongodb server on it.

.. note:: Make it listen only on loopback

    Edit ``/etc/mongodb.conf`` to listen only on loopback interface. You should
    have the following configuration:

    .. code-block:: none
    
        bind_ip 127.0.0.1
        port = 27017
