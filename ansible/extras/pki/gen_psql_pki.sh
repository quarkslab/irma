#!bin/bash
set -e
usage="$(basename "$0") [-h] -d pki_dir -c config_ca -s config_server -f config_frontend"

while getopts 'hd:c:s:f:' arg; do
    case "$arg" in
        h) echo "$usage"
           exit
           ;;
        d) PKI_FOLDER=$OPTARG
           ;;
        c) CONFIG_CA=$OPTARG
           ;;
        s) CONFIG_SERVER=$OPTARG
           ;;
        f)CONFIG_FRONTEND=$OPTARG
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

if [[ -z $PKI_FOLDER || -z $CONFIG_CA || -z $CONFIG_SERVER || -z $CONFIG_FRONTEND ]]
then
    echo "$usage"
    exit 1
fi
cd "$PKI_FOLDER"
PKI_FOLDER=$PWD

ROOT_DIR=$PKI_FOLDER/root
ROOT_CERT=$ROOT_DIR/root.crt
ROOT_CRL=$ROOT_DIR/root.crl
ROOT_CONF=$ROOT_DIR/root.config
PSQL_DIR=$PKI_FOLDER/psql
CA_DIR=$PSQL_DIR/ca
CA_KEY=$CA_DIR/ca.key
CA_CSR=$CA_DIR/ca.csr
CA_CERT=$CA_DIR/ca.crt
CA_CHAIN=$CA_DIR/ca-chain.crt
CA_CONF=$CA_DIR/ca.config
CA_DB=$CA_DIR/db
CRL=$CA_DIR/psql.crl
SRV_DIR=$PSQL_DIR/server
SRV_KEY=$SRV_DIR/server.key
SRV_CSR=$SRV_DIR/server.csr
SRV_CERT=$SRV_DIR/server.crt
SRV_CONF=$SRV_DIR/server.config
CLT_DIR=$PSQL_DIR/clients
FRT_KEY=$CLT_DIR/frontend.key
FRT_CSR=$CLT_DIR/frontend.csr
FRT_CERT=$CLT_DIR/frontend.crt
FRT_CONF=$CLT_DIR/frontend.config

cd "$ROOT_DIR"
cp "$CONFIG_CA" "$CA_CONF"
openssl req -new -config "$CA_CONF" -out "$CA_CSR" -keyout "$CA_KEY"
mkdir "$CA_DB"
touch "$CA_DB/ca.db"
echo 01 > "$CA_DB/ca.crt.srl"
openssl ca -config "$ROOT_CONF" -in  "$CA_CSR" -out "$CA_CERT" -extensions signing_ca_ext -batch
rm "$CA_CSR"
cd "$CA_DIR"
cat "$CA_CERT" "$ROOT_CERT" > "$CA_CHAIN"
cp "$CONFIG_SERVER" "$SRV_CONF"
openssl req -new -config "$SRV_CONF" -out "$SRV_CSR" -keyout "$SRV_KEY"
openssl ca -config "$CA_CONF" -in "$SRV_CSR" -out "$SRV_CERT" -extensions signing_ca_ext -batch
cp "$CONFIG_FRONTEND" "$FRT_CONF"
openssl req -new -config "$FRT_CONF" -out "$FRT_CSR" -keyout "$FRT_KEY"
openssl ca -config "$CA_CONF" -in "$FRT_CSR" -out "$FRT_CERT" -extensions signing_ca_ext -batch
echo 01 > "$CA_DB/ca.crl.srl"
openssl ca -gencrl -config "$CA_CONF" -out "$CRL"
cat "$ROOT_CRL" >> "$CRL"
rm "$SRV_CSR"
rm "$FRT_CSR"
