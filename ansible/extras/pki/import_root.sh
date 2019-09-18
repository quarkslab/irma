#!/bin/bash
set -e
usage="$(basename "$0") [-h] -f pki_folder -c config -r root_cert -k root_key "

while getopts 'hf:c:r:k:' arg; do
    case "$arg" in
        h) echo "$usage"
           exit
           ;;
        f) PKI_FOLDER=$OPTARG
           ;;
        c) CONFIG=$OPTARG
	   ;;
        r) ROOT_CERT_SRC=$OPTARG
	   ;;
        k) ROOT_KEY_SRC=$OPTARG
	   ;;
        :) printf "missing argument for -%s\\n" "$OPTARG" >&2
           echo "$usage" >&2
           exit 1
           ;;
        \?) printf "illegal option: -%s\\n" "$OPTARG" >&2
            echo "$usage" >&2
            ;;
    esac
done
shift $((OPTIND -1))

if [[ -z $PKI_FOLDER || -z $CONFIG ]]
then
    echo "$usage"
    exit 1
fi

cd "$PKI_FOLDER"
PKI_FOLDER=$PWD

ROOT_DIR=$PKI_FOLDER/root
ROOT_KEY=$ROOT_DIR/root.key
ROOT_CSR=$ROOT_DIR/root.csr
ROOT_CERT=$ROOT_DIR/root.crt
ROOT_CONF=$ROOT_DIR/root.config

cd "$ROOT_DIR"
cp "$CONFIG" "$ROOT_CONF"
cp "$ROOT_KEY_SRC" "$ROOT_KEY"
cp "$ROOT_CERT_SRC" "$ROOT_CERT"
mkdir db
touch db/root.db
echo 02 > db/root.crt.srl
echo 01 > db/root.crl.srl
openssl ca -gencrl -config "$ROOT_CONF" -out root.crl
