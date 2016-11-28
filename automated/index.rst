Automated Install
=================

IRMA platform can be easily installed with a set of `ansible
<http://www.ansible.com>`_ roles and playbooks. It will help you to build,
install or maintain different setups.

Requirements
------------

- `Ansible <https://github.com/ansible/ansible>`_ 2.0 or higher;


.. warning::

   The automated install is not working with latest version of ansible. Maximum tested version is 2.0.1.0


Ansible scripts
---------------

Get IRMA ansible scripts on github:

.. code-block:: bash

	$ git clone https://github.com/quarkslab/irma-ansible

Install the dependencies via `Ansible Galaxy <https://galaxy.ansible.com/>`_
repository:

.. code-block:: bash

	$ ansible-galaxy install -r ansible-requirements.yml # eventually, add '--force' to overwrite installed roles

Predefined Environments
-----------------------

There are 3 different IRMA setups available:

.. toctree::
    testing-env.rst
    development-env.rst
    production-env.rst


Using Debian repos
------------------

If you planned to use only Debian official repository, you'll need to change in
``playbooks/group_vars/all``:

.. code-block:: yaml

    default_use_debian_repo: yes # no is the default value
