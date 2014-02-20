change app name and path in celery.defaults

copy celeryd in /etc/init.d/
chmod +x /etc/init.d/celeryd
copy celery.defaults  in /etc/default/celeryd
sudo /usr/sbin/update-rc.d celeryd defaults
