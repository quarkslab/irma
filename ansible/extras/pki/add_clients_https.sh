#!bin/bash
set -e
usage="$(basename "$0") [-h] -f pki_folder -c config -u username"

while getopts 'hf:c:u:' arg; do
    case "$arg" in
        h) echo "$usage"
           exit
           ;;
        f) PKI_FOLDER=$OPTARG
           ;;
        c) CONFIG_FOLDER=$OPTARG
           ;;
        u) USER=$OPTARG
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

if [[ -z $PKI_FOLDER || -z $CONFIG_FOLDER ]]
then
    echo "$usage"
    exit 1
fi
cd "$PKI_FOLDER"
PKI_FOLDER=$PWD

HTTPS_DIR=$PKI_FOLDER/https
CA_DIR=$HTTPS_DIR/ca
CA_CONF=$HTTPS_DIR/ca/ca.config
CA_CHAIN=$CA_DIR/ca-chain.crt
CLT_DIR=$HTTPS_DIR/clients
USER_KEY=$CLT_DIR/$USER.key
USER_CSR=$CLT_DIR/$USER.csr
USER_CERT=$CLT_DIR/$USER.crt
USER_CHAIN=$CLT_DIR/$USER-chain.crt
USER_CONF=$CLT_DIR/$USER.config

cd "$CA_DIR"
cp "$CONFIG_FOLDER/$USER.config" "$USER_CONF"
openssl req -new -config "$USER_CONF" -out "$USER_CSR" -keyout "$USER_KEY"
openssl ca -config "$CA_CONF" -in "$USER_CSR" -out "$USER_CERT" -extensions signing_ca_ext -batch
cat "$USER_CERT" "$CA_CHAIN" > "$USER_CHAIN"
rm "$USER_CSR"
