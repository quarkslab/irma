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

ROOT_CRT=$PKI_FOLDER/root/root.crt
HTTPS_DIR=$PKI_FOLDER/https
CA_CONF=$HTTPS_DIR/ca/ca.config
CRL=$HTTPS_DIR/ca/https.crl
USR_PATH=$HTTPS_DIR/clients/$REV_USR
REVOKED_DIR=$HTTPS_DIR/clients/revoked
CA_DIR=$PKI_FOLDER/https/ca

cd "$CA_DIR"
openssl ca -config "$CA_CONF" -revoke "$USR_PATH.crt"
openssl ca -config "$CA_CONF" -gencrl -out "$CRL"
cat "$CA_CERT" "$ROOT_CRT" >> "$CRL"
mv "$USR_PATH.*" "$REVOKED_DIR"
