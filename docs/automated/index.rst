Automated Install
=================

IRMA platform can be easily installed with a set of `ansible
<http://www.ansible.com>`_ roles and playbooks. It will help you to build,
install or maintain different setups.

Requirements
------------

- `Ansible <https://github.com/ansible/ansible>`_ 2.0 or higher;


.. warning::

   Some version of Ansible breaks IRMA install. Current tested version: 2.1.1.0


Ansible scripts
---------------

Get IRMA ansible scripts on github:

.. code-block:: bash

    $ git clone https://github.com/quarkslab/irma

Predefined Environments
-----------------------

There are 2 different IRMA setups available:

.. toctree::
    development-env.rst
    production-env.rst


Using Debian repos
------------------

If you planned to use only Debian official repository, you'll need to change in
``playbooks/group_vars/all``:

.. code-block:: yaml

    default_use_debian_repo: yes # no is the default value
