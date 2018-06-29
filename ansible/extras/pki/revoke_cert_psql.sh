#!bin/bash
set -e
usage="$(basename "$0") [-h] -f pki_folder -u user"

while getopts 'hf:u:' arg; do
    case "$arg" in
        h) echo "$usage"
           exit
           ;;
        f) PKI_FOLDER=$OPTARG
           ;;
        u) REV_USR=$OPTARG
           ;;
        :) printf "missing argument for -%s\\n" "$OPTARG" >&2
           echo "$usage" >&2
           exit 1
           ;;
        \?) printf "illegal option: -%s\\n", "$OPTARG" >&2
            echo "$usage" >&2
            ;;
    esac
done
shift $((OPTIND -1))

if [[ -z $PKI_FOLDER || -z $REV_CRT ]]
then
    echo "$usage"
    exit 1
fi

cd "$PKI_FOLDER"
PKI_FOLDER=$PWD

PSQL_DIR=$PKI_FOLDER/psql
CA_CONF=$PSQL_DIR/ca/ca.config
ROOT_CRL=$PKI_FOLDER/root/root.crl
CRL=$PSQL_DIR/ca/psql.crl
USR_PATH=$PSQL_DIR/clients/$REV_USR
USR_CONFIG=$USR_PATH.config
USR_CSR=$USR_PATH.csr
USR_CERT=$USR_PATH.crt
USR_KEY=$USR_PATH.key
REVOKED_DIR=$PSQL_DIR/clients/revoked
CA_DIR=$PKI_FOLDER/psql/ca

cd "$CA_DIR"
openssl ca -config "$CA_CONF" -revoke "$USR_PATH.crt"
openssl ca -config "$CA_CONF" -gencrl -out "$CRL"
cat "$ROOT_CRL" >> "$CRL"
mv "$USR_CERT" "$REVOKED_DIR"
mv "$USR_KEY" "$REVOKED_DIR"
openssl req -new -config "$USR_CONFIG" -out "$USR_CSR" -keyout "$USR_KEY"
openssl ca -config "$CA_CONF" -in "$USR_CSR" -out "$USR_CERT" -extensions signing_ca_ext -batch
