=========================
IRMA Ansible Provisioning
=========================

|build-status| |docs|

IRMA platform is easily installed thanks to a set of `ansible <http://www.ansible.com>`_ roles and playbooks. It will allow you to build, install or maintain different setups.

- First, clone this repository:

.. code-block:: bash

	$ git clone https://github.com/quarkslab/irma-ansible

There are 3 different types of IRMA setup:

- `Testing IRMA, the easiest way`_ (everything in one vm)
- `Production environment <docs/install_prod.rst>`_ (install on physical servers)
- `Development environment <docs/install_dev.rst>`_ (everything in one vm with sources rsync'd between host and vm)

Common requirements
-------------------

- `Ansible <http://www.ansible.com>`_ 1.8 or higher;

Dependencies are available via `Ansible Galaxy <https://galaxy.ansible.com/>`_ repository. Installation has been made easy using:

.. code-block:: bash

	$ ansible-galaxy install -r ansible-requirements.yml # --force if you’ve already installed it


Testing IRMA, the easiest way
-----------------------------

Everything will be installed in the same virtual machine named `brain.irma`.

Requirements
````````````

- `Vagrant <http://www.vagrantup.com/>`_ 1.5 or higher has to be installed
- As the installation work only for `Virtualbox <https://www.virtualbox.org/>`_,
  you’ll need to install it

Setup
`````

Simply run in the `Vagrantfile` directory:

.. code-block:: bash

	$ vagrant up


Vagrant will launch a VM and install IRMA on it. It can take a while
(from 15 to 30 min) depending on the amount of RAM you have on your computer
and the hard disk drive I/O speed.

IRMA allinone interface is available at `http://172.16.1.30 <http://172.16.1.30>`_.

Note: The basebox used in this project is provided by Quarkslab. The code
source to build it is `here <https://github.com/quarkslab/debian-vm>`_.


Useful commands
```````````````

some useful commands with vagrant:


.. code-block:: bash

	$ vagrant ssh brain.irma       # login through ssh
	$ vagrant halt brain.irma      # shutdown the machine
	$ vagrant reload brain.irma    # restart the machine
	$ vagrant up brain.irma        # start the machine
	$ vagrant destroy brain.irma   # delete the machine

for advanced usage of vagrant be sure to check `extras <docs/install_extras.rst>`_

Credits
-------

Some of roles from `Ansible Galaxy <https://galaxy.ansible.com/>`_ used here:

- MongoDB role from `Stouts/Stouts.mongodb <https://github.com/Stouts/Stouts.mongodb>`_
- NodeJS role from `JasonGiedymin/nodejs <https://github.com/AnsibleShipyard/ansible-nodejs>`_
- Nginx role from `jdauphant/ansible-role-nginx <https://github.com/jdauphant/ansible-role-nginx>`_
- OpenSSH role from `Ansibles/openssh <https://github.com/Ansibles/openssh>`_
- Sudo role from `weareinteractive/ansible-sudo <https://github.com/weareinteractive/ansible-sudo>`_
- Users role from `mivok/ansible-users <https://github.com/mivok/ansible-users>`_
- uWSGI role from `gdamjan/ansible-uwsgi <https://github.com/gdamjan/ansible-uwsgi>`_


.. |build-status| image:: https://travis-ci.org/quarkslab/irma-ansible.svg?branch=master
    :alt: Travis-CI build status
    :scale: 100%
    :target: https://travis-ci.org/quarkslab/irma-ansible

.. |docs| image:: https://readthedocs.org/projects/irma/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/irma/
