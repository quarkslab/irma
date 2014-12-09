Automated Install
=================

IRMA platform can be easily installed with a set of `ansible
<http://www.ansible.com>`_ roles and playbooks. It will help you to build,
install or maintain different setups.

Requirements
------------

- `Ansible <http://www.ansible.com>`_ 1.8 or higher;

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
    production-env.rst
    development-env.rst
