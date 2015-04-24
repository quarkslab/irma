#!/bin/sh

# /!\ Check ftpuser/ftpgroup is set
#--------
# ftpuser
#--------
# groupadd ftpgroup
# useradd -g ftpgroup -d /dev/null -s /etc ftpuser
#
#---------
# ftpdconf
#---------
# echo "yes" > /etc/pure-ftpd/conf/CreateHomeDir
# echo "no" > /etc/pure-ftpd/conf/PAMAuthentication
# echo "2" > /etc/pure-ftpd/conf/TLS
# ln -s ../conf/PureDB /etc/pure-ftpd/auth/50puredb
#
#-------
# Certs
#-------
# mkdir -p /etc/ssl/private/
# openssl req -x509 -nodes -days 7300 -newkey rsa:2048 -keyout /etc/ssl/private/pure-ftpd.pem -out /etc/ssl/private/pure-ftpd.pem
# chmod 600 /etc/ssl/private/pure-ftpd.pem

# Check Parameters
if [ $# -ne 3 ]
then
  echo "Usage: sudo `basename $0` <user> <virtualuser> <chroot home>"
  exit 1
fi

set -u
echo "[+] Check rights"

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


USER=$1
VUSER=$2
VHOME=$3
echo "[+] Create user $USER"
pure-pw useradd $USER -u $VUSER -d $VHOME
echo "[+] Enable new user in conf"
pure-pw mkdb
