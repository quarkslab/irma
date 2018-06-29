Vagrant setup
=============

Requirements
------------

- `Vagrant <http://www.vagrantup.com/>`_ 1.9 or higher has to be installed
- a supported hypervisor:
    - kvm/qemu (libvirt required, vagrant-libvirt plugin required)
    - `Virtualbox <https://www.virtualbox.org/>`_

Vagrant setup
-------------

.. code-block:: console

    (venv)$ export VM_ENV=dev
    (venv)$ export VM_ENV=allinone_dev
    (venv)$ export VM_ENV=prod
    (venv)$ export VM_ENV=allinone_prod  # (default)


Simply run in the `Vagrantfile` directory:

.. code-block:: console

    (venv)$ vagrant up (--provider=libvirt)


Vagrant will launch one/many VM(s).

.. note:: The basebox used in this project is provided by Quarkslab. The code source to build it is `here <https://github.com/quarkslab/debian>`_.


Useful commands
```````````````

Some useful commands with vagrant:

.. code-block:: console

    $ vagrant ssh <server_name>       # login through ssh
    $ vagrant halt <server_name>      # shutdown the machine
    $ vagrant reload <server_name>    # restart the machine
    $ vagrant up <server_name>        # start the machine
    $ vagrant destroy <server_name>   # delete the machine
