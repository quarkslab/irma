#!bin/bash
usage="$(basename "$0") [-h] -c config -u user  --create a new user according to a config
where:
    -h         show this help text
    -c config  set the openssl config file for the new user
    -u user    set the user name"

while getopts 'c:u:' arg; do
  case "$arg" in
    h) echo "$usage"
       exit
       ;;
    c) config=$OPTARG
       ;;
    u) user=$OPTARG
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
  esac
done
shift $(($OPTIND - 1))

if ["$config" == ""]||["$user" == ""]
then
    echo "$usage"
    exit 1
fi

openssl req -new -config $config -out $user.csr -keyout certs/$user.key
openssl ca -config irma-ca.config -in $user.csr -out certs/$user.crt -extensions signing_ca_ext
rm $user.csr
