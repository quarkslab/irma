Automatic Install
=================

IRMA platform is easily installed thanks to a set of `ansible
<http://www.ansible.com>`_ roles and playbooks. It will allow you to build,
install or maintain different setups.

First, get IRMA ansible scripts on github:

.. code-block:: bash

	$ git clone --recursive https://github.com/quarkslab/irma-ansible

There are 3 different IRMA setup available:

- `Testing IRMA, the easiest way`_ (everything in one vm)
- `Production environment`_ (install on physical servers)
- `Development environment`_ (everything in one vm with sources rsync-ed between
  host and vm)

Common Requirements
-------------------

- `Ansible <http://www.ansible.com>`_ 1.6 or higher;

Dependencies are available via `Ansible Galaxy <https://galaxy.ansible.com/>`_
repository. Installation has been made easy using:

.. code-block:: bash

	$ ansible-galaxy install -r galaxy.yml # eventually, add '--force' to overwrite installed roles


Testing IRMA, the easiest way
-----------------------------

Everything will be installed in the same virtual machine.

Requirements
````````````

- `Vagrant <http://www.vagrantup.com/>`_ 1.5 or higher has to be installed
- As the installation work only for `Virtualbox <https://www.virtualbox.org/>`_,
  you will need to install it

Setup
`````

Run the following command in the directory containing the
`Vagrantfile`:

.. code-block:: bash

	$ vagrant up


Vagrant will launch a VM and install IRMA on it. It can take a while
(from 15 to 30 min) depending on the amount of RAM you have on your computer
and the hard disk drive I/O speed.

IRMA allinone interface is available at `http://172.16.1.30 <http://172.16.1.30>`_.


Production environment
----------------------

IRMA will be installed on physical servers.

Requirements
````````````

- One or multiple 64-bit `Debian <https://www.debian.org>`_ 7 servers.

1. Prep servers
```````````````

Create an account for Ansible provisioning, or use one which has already been
created. For speed up provisioning, you can:

- Authorize you SSH key for password-less authentication (optional):


.. code-block:: bash

	*On your local machine*
	$ ssh-copy-id user@hostname # -i if you want to select your identity file


- If you don’t want to have to type your password for `sudo` command execution,
  add your user to sudoers, using `visudo` command (optional):

.. code-block:: bash

	  user ALL=(ALL) NOPASSWD: ALL


2. Configure you installation
`````````````````````````````

Modify settings in `group_vars/*` especially the `default_ssh_keys:` section,
you’ll need to add private keys from user for password-less connection to the
default irma server user. *Be careful, you’ll need to change all passwords
from this configuration files (`password` variables for most of them).*

You’ll need to custom the `hosts` file and adapt it with you own server
infrastructure. There is three sections, one for each server role (frontend,
brain, probe).


3. Run the Ansible Playbook
```````````````````````````

To run the whole thing:

.. code-block:: bash

	$ ansible-playbook -i ./hosts playbook.yml -u <your_sudo_username> -K

Ansible will ask you the sudo password (`-K` option),

To run one or more specific actions you can use tags. For example, if you want
to re-provision Nginx, run the same command, but add `--tags=nginx`. You can
combine multiple tags.


4. Modify .ini files
````````````````````

You’ll need to connect on each server you’ve just used, and modify manually .ini
files.

In next release of this playbook, there’ll be more convenient way to automate
configuration generation.


5. Deploy new version of IRMA
`````````````````````````````

As your servers have been provision and deploy in step 5, when you want to upgrade
it, you’ll need to run the deployment script:

.. code-block:: bash

	$ ansible-playbook -i ./hosts deployment.yml -u irma


/!\ Replace `irma` with the default user if you’ve change it in the
`group_vars/all` file.


6. Access to your IRMA installation
```````````````````````````````````

Access to your installation using the hostname you’ve used as frontend hostname.


Development environment
-----------------------

Everything is installed in one vm with sources rsync'd between host and guest.
If you want to modify IRMA, this is the recommended way of installing it.

Requirements
````````````

- `Vagrant <http://www.vagrantup.com/>`_ 1.5 or higher has to be installed
- As the installation work only for `Virtualbox <https://www.virtualbox.org/>`_,
  you’ll need to install it
- `Rsync <https://rsync.samba.org/>`_ to synchronize directories from host to VMs
- Read the `Ansible introduction <http://docs.ansible.com/intro.html>`_



1. Create the right environment
```````````````````````````````


Clone IRMA repositories:

.. code-block:: bash

	$ git clone --recursive https://github.com/quarkslab/irma-frontend
	$ git clone --recursive https://github.com/quarkslab/irma-brain
	$ git clone --recursive https://github.com/quarkslab/irma-probe

If you’re interested in using `Vagrant <http://vagrantup.com>`_, be sure to have
the following directory layout:

.. code-block:: bash

	# all in the same directory
 	|
 	+--- irma-frontend
 	+--- irma-probe
 	+--- irma-brain
 	[...]
 	+--- irma-ansible


Note: This directory layout can be modified, see `share_*` from
`environments/dev.yml` and `environments/allinone_dev.yml` files.


2. Run Vagrant and create your VMs
``````````````````````````````````

To initialize and provision the Virtualbox VM, run in the
irma-ansible-provisioning directory `vagrant up --no-provision`. VM will be
downloaded, and configured using `environments/dev.yml` file (default behavior).

(optional) If you want to use your own environment, create it in `environments`
directory and run:

.. code-block:: bash

	$ VM_ENV=your_environment_name vagrant up --no-provision

3. Configure your .ini files
````````````````````````````

/!\ You can bypass this step, as this provisioning is sync with default username
and password used in (frontend|brain|probe) config files.

As your `config/*.ini` file are transferring from host to VMs, you’ll need
locally to modify it (frontend, probe, brain) to match `group_vars/*` user and
password.

In next release of this playbook, there’ll be more convenient way to automate
configuration generation.


4. Provision your VMs
`````````````````````

Due to Ansible limitations using parallel execution, you’ll need to launch the
provision Vagrant command only for one VM:

.. code-block:: bash

	$ vagrant provision frontend.irma


The provisioning and deployment will apply to all of your VMs.


5. Modify your host and open IRMA frontend
``````````````````````````````````````````

Then, for proper use, update your `/etc/hosts` file and add:


.. code-block:: bash

	172.16.1.30    www.frontend.irma


Then, with your web browser, IRMA allinone is available at
`www.frontend.irma <http://www.frontend.irma>`_.

6. Sync files between host and guest
````````````````````````````````````

Once rsync is installed inside your virtual machine and your environment is correctly set. You could easily sync your code with:

.. code-block:: bash

	$ vagrant rsync # or vagrant rsync-auto to automatically initiates an rsync
                        # transfer when changes are detected


Then reload the modified application.

Enable SSL using OpenSSL
------------------------

If you want to activate SSL on the frontend server, you’ll need:

- modify frontend_openssl variables in `group_vars/frontend`:


.. code-block:: bash

  frontend_openssl: True # Default is false
  frontend_openssl_dh_param: # put the DH file locations
  frontend_openssl_certificates: [] # an array of files {source, destination}
                                    # to copy to the server

- Uncomment (and customize) the `nginx_sites` variable in the
  `group_vars/frontend`, a commented example is available.

Then, provision or re-provision your infrastructure. Ansible will only change
file related to OpenSSL and Nginx configurations.


Speed up your Vagrant VMs
-------------------------

Install this softwares:

- vagrant-cachier (more `info <https://github.com/fgrehm/vagrant-cachier>`_)

.. code-block:: bash

	$ vagrant plugin install vagrant-cachier

- vagrant-vbguest (more `info <https://github.com/dotless-de/vagrant-vbguest>`_)

.. code-block:: bash

	$ vagrant plugin install vagrant-vbguest

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
