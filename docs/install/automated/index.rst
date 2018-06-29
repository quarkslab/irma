Automated Installation
======================

The IRMA platform is easily installed thanks to a set of `ansible <http://www.ansible.com>`_ roles and playbooks. It permits a user to build, install or maintain different setups.

There are 2 different types of IRMA environment, and multiple setups for each environment:

- **Development environment** (sources rsync'd between host and vms)
    - ``allinone_dev``: everything installed in the same vm
    - ``dev``: every component on its own vm

- **Production environment** (sources installed through generated archives, install on vms/physical servers)
    - ``allinone_prod``: everything installed in the same vm/physical server (default environment)
    - ``prod``: every component on its own vm/physical server

For specific instructions on these 2 environments see the related section.

.. note:: Vagrant step is optional in production mode.

.. toctree::
    :maxdepth: 1

    environment_file.rst
    vagrant.rst
    ansible.rst
    windows.rst
    prod_specific.rst
    install_extras.rst

