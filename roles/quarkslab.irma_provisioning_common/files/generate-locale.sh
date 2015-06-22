#!/bin/sh -e
#
# This script tries to solve a locale issue when connecting via SSH: the SSH
# client will often forward a locale that may not be available on the box. We
# check for an entry and install it in real time if not installed.
#

LOCALEVARS="LANG LC_ALL LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION"

for ENTRY in ${LOCALEVARS};
do
    LOCALE=$(eval echo \$$ENTRY)
    if [ ! -z ${LOCALE} ]
    then
        if grep -q "# ${LOCALE}" /etc/locale.gen
        then
            sudo sed -e "s/# ${LOCALE}/${LOCALE}/" -i /etc/locale.gen
            sudo /usr/sbin/locale-gen ${LOCALE}
        fi
    else
        export ${ENTRY}=C
    fi
done
