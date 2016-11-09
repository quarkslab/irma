#!/bin/sh

HOSTFILE=/etc/hosts
HOSTFILE=/etc/hostname
BACKUP_SUFFIX=bak

# Check Parameters
if [ $# -ne 1 ]
then
  echo "Usage: sudo `basename $0` <New_Probe_Name>"
  exit 1
fi

set -u
echo "[+] Check rights"

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "[+] Modify hosts"
mv /etc/hosts /etc/hosts.$BACKUP_SUFFIX
cat <<EOF > /etc/hosts
127.0.0.1   localhost
127.0.1.1   $1

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

echo "[+] Modify hostname"
mv /etc/hostname /etc/hostname.$BACKUP_SUFFIX
cat <<EOF > /etc/hostname
$1
EOF

echo "Now reboot..."
