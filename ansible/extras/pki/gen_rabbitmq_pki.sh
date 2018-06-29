#!bin/bash
set -e
usage="$(basename "$0") [-h] -f pki_folder -c config_ca"

while getopts 'hf:c:' arg; do
    case "$arg" in
        h) echo "$usage"
           exit
           ;;
        f) PKI_FOLDER=$OPTARG
           ;;
        c) CONFIG_CA=$OPTARG
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
shift $((OPTIND-1))

if [[ -z $PKI_FOLDER || -z $CONFIG_CA ]]
then
    echo "$usage"
    exit 1
fi

cd "$PKI_FOLDER"
PKI_FOLDER=$PWD

ROOT_DIR=$PKI_FOLDER/root
ROOT_CERT=$ROOT_DIR/root.crt
ROOT_CONF=$ROOT_DIR/root.config
RABBITMQ_DIR=$PKI_FOLDER/rabbitmq
CA_DIR=$RABBITMQ_DIR/ca
CA_KEY=$CA_DIR/ca.key
CA_CSR=$CA_DIR/ca.csr
CA_CERT=$CA_DIR/ca.crt
CA_CHAIN=$CA_DIR/ca-chain.crt
CA_CONF=$CA_DIR/ca.config
CA_DB=$CA_DIR/db
SRV_DIR=$RABBITMQ_DIR/server
SRV_KEY=$SRV_DIR/brain.key
SRV_CSR=$SRV_DIR/brain.csr
SRV_CERT=$SRV_DIR/brain.crt
CLT_DIR=$RABBITMQ_DIR/clients
BRAIN_KEY=$CLT_DIR/brain-client.key
BRAIN_CSR=$CLT_DIR/brain-client.csr
BRAIN_CERT=$CLT_DIR/brain-client.crt
FRT_KEY=$CLT_DIR/frontend-client.key
FRT_CSR=$CLT_DIR/frontend-client.csr
FRT_CERT=$CLT_DIR/frontend-client.crt
PRB_KEY=$CLT_DIR/probe-client.key
PRB_CSR=$CLT_DIR/probe-client.csr
PRB_CERT=$CLT_DIR/probe-client.crt

cd "$ROOT_DIR"
cp "$CONFIG_CA" "$CA_CONF"
openssl req -new -config "$CA_CONF" -out "$CA_CSR" -keyout "$CA_KEY"
mkdir "$CA_DB"
touch "$CA_DB/ca.db"
echo 01 > "$CA_DB/ca.crt.srl"
openssl ca -config "$ROOT_CONF" -in "$CA_CSR" -out "$CA_CERT" -extensions signing_ca_ext -batch
rm "$CA_CSR"
cd "$CA_DIR"
cat "$CA_CERT" "$ROOT_CERT" > "$CA_CHAIN"
openssl req -new -subj "/nsCertType=SERVER/CN=brain/C=FR/O=Quarkslab/" -out "$SRV_CSR" -keyout "$SRV_KEY" -nodes -batch
openssl ca -config "$CA_CONF" -in "$SRV_CSR" -out "$SRV_CERT" -days 365 -extensions signing_ca_ext -batch
rm "$SRV_CSR"
openssl req -new -subj "/CN=brain-client/C=FR/O=Quarkslab/" -out "$BRAIN_CSR" -keyout "$BRAIN_KEY" -nodes -batch
openssl ca -config "$CA_CONF" -in "$BRAIN_CSR" -out "$BRAIN_CERT" -days 365 -extensions signing_ca_ext -batch
rm "$BRAIN_CSR"
openssl req -new -subj "/CN=frontend-client/C=FR/O=Quarkslab/" -out "$FRT_CSR" -keyout "$FRT_KEY" -nodes -batch
openssl  ca -config "$CA_CONF" -in "$FRT_CSR" -out "$FRT_CERT" -days 365 -extensions signing_ca_ext -batch
rm "$FRT_CSR"
openssl req -new -subj "/CN=probe-client/C=FR/O=Quarkslab/" -out "$PRB_CSR" -keyout "$PRB_KEY" -nodes -batch
openssl ca -config "$CA_CONF" -in "$PRB_CSR" -out "$PRB_CERT" -days 365 -extensions signing_ca_ext -batch
rm "$PRB_CSR"
