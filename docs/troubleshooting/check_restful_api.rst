Restful API
```````````

One can verify that the restful API is up and running by querying a specific
route on the web server or by checking the system logs:

.. code-block:: console

    $ curl http://localhost/api/v1.1/probes
    {"total": 9, "data": ["ClamAV", "ComodoCAVL", "EsetNod32", "FProt", "Kaspersky", "McAfeeVSCL", "NSRL", "StaticAnalyzer", "VirusTotal"]}

    $  sudo cat /var/log/supervisor/frontend_api.log
    [...]
    added /opt/irma/irma-frontend/current/venv/ to pythonpath.
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI master process (pid: 3943)
    spawned uWSGI worker 1 (pid: 3944, cores: 1)
    spawned uWSGI worker 2 (pid: 3945, cores: 1)
    spawned uWSGI worker 3 (pid: 3946, cores: 1)
    spawned uWSGI worker 4 (pid: 3947, cores: 1)
    mounting frontend/api/base.py on /api
    mounting frontend/api/base.py on /api
    mounting frontend/api/base.py on /api
    mounting frontend/api/base.py on /api
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3945 (default app)
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3946 (default app)
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3944 (default app)
    WSGI app 0 (mountpoint='/api') ready in 0 seconds on interpreter 0x99a3e0 pid: 3947 (default app)

