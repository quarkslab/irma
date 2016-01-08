Connect to a vagrant box through ssh
------------------------------------

If you don't already have it download vagrant insecure_private_key

.. code-block:: bash

	$ wget https://raw.githubusercontent.com/mitchellh/vagrant/master/keys/vagrant -O insecure_private_key


Then change rights on the key otherwise ssh will complains and connect to your vagrant box

.. code-block:: bash

	$ chmod 700 insecure_private_key
	$ ssh vagrant@172.16.1.30 -i insecure_private_key



Enable SSL using OpenSSL in ansible scripts
-------------------------------------------

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

- vagrant-cachier (more `info on vagrant-cachier <https://github.com/fgrehm/vagrant-cachier>`_)

.. code-block:: bash

	$ vagrant plugin install vagrant-cachier

- vagrant-vbguest (more `info on vagrant-vbguest <https://github.com/dotless-de/vagrant-vbguest>`_)

.. code-block:: bash

	$ vagrant plugin install vagrant-vbguest
