Testing Environment
-------------------

This environment is used to install the whole IRMA platform in a single
virtual machine, merely for testing purposes.

Requirements
````````````

- `Vagrant <http://www.vagrantup.com/>`_ 1.5 or higher has to be installed.
- As the installation work only for `Virtualbox <https://www.virtualbox.org/>`_,
  you will need to install it.

Setup
`````

Run the following command in the directory containing the ``Vagrantfile``:

.. code-block:: bash

	$ vagrant up

Vagrant will launch a VM and install IRMA on it. It can take a while
(from 15 to 30 min) depending on the amount of RAM you have on your computer,
the hard disk drive I/O speed and your Internet connection speed.

Once the installation has completed, IRMA's frontend interface will be available at `http://172.16.1.30 <http://172.16.1.30>`_.


