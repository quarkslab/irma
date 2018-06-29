Ansible setup
=============

Common requirements
-------------------

- `Ansible <http://www.ansible.com>`_ 2.0+ (see requirements.txt for version required)

.. code-block:: console

    (venv)$ pip install -r requirements.txt

.. warning::  Due to ansible breaking releases, the ansible version supported is now fixed


Ansible playbooks
-----------------

IRMA Installation is split in playbooks (in ansible/playbooks directory):

* playbooks/provisioning.yml for dependencies setup
* playbooks/updating.yml for av update only
* playbooks/deployment.yml for irma code setup
* playbooks/playbook.yml (provisioning + updating + deployment)


Launch Ansible
--------------

.. note:: If your environment requires some virtual machines handled by vagrant, you must do this first.

To launch one of these playbook, the full command is:

.. code-block:: console

    # Dependencies setup
    (venv)$ python irma-ansible.py environments/allinone_prod.yml playbooks/provisioning.yml

    # AV update only
    (venv)$ python irma-ansible.py environments/allinone_prod.yml playbooks/updating.yml

    # IRMA code install
    (venv)$ python irma-ansible.py environments/allinone_prod.yml playbooks/deployment.yml

    # Full install (provisioning + updating + deployment)
    (venv)$ python irma-ansible.py environments/allinone_prod.yml playbooks/playbook.yml

Last one will do the full install of IRMA. It can take a while
(from 15 to 30 min) depending on the amount of RAM available on the machine
and the hard disk drive I/O speed.

The default IRMA interface is available at `http://172.16.1.30 <http://172.16.1.30>`_. According to your frontend server configuration.

References
----------

Some roles from `Ansible Galaxy <https://galaxy.ansible.com/>`_ used here:

- NodeJS role from `JasonGiedymin/nodejs <https://github.com/AnsibleShipyard/ansible-nodejs>`_
- Nginx role from `jdauphant/ansible-role-nginx <https://github.com/jdauphant/ansible-role-nginx>`_
- OpenSSH role from `Ansibles/openssh <https://github.com/Ansibles/openssh>`_
- UFW role from `weareinteractive/ansible-ufw <https://github.com/weareinteractive/ansible-ufw>`_
- Sudo role from `weareinteractive/ansible-sudo <https://github.com/weareinteractive/ansible-sudo>`_
- Users role from `mivok/ansible-users <https://github.com/mivok/ansible-users>`_
