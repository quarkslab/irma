#!/bin/bash

IRMA_DIR=/home/irma/irma
PIDFILE=$IRMA_DIR/frontend.pid

function launch_frontend {
	cd $IRMA_DIR
	python -m frontend.web.api 2> $IRMA_DIR/frontend.log &
	echo -n $! > $PIDFILE
}

if [ -f $PIDFILE ] ; then
	PID=`cat $PIDFILE`
   	if ! ps -p $PID &> /dev/null; then
	   launch_frontend
	fi
else
	launch_frontend
fi
