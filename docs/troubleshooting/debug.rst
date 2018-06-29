How to debug
------------

Collect debug files
+++++++++++++++++++

An Ansible playbook is available in order to gather logs and other useful
files.

The playbook is ``ansible/playbooks/collect_debug.yml`` and it will allow you
to retrieve on each host:
 - IRMA Files (located on the multiples hosts);
 - Systemd logs;
 - Application logs (Nginx, RabbitMQ, PostgreSQL).

After running the playbook, all the files are available in the directory
specified in the ``debug_directory`` variable of the playbook. The files are
store in directories named after the host they where retrieve from
(``<debug_directory>/<host_name>/<debug_files_or_directory>``).
Most of the files are plain text but Systemd logs are using a binary format.
To explore and read them, you'll need the ``journalctl`` command, for example:

.. code-block:: console

    $ journalctl -D debug/brain.irma/var/log/journal


Switch debug log on
+++++++++++++++++++

Configuration file for frontend, brain and probe is located by default in the ``config`` folder and
is named respectively ``frontend.ini``, ``brain.ini`` and ``probe.ini``.

To turn on debug log just add the following line:


.. code-block:: ini
   :emphasize-lines: 3

    [log]
    syslog = 0
    debug = 1

and restart all related applications.

To turn on SQL debug log (warning: its verbose) just add the following line:

.. code-block:: ini
   :emphasize-lines: 4

    [log]
    syslog = 0
    debug = 1
    sql_debug = 1

and restart all related applications.

Debug a probe
+++++++++++++

Open a session on the probe machine and change directory to
the irma-probe location. Try the run_module tool on a file
to see what analyzer is detected and what is its output on a
file.


.. code-block:: console
   :emphasize-lines: 7

    $ sudo su deploy
    $ cd /opt/irma/irma-probe/current
    $ ./venv/bin/python -m extras.tools.run_module

    [...]
    usage: run_module.py [-h] [-v]
                     {Unarchive,StaticAnalyzer,ClamAV,VirusTotal} filename
                     [filename ...]
    run_module.py: error: too few arguments


Here 4 probes are automatically detected. Now try one on a file:


.. code-block:: console

    $ ./venv/bin/python -m extras.tools.run_module ClamAV requirements.txt
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


Debug Ansible Provisioning
++++++++++++++++++++++++++

To debug errors while provisioning (same goes with deployment) with following typical command:


.. code-block:: console

    $ ansible-playbook  --private-key=~/.vagrant.d/insecure_private_key --inventory-file=.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory -u vagrant playbooks/provisioning.yml


Example output:


.. code-block:: none

    TASK [Mayeu.RabbitMQ : add rabbitmq user and set privileges] *******************
    [DEPRECATION WARNING]: Using bare variables is deprecated. Update your playbooks so that the environment value uses the
    full variable syntax ('{{rabbitmq_users_definitions}}').
    This feature will be removed in a future release. Deprecation
    warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
    failed: [brain.irma] (item={u'vhost': u'mqbrain', u'password': u'brain', u'user': u'brain'}) => {"failed": true, "item": {"password": "brain", "user": "brain", "vhost": "mqbrain"}, "module_stderr": "", "module_stdout": "Traceback (most recent call last):\r\n  File \"/tmp/ansible_wKXoO5/ansible_module_rabbitmq_user.py\", line 302, in <module>\r\n    main()\r\n  File \"/tmp/ansible_wKXoO5/ansible_module_rabbitmq_user.py\", line 274, in main\r\n    if rabbitmq_user.get():\r\n  File \"/tmp/ansible_wKXoO5/ansible_module_rabbitmq_user.py\", line 155, in get\r\n    users = self._exec(['list_users'], True)\r\n  File \"/tmp/ansible_wKXoO5/ansible_module_rabbitmq_user.py\", line 150, in _exec\r\n    rc, out, err = self.module.run_command(cmd + args, check_rc=True)\r\n  File \"/tmp/ansible_wKXoO5/ansible_modlib.zip/ansible/module_utils/basic.py\", line 1993, in run_command\r\n  File \"/usr/lib/python2.7/posixpath.py\", line 261, in expanduser\r\n    if not path.startswith('~'):\r\nAttributeError: 'list' object has no attribute 'startswith'\r\n", "msg": "MODULE FAILURE", "parsed": false}

You could first increase ansible verbosity by adding ``-vvv`` option (``-vvvv`` on windows for winrm debug), it will help is the problem is linked to arguments.


.. code-block:: console
   :emphasize-lines: 13

    $ ansible-playbook -vvv --private-key=~/.vagrant.d/insecure_private_key --inventory-file=.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory -u vagrant playbooks/provisioning.yml
    TASK [Mayeu.RabbitMQ : add rabbitmq user and set privileges] *******************
    task path: /home/alex/repo/irma-ansible/roles/Mayeu.RabbitMQ/tasks/vhost.yml:13
    [DEPRECATION WARNING]: Using bare variables is deprecated. Update your playbooks so that the environment value uses the full
    variable syntax ('{{rabbitmq_users_definitions}}').
    This feature will be removed in a future release. Deprecation warnings can be
    disabled by setting deprecation_warnings=False in ansible.cfg.
    <127.0.0.1> ESTABLISH SSH CONNECTION FOR USER: vagrant
    <127.0.0.1> SSH: EXEC ssh -C -q -o ForwardAgent=yes -o Port=2222 -o 'IdentityFile="/home/alex/.vagrant.d/insecure_private_key"' -o KbdInteractiveAuthentication=no -o PreferredAuthentications=gssapi-with-mic,gssapi-keyex,hostbased,publickey -o PasswordAuthentication=no -o User=vagrant -o ConnectTimeout=10 127.0.0.1 '/bin/sh -c '"'"'( umask 77 && mkdir -p "` echo $HOME/.ansible/tmp/ansible-tmp-1468570550.09-211613386938202 `" && echo ansible-tmp-1468570550.09-211613386938202="` echo $HOME/.ansible/tmp/ansible-tmp-1468570550.09-211613386938202 `" ) && sleep 0'"'"''
    <127.0.0.1> PUT /tmp/tmpiysJ6l TO /home/vagrant/.ansible/tmp/ansible-tmp-1468570550.09-211613386938202/rabbitmq_user
    <127.0.0.1> SSH: EXEC sftp -b - -C -o ForwardAgent=yes -o Port=2222 -o 'IdentityFile="/home/alex/.vagrant.d/insecure_private_key"' -o KbdInteractiveAuthentication=no -o PreferredAuthentications=gssapi-with-mic,gssapi-keyex,hostbased,publickey -o PasswordAuthentication=no -o User=vagrant -o ConnectTimeout=10 '[127.0.0.1]'
    <127.0.0.1> ESTABLISH SSH CONNECTION FOR USER: vagrant
    <127.0.0.1> SSH: EXEC ssh -C -q -o ForwardAgent=yes -o Port=2222 -o 'IdentityFile="/home/alex/.vagrant.d/insecure_private_key"' -o KbdInteractiveAuthentication=no -o PreferredAuthentications=gssapi-with-mic,gssapi-keyex,hostbased,publickey -o PasswordAuthentication=no -o User=vagrant -o ConnectTimeout=10 -tt 127.0.0.1 '/bin/sh -c '"'"'sudo -H -S -n -u root /bin/sh -c '"'"'"'"'"'"'"'"'echo BECOME-SUCCESS-rbeeckncuxenewcwkayivqiwvarchlrd; LANG=fr_FR.UTF-8 LC_ALL=fr_FR.UTF-8 LC_MESSAGES=fr_FR.UTF-8 /usr/bin/python /home/vagrant/.ansible/tmp/ansible-tmp-1468570550.09-211613386938202/rabbitmq_user; rm -rf "/home/vagrant/.ansible/tmp/ansible-tmp-1468570550.09-211613386938202/" > /dev/null 2>&1'"'"'"'"'"'"'"'"' && sleep 0'"'"''
    failed: [brain.irma] (item={u'vhost': u'mqbrain', u'password': u'brain', u'user': u'brain'}) => {"failed": true, "invocation": {"module_name": "rabbitmq_user"}, "item": {"password": "brain", "user": "brain", "vhost": "mqbrain"}, "module_stderr": "", "module_stdout": "Traceback (most recent call last):\r\n  File \"/tmp/ansible_Qo3lZl/ansible_module_rabbitmq_user.py\", line 302, in <module>\r\n    main()\r\n  File \"/tmp/ansible_Qo3lZl/ansible_module_rabbitmq_user.py\", line 274, in main\r\n    if rabbitmq_user.get():\r\n  File \"/tmp/ansible_Qo3lZl/ansible_module_rabbitmq_user.py\", line 155, in get\r\n    users = self._exec(['list_users'], True)\r\n  File \"/tmp/ansible_Qo3lZl/ansible_module_rabbitmq_user.py\", line 150, in _exec\r\n    rc, out, err = self.module.run_command(cmd + args, check_rc=True)\r\n  File \"/tmp/ansible_Qo3lZl/ansible_modlib.zip/ansible/module_utils/basic.py\", line 1993, in run_command\r\n  File \"/usr/lib/python2.7/posixpath.py\", line 261, in expanduser\r\n    if not path.startswith('~'):\r\nAttributeError: 'list' object has no attribute 'startswith'\r\n", "msg": "MODULE FAILURE", "parsed": false}


In this particular case, verbose doesn't add much information as the problem is linked to ansible scripts. Let's go one level deeper so.
Ansible output the temporary script executed on guest (highlighted in previous code block) but delete it just after execution. To further debug it we will set ansible to keep remote files and the debug session will now takes place inside the guest.


.. code-block:: console

    $ ANSIBLE_KEEP_REMOTE_FILES=1 ansible-playbook -vvv --private-key=~/.vagrant.d/insecure_private_key --inventory-file=.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory -u vagrant playbooks/provisioning.yml


in debug log get the temporary ansible path to remote script:


.. code-block:: console

    /usr/bin/python /home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/rabbitmq_user

Log in to remote machine and go to the temporary ansible dir. Explode the compressed script and run it locallly:


.. code-block:: console

    $ vagrant@brain:~/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275$ ls
    rabbitmq_user

    $ vagrant@brain:~/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275$ python rabbitmq_user explode
    Module expanded into:
    /home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/debug_dir

    $ vagrant@brain:~/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275$ ls debug_dir/
    ansible
    ansible_module_rabbitmq_user.py
    args

    $ vagrant@brain:~/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275$ python rabbitmq_user execute
    Traceback (most recent call last):
      File "/home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/debug_dir/ansible_module_rabbitmq_user.py", line 302, in <module>
        main()
      File "/home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/debug_dir/ansible_module_rabbitmq_user.py", line 274, in main
       if rabbitmq_user.get():
      File "/home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/debug_dir/ansible_module_rabbitmq_user.py", line 155, in get
        users = self._exec(['list_users'], True)
      File "/home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/debug_dir/ansible_module_rabbitmq_user.py", line 150, in _exec
        rc, out, err = self.module.run_command(cmd + args, check_rc=True)
      File "/home/vagrant/.ansible/tmp/ansible-tmp-1468571039.87-134696488633275/debug_dir/ansible/module_utils/basic.py", line 1993, in run_command
        args = [ os.path.expandvars(os.path.expanduser(x)) for x in args if x is not None ]
      File "/usr/lib/python2.7/posixpath.py", line 261, in expanduser
        if not path.startswith('~'):
    AttributeError: 'list' object has no attribute 'startswith'

You could now add debug to source files and properly understand where the problem is. In our example case, it is an ansible
problem related to module_rabbitmq_user present in 2.1.0.0 see github `PR <https://github.com/ansible/ansible-modules-extras/pull/2310>`_
