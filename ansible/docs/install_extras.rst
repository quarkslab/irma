Extras
======

Enable SSL using OpenSSL
------------------------

If you want to activate SSL on the frontend server, you’ll need:

- modify frontend_openssl variables in `playbooks/group_vars/frontend`:


.. code-block:: bash

  frontend_openssl: True # Default is false
  frontend_openssl_dh_param: # put the DH file locations
  frontend_openssl_certificates: [] # an array of files {source, destination}
                                    # to copy to the server

- Uncomment (and customize) the `nginx_sites` variable in the
  `playbooks/group_vars/frontend`, a commented example is available.

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


Installation behind a corporate proxy
-------------------------------------

Thanks to the `vagrant-proxyconf` plugin (see: https://github.com/tmatilai/vagrant-proxyconf),
IRMA can be installed behind corporate proxy.

First, `vagrant-proxyconf` has to be installed:

.. code-block:: bash

    $ vagrant plugin install vagrant-proxyconf

Then, the `vagrant-proxyconf` configuration has to be added to `ansible/Vagrantfile`.
Here is an example:

.. code-block:: ruby

  if Vagrant.has_plugin?("vagrant-proxyconf")
    config.proxy.http     = "http://corporate.proxy:3128"
    config.proxy.https    = "http://corporate.proxy:3128"
    config.proxy.no_proxy = "localhost,127.0.0.1"
  end

Finally, `vagrant up` can be launched, as usual.

It has to be noted that using such mechnanism has two limitations:

- it is not working with Windows based boxes
- it is not working with tools that are not able do deal with environment based
  proxy definition (`http_proxy` and `https_proxy` environment varibles). For
  instance, AVG updater does not take into account such definition.
