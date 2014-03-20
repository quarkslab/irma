SET WORKDIR=c:\irma
SET PIP_PKG=irma-probe
SET LOCAL_PYPI_URL=http://brain.irma.qb:8000/pypi

SET PIPLOGFILE=%WORKDIR%\pip_upgrade.log
SET LOGFILE=%WORKDIR%\celery.log

c:\Python27\Scripts\pip.exe install --install-option="--install-purelib=%WORKDIR%" -i %LOCAL_PYPI_URL% %PIP_PKG% > %PIPLOGFILE% 2>&1
CD %WORKDIR%
c:\Python27\python.exe -m probe.tasks  > %LOGFILE% 2>&1
PAUSE
