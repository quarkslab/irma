#!/bin/sh

# Check Parameters
if [ $# -ne 3 ]
then
  echo "Usage: sudo `basename $0` <user> <password> <vhost>"
  exit 1
fi

set -u
echo "[+] Check rights"

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

USER=$1
PASSWD=$2
VHOST=$3
echo "[+] Create user $USER"
rabbitmqctl add_user $USER $PASSWD
echo "[+] Create vhost $VHOST"
rabbitmqctl add_vhost $VHOST
rabbitmqctl set_permissions -p $VHOST $USER ".*" ".*" ".*"
