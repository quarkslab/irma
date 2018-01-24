PKI Management Scripts
======================
The script creation.sh create a new pki (a pair certificate-key for the CA, the client and the server), according to the config files irma-ca.config (for the CA), client.config (for the client) and server.config (for the server).

To create a new PKI :

.. code-block:: bash

   bash creation.sh

The script will ask confirmation for the different certificates, confirm if it's good.

Then the cryptographic objects of CA (are generated in the directory irma-ca : the certificate is irma-ca.crt and the private key are stocked in private/irma-ca.key. The others objects are created in the directory certs.

To add a new user in the PKI, use the script add.sh :

.. code-block:: bash

   bash add.sh -c config -u user

where user is the string used to name the cryptographics objects and config is the openssl config file for the new user. You can use the config file client.config for a new client.

As in the creation step, the new objects are generated in the directory certs.
