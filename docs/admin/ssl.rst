SSL settings
------------

SSL is available for 5 services:

* for an https connection with an nginx configuration;
* for RabbitMQ;
* for PostgreSQL with an authentication by certificate;

In the nominal case, enabling SSL for at least one of these services generates a PKI made of a root CA and, for each mechanism, an intermediate CA and some other stuff.
Every CA and https certificate requires an openssl configuration file. These files are set in the appropriate directory in ``./extras/pki/conf``: ``root.config`` at the root, a ``<service>/ca.config`` in the ``https``, ``rabbitmq`` and  ``psql`` directories and configuration file corresponding to https clients in ``https`` directory. The configuration files are copied in the corresponding directories during their generation.


The PKI is generated in the infra directory ``./infras/<infra-name>/pki`` where ``<infra-name>`` is the ansible variable ``infra_name`` in ``group_vars/all.yml`` (defaults to "Qb"). The PKI is described in ``infras/<infra-name>/<infra-name>-infra.yml``. During the provisioning, ansible updates the PKI (or creates it) according to this file. To erase the PKI, delete the infra directory first.

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

* edit ``infras/<infra-name>/<infra-name>-infra.yml`` with:

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

* edit ``infras/<infra-name>/<infra-name>-infra.yml`` with:

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

Enable SSL on RabbitMQ
++++++++++++++++++++++

To enable SSL in RabbitMQ, edit ``group_vars/brain.yml`` with:

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

The crypto objects for RabbitMQ with SSL are generated in ``infras/<infra-name>/pki/rabbitmq``. These are:

* a CA (key, certificate, chained certificate and database);
* a server brain (key, certificate);
* 3 clients for the entities frontend, brain and probe (key, certificate).

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

   In RabbitMQ case, only the CA needs a openssl configuration file.


Postgresql
**********

Enable SSL on Postgresql
++++++++++++++++++++++++

To activate SSL in PostgreSQL service, edit ``group_vars/brain.yml`` with:

.. code-block:: yaml

    postgresql_ssl: True


Generate certificates
+++++++++++++++++++++

The crypto objects for PostgreSQL with SSL are generated in ``infras/<infra-name>/pki/psql``. These are:

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

* edit ``infras/<infra-name>/<infra-name>-infra.yml`` with:

  .. code-block:: yaml

      ---

      infra:
        name: Qb

        psql:
          clients:
            revoked:
              - name: bad_user # bad_user is now in revoked list and no longer in running list


* provision with ansible: it revokes the user with the user's CA and moves its stuff in ``clients/revoked/``.


External PKI
************

It is also possible to use an external PKI for one or more of these services, for the root entity or the whole Irma's PKI. In this case, it is necessary to provide the corresponding cryptographic objects in PEM format.
To specify which PKI's part are provided by an external PKI, edit ``group_vars/all.yml`` :

.. code-block:: yaml

    root_external: False
    pki_rabbitmq_external: False
    pki_https_external: False
    pki_psql_external: False

By default, the automatic generation of the whole PKI is activated and all variables for external PKI are set to False.


External root
+++++++++++++

To use a external root, edit ``group_vars/all.yml`` with:

.. code-block:: yaml

    root_external: True
    root_external_key: root_key.key
    root_external_cert: root_cert.crt

.. note::

    ``root_key.key`` and ``root_external_cert`` must contain the paths to respectively the key and the certificate of the external root entity.

The Irma's PKI will be generated with this external root as authority.


External HTTPS PKI
++++++++++++++++++

To use an external PKI for HTTPS and disable the automatic generation of a new one, edit ``group_vars/all.yml`` with:

.. code-block:: yaml

    pki_https_external: True

Provide the cryptographic objects and specify the paths editing ``group_vars/frontend.yml``:

.. code-block:: yaml

    frontend_openssl_certificates:
      cert:
       src: https_server.crt
       dst: /etc/nginx/certs/{{ hostname }}.crt
      key:
       src: https_server.key
       dst: /etc/nginx/certs/{{ hostname }}.key
      ca:
       src: https_ca_cert.crt
       dst: /etc/nginx/certs/ca.crt
      chain:
       src: https_ca_chain.crt
       dst: /etc/nginx/certs/ca-chain.crt
      crl:
       src: https_crl.crl
       dst: /etc/nginx/certs/https.crl

.. note::

    ``frontend_openssl_certificates.cert.src`` is the path to the server's certificate
    ``frontend_openssl_certificates.key.src`` is the path to the server's private key
    ``frontend_openssl_certificates.ca.src`` is the path to the CA's certificate
    ``frontend_openssl_certificates.chain.src`` is the path to the CA's certification chain
    ``frontend_openssl_certificates.crl.src`` is the path to the CRL


External RabbitMQ PKI
+++++++++++++++++++++

To use an external PKI for RabbitMQ and disable the automatic generation of a new one, edit ``group_vars/all.yml`` with:

.. code-block:: yaml

    pki_rabbitmq_external: True

Provide the cryptographic objects and specify the paths editing ``group_vars/all.yml``:

.. code-block:: yaml

    rabbitmq_cacert : ca-chain.crt
    rabbitmq_server_key : server.key
    rabbitmq_server_cert: server.crt
    rabbitmq_frontend_key: frontend-client.key
    rabbitmq_frontend_cert: frontend-client.crt
    rabbitmq_brain_key: brain-client.key
    rabbitmq_brain_cert: brain-client.crt
    rabbitmq_probe_key: probe-client.key
    rabbitmq_probe_cert: probe-client.crt

.. note::

    ``rabbitmq_cacert`` is the path to the CA's certification chain
    ``rabbitmq_server_key`` is the path to the server's private key
    ``rabbitmq_server_cert`` is the path to the server's certificate
    ``rabbitmq_frontend_key`` is the path to the frontend's private key
    ``rabbitmq_fontend_cert`` is the path to the frontend's certificate
    ``rabbitmq_brain_key`` is the path to the brain's private key
    ``rabbitmq_brain_cert`` is the path to the brain's certificate
    ``rabbitmq_probe_key`` is the path to the probes' private key
    ``rabbitmq_probe_cert`` is the path to the probes' certificate


External PostgreSQL PKI
+++++++++++++++++++++++

To use an external PKI for PostgreSQL and disable the automatic generation of a new one, edit ``group_vars/all.yml`` with:

.. code-block:: yaml

    pki_psql_external: True

Provide the cryptographic objects and specify the paths editing ``group_vars/sql-server.yml``:

.. code-block:: yaml

    postgresql_ssl_cert_src_path: server.crt
    postgresql_ssl_key_src_path: server.key
    postgresql_ssl_ca_src_path: ca-chain.crt
    postgresql_ssl_crl_src_path: psql.crl

.. note::

    ``postgresql_ssl_cert_src_path`` is the path to the server's certificate
    ``postgresql_ssl_key_src_path`` is the path to the server's private key
    ``postgresql_ssl_ca_src_path`` is the path to the CA's certificate chain
    ``postgresql_ssl_crl_src_path`` is the path to the CRL
