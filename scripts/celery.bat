SET WORKDIR=c:\irma

SET LOGFILE=%WORKDIR%\celery.log
c:\Python27\Scripts\celery -A probe.probetasks worker -l info -n avname --without-heartbeat --without-mingle --without-gossip --workdir=%WORKDIR% > %LOGFILE% 2>&1
PAUSE
