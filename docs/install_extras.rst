Extras
======

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
