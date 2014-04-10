#!/bin/sh

PYPI_MIRROR_URL=http://brain.irma.qb:8000/pypi
IRMA_INSTALL_DIR=/home/irma/irma
IRMA_SCRIPTS_DIR=/home/irma/bin

if [ "$(id -u)" != "0" ]; then
echo "This script must be run as root" 1>&2
   exit 1
fi

echo "[+] update irma frontend package"
echo ""
sudo -u irma sh -c "pip install --install-option="--install-purelib=$IRMA_INSTALL_DIR" --install-option="--install-scripts=$IRMA_SCRIPTS_DIR" -i $PYPI_MIRROR_URL irma-frontend"
echo "[+] start/restart services"
echo ""
service mongodb start
service nginx start
service uwsgi restart
service celeryd restart
service celerybeat restart
echo "[+] done"
