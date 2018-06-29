#!bin/bash
set -e
usage="$(basename "$0") [-h] -f pki_folder -c config "

while getopts 'hf:c:' arg; do
    case "$arg" in
        h) echo "$usage"
           exit
           ;;
        f) PKI_FOLDER=$OPTARG
           ;;
        c) CONFIG=$OPTARG
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
openssl req -new -config  "$ROOT_CONF" -out "$ROOT_CSR" -keyout "$ROOT_KEY"
mkdir db
touch db/root.db
echo 01 > db/root.crt.srl
openssl ca  -selfsign -config "$ROOT_CONF" -in "$ROOT_CSR" -out "$ROOT_CERT" -extensions root_ca_ext -batch
echo 01 > db/root.crl.srl
openssl ca -gencrl -config "$ROOT_CONF" -out root.crl
rm "$ROOT_CSR"
