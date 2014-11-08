Development environment
=======================

Everything is installed in one vm with sources rsync'd between host and guest.
If you want to modify IRMA, this is the recommended way of installing it.

Requirements
------------

- `Vagrant <http://www.vagrantup.com/>`_ 1.5 or higher has to be installed
- As the installation work only for `Virtualbox <https://www.virtualbox.org/>`_,
  you’ll need to install it
- `Rsync <https://rsync.samba.org/>`_ to synchronize directories from host to VMs
- Read the `Ansible introduction <http://docs.ansible.com/intro.html>`_



1. Create the right environment
-------------------------------


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
----------------------------------

To initialize and provision the Virtualbox VM, run in the
irma-ansible-provisioning directory `vagrant up --no-provision`. VM will be
downloaded, and configured using `environments/dev.yml` file (default behavior).

(optional) If you want to use your own environment, create it in `environments`
directory and run:

.. code-block:: bash

	$ VM_ENV=your_environment_name vagrant up --no-provision


3. Configure your .ini files
----------------------------

/!\ You can bypass this step, as this provisioning is sync with default username
and password used in (frontend|brain|probe) config files.

As your `config/*.ini` file are transferring from host to VMs, you’ll need
locally to modify it (frontend, probe, brain) to match `group_vars/*` user and
password.

In next release of this playbook, there’ll be more convenient way to automate
configuration generation.


4. Provision your VMs
---------------------

Due to Ansible limitations using parallel execution, you’ll need to launch the
provision Vagrant command only for one VM:

.. code-block:: bash

	$ vagrant provision frontend.irma


The provisioning and deployment will apply to all of your VMs.


5. Access to the IRMA interface
-------------------------------

Then, with your web browser, IRMA allinone is available at
`http://172.16.1.30 <http://172.16.1.30>`_.


6. Sync files between host and guest
------------------------------------

Once rsync is installed inside your virtual machine and your environment is correctly set. You could easily sync your code with:

.. code-block:: bash

	$ vagrant rsync # or vagrant rsync-auto to automatically initiates an rsync
                        # transfer when changes are detected


Then reload the modified application.
