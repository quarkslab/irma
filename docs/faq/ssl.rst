SSL settings
------------

SSL is available for 3 services:

* for an https connection with a nginx configuration;
* for RabbitMQ;
* for PostgreSQL with an authentication by certificate.

Enabling SSL for at least one of these services, generates a PKI made of a root CA and, for each mechanism, an intermediate CA and some other stuff.
Every CA and https certificate requires an openssl configuration file. These files are set in the appropriate directory in ``./extras/pki/conf``: ``root.config`` at the root, a ``<service>/ca.config`` in the ``https``, ``rabbitmq`` and  ``psql`` directories and configuration file corresponding to https clients in ``https`` directory. During the generation the configuration files will be copied in the corresponding directory.


The PKI is generated in the infra directory ``./infras/<infra-name>/pki`` where ``<infra-name>`` is set with ``infra_name`` in ``group_vars/all.yml`` (defaults to "Qb"). The PKI is described in ``infras/<infra-name>/<infra-name>-infra.yml``. During the provisioning, ansible updates the PKI (or creates it) according to this file. To erase the PKI, delete the infra directory first.

HTTPS
*****

Enable HTTPS
++++++++++++

To enable SSL on the frontend server, edit ``group_vars/all.yml`` with:

.. code-block:: yaml

    frontend_openssl: True
    nginx_https_enabled: True  # require frontend_openssl
    nginx_https_client_enabled: True  # require nginx_https_enabled

.. note::

    HTTPS and HTTP connections can operate at the same time.

.. note::

    ``nginx_https_enabled`` [required] activates the server's certificate verification.
    ``nginx_https_client_enabled`` [optional] activates the client's certificate verification.


Generate certificates
^^^^^^^^^^^^^^^^^^^^^

The crypto objects for an https connection are generated in ``infras/<infra-name>/pki/https``. By default, these are:

* a CA (key, certificate, chained certificate, database and CRL);
* a server (key, certificate, chained certificate);
* a client (key, certificate, chained certificate).


.. code-block:: console

    $ tree infras/Qb/pki/https
    infras/Qb/pki/https/
    ├── ca
    │   ├── 01.pem
    │   ├── 02.pem
    │   ├── ca-chain.crt
    │   ├── ca.config
    │   ├── ca.crt
    │   ├── ca.key
    │   ├── db
    │   │   ├── ca.crl.srl
    │   │   ├── ca.crl.srl.old
    │   │   ├── ca.crt.srl
    │   │   ├── ca.crt.srl.old
    │   │   ├── ca.db
    │   │   ├── ca.db.attr
    │   │   ├── ca.db.attr.old
    │   │   └── ca.db.old
    │   └── https.crl
    ├── clients
    │   ├── client-chain.crt
    │   ├── client.config
    │   ├── client.crt
    │   ├── client.key
    │   └── revoked
    └── server
        ├── server-chain.crt
        ├── server.config
        ├── server.crt
        └── server.key

Add a client
++++++++++++

To add a client:

* edit ``infras/<infra-name>/<infra-name>-infra.yml>`` with:

  .. code-block:: yaml

      ---

      infra:
        name: Qb
        https:
          clients:
            running:
              - name: client
              - name: new_client #there we indicate a the name of the new user
            revoked: []

* add an openssl configuration file ``./extras/pki/conf/https/<client-name>.config`` corresponding to the new user.
* provision with ansible: it copies the previous file in clients directory.

Revoke a client
+++++++++++++++

To revoke a client:

* edit ``infras/<infra-name>/<infra-name>-infra.yml>`` with:

  .. code-block:: yaml

      ---

      infra:
        name: Qb

        clients:
          running:
            - name: client
          revoked:
            - name: bad_user # the user is now in revoked list and not in running list

* provision with ansible: it revokes the user with the user's CA and moves its stuff in ``clients/revoked/``.

RabbitMQ
********

Enable SSL on RabbitMq
++++++++++++++++++++++

To enable SSL in RabbitMq, edit ``group_vars/brain.yml`` with:

.. code-block:: yaml

    rabbitmq_ssl: True

.. note::

    If you are updating an already running no_ssl version,
    do the following on irma-brain RabbitMQ server:

    .. code-block:: console

        $ sudo rabbitmqctl stop_app
        $ sudo rabbitmqctl reset
        $ sudo rabbitmqctl start_app
        # create again the RabbitMQ vhosts, usernames and passwords:
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh probe probe mqprobe
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh brain brain mqbrain
        $ sudo ./extras/scripts/rabbitmq/rmq_adduser.sh frontend frontend mqfrontend

Certificates generation
+++++++++++++++++++++++

The crypto objects for RabbitMq with SSl are generated in ``infras/<infra-name>/pki/rabbitmq``. These are:

* a CA (key, certificate, chained certificate and database);
* a server brain (key, certificate);
* 3 clients for the entity frontend, brain and probe (key, certificate).

.. code-block:: console

    $ tree infras/Qb/pki/rabbitmq
    infras/Qb/pki/rabbitmq/
    ├── ca
    │   ├── 01.pem
    │   ├── 02.pem
    │   ├── 03.pem
    │   ├── 04.pem
    │   ├── ca-chain.crt
    │   ├── ca.config
    │   ├── ca.crt
    │   ├── ca.key
    │   └── db
    │       ├── ca.crt.srl
    │       ├── ca.crt.srl.old
    │       ├── ca.db
    │       ├── ca.db.attr
    │       ├── ca.db.attr.old
    │       └── ca.db.old
    ├── clients
    │   ├── brain-client.crt
    │   ├── brain-client.key
    │   ├── frontend-client.crt
    │   ├── frontend-client.key
    │   ├── probe-client.crt
    │   └── probe-client.key
    └── server
        ├── brain.crt
        └── brain.key

.. note::

   In RabbitMq case, only the CA needs a openssl configuration file.


Postgresql
**********

Enable SSL on Postgresql
++++++++++++++++++++++++

To activate SSL in Postgresql service, edit ``group_vars/brain.yml`` with:

.. code-block:: yaml

    postgresql_ssl: True


Generate certificates
+++++++++++++++++++++

The crypto objects for RabbitMq with SSl are generated in ``infras/<infra-name>/pki/rabbitmq``. These are:

* a CA (key, certificate, chained certificate, a CRL and database);
* a server (key, certificate);
* a client frontend (key, certificate).

.. code-block:: console

    $ tree infras/Qb/pki/psql
    infras/Qb/pki/psql/
    ├── ca
    │   ├── 01.pem
    │   ├── 02.pem
    │   ├── ca-chain.crt
    │   ├── ca.config
    │   ├── ca.crt
    │   ├── ca.key
    │   ├── db
    │   │   ├── ca.crl.srl
    │   │   ├── ca.crl.srl.old
    │   │   ├── ca.crt.srl
    │   │   ├── ca.crt.srl.old
    │   │   ├── ca.db
    │   │   ├── ca.db.attr
    │   │   ├── ca.db.attr.old
    │   │   └── ca.db.old
    │   └── psql.crl
    ├── clients
    │   ├── frontend.config
    │   ├── frontend.crt
    │   ├── frontend.key
    │   └── revoked
    └── server
        ├── server.config
        ├── server.crt
        └── server.key


Revoke a client
+++++++++++++++

To revoke a client:

* edit ``infras/<infra-name>/<infra-name>-infra.yml>`` with:

  .. code-block:: yaml

      ---

      infra:
        name: Qb

        psql:
          clients:
            revoked:
              - name: bad_user # bad_user is now in revoked list and no longer in running list


* provision with ansible: it revokes the user with the user's CA and moves its stuff in ``clients/revoked/``.
