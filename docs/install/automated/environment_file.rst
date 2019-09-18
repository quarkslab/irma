Environment file
================

IRMA installation uses ansible and optionally Vagrant, and supports a common configuration format that allows
launching of Vagrant and/or ansible. ``VagrantFile`` automatically parses the configuration file to allow vagrant to launch required virtual machines, and ``irma-ansible.py`` parses this same file to create an inventory and an extra variable (vars) file before launching ansible.


Format
------

For examples look at the files ``*.yml`` in the ``ansible/environments`` directory.
Whole IRMA infrastructure is described here:

.. code-block:: yaml

    servers:
      - name: <hostname>
        ip: <ip address>
        ansible_groups: [list of ansible groups]
        box: [vagrant box name]
        cpus: [vagrant cpus (optional)]
        memory: [vagrant memory (optional)]
        shares: [vagrant share (optional)]
        [...]

    libvirt_config:
      driver: kvm
      # connect_via_ssh: true
      # host:
      # username:
      # storage_pool_name:
      # id_ssh_key_file:

    ansible_vars:
      key: value
      [...]

* ``servers`` section both described ansible usage of the server and its vagrant configuration if needed.
* ``libvirt_config`` section is a vagrant-only section for using libvirt hypervisor.
* ``ansible_vars`` section is an ansible-only section for defining extra ansible variables.

Example of a development environment with vagrant:

.. code-block:: yaml
    :emphasize-lines: 1, 34, 37

    servers:
      - name: brain.irma
        ip: 172.16.1.30
        ansible_groups: [frontend, sql-server, brain, comodo, trid]
        box: quarkslab/debian-9.0.0-amd64
        cpus: 2
        memory: 2048
        shares:
          - share_from: ../common
            share_to: /opt/irma/irma-common/releases/sync
            share_exclude:
              - .git/
              - venv/
          - share_from: ../frontend
            share_to: /opt/irma/irma-frontend/releases/sync
            share_exclude:
              - .git/
              - venv/
              - web/dist
              - web/node_modules
          - share_from: ../brain
            share_to: /opt/irma/irma-brain/releases/sync
            share_exclude:
              - .git/
              - venv/
              - db/
          - share_from: ../probe
            share_to: /opt/irma/irma-probe/releases/sync
            share_exclude:
              - .git/
              - venv/

    libvirt_config:
      driver: kvm

    ansible_vars:
      irma_environment: development
      vagrant: true

And an example of an environment without vagrant:

.. code-block:: yaml

    servers:
      - name: frontend.irma
        ip: 172.16.1.30
        ansible_groups: [frontend, sql-server]
      - name: brain.irma
        ip: 172.16.1.31
        ansible_groups: [brain]
      - name: avs-linux.irma
        ip: 172.16.1.32
        ansible_groups: [avast, avg, bitdefender, clamav, comodo, escan]
      - name: mcafee-win.irma
        ip: 172.16.1.33
        ansible_groups: [mcafee-win]
        windows: true

    ansible_vars:
      irma_environment: production
      vagrant: true
      irma_release: HEAD


Extra vars
----------

It is possible to customize IRMA variables in section ``ansible_vars``
(see ``irma_vars.yml.sample`` for a full list of available vars).
