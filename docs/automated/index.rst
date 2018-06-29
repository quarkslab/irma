Automated Install
=================

IRMA platform can be easily installed with a set of `ansible
<http://www.ansible.com>`_ roles and playbooks. It will help you to build,
install or maintain different setups.

Requirements
------------

- `Ansible <https://github.com/ansible/ansible>`_ 2.2.1.0;



Ansible scripts
---------------

Get IRMA ansible scripts on github:

.. code-block:: console

    $ git clone https://github.com/quarkslab/irma
    $ cd irma/ansible

Predefined Environments
-----------------------

There are 2 different IRMA setups available. Dev/Testing will be installed in one or
multiple virtual machines while production could be used to install IRMA on physical machines
or virtual machines already setup:

.. toctree::
    development-env.rst
    production-env.rst


Using Debian repos
------------------

If you planned to use only Debian official repository, you'll need to change in
``playbooks/group_vars/all``:

.. code-block:: yaml

    default_use_debian_repo: yes # no is the default value
