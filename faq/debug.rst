How to debug
------------


Switch debug log on
+++++++++++++++++++

Configuration file for frontend, brain and probe is located by default in the ``config`` folder and
is named respectively ``frontend.ini``, ``brain.ini`` and ``probe.ini``.

To turn on debug log just add the following line:


.. code-block:: bash
   :emphasize-lines: 3

	[log]
	syslog = 0
	debug = 1

and restart all applications.


Debug a probe
+++++++++++++

Open a session on the probe machine and change directory to
the irma-probe location. Try the run_module tool on a file
to see what analyzer is detected and what is its output on a
file.


.. code-block:: bash

	$ sudo su deploy
	$ cd /opt/irma/irma-probe/current
	$ ./venv/bin/python -m tools.run_module

	[...]
	usage: run_module.py [-h] [-v]
                     {Unarchive,StaticAnalyzer,ClamAV,VirusTotal} filename
                     [filename ...]
	run_module.py: error: too few arguments


Here 4 probes are automatically detected. Now try one on a file:


.. code-block:: bash

	$ ./venv/bin/python -m tools.run_module ClamAV requirements.txt
	{'database': {'/var/lib/clamav/bytecode.cvd': {'ctime': 1458640823.285298,
                                               'mtime': 1458640823.069295,
                                               'sha256': '82972e6cc5f1204829dba913cb1a0b5f8152eb73d3407f6b86cf388626cff1a1'},
              '/var/lib/clamav/daily.cvd': {'ctime': 1458640822.8932924,
                                            'mtime': 1458640822.6692889,
                                            'sha256': '9804c9b9aaf983f85b4f13a7053f98eb7cca5a5a88d3897d49b22182b228885f'},
              '/var/lib/clamav/main.cvd': {'ctime': 1458640821.6972747,
                                           'mtime': 1458640813.9771628,
                                           'sha256': '4a8dfbc4c44704186ad29b5a3f8bdb6674b679cecdf83b156dd1c650129b56f2'}},
	 'duration': 0.0045299530029296875,
	 'error': None,
	 'name': 'Clam AntiVirus Scanner',
	 'platform': 'linux2',
	 'results': None,
	 'status': 0,
	 'type': 'antivirus',
	 'version': '0.99'}

And check the output.