#!/bin/bash
mkdir -p irma-ca/private irma-ca/db certs
chmod 700 irma-ca/private/
cp /dev/null irma-ca/db/irma-ca.db
cp /dev/null irma-ca/db/irma-ca.db.attr
echo 01 > irma-ca/db/irma-ca.crt.srl
echo 01 > irma-ca/db/irma-ca.crl.srl
openssl req -new -config irma-ca.config -out irma-ca.csr -keyout irma-ca/private/irma-ca.key
openssl ca -selfsign -config irma-ca.config -in irma-ca.csr -out irma-ca/irma-ca.crt -extensions root_ca_ext
openssl req -new -config client.config -out client.csr -keyout certs/client.key
openssl ca -config irma-ca.config -in client.csr -out certs/client.crt -extensions signing_ca_ext
openssl req -new -config server.config -out server.csr -keyout certs/server.key
openssl ca -config irma-ca.config -in server.csr -out certs/server.crt -extensions signing_ca_ext
rm *.csr
