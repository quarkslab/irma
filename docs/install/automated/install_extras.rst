Extras
======

Installation behind a corporate proxy
-------------------------------------

Thanks to the `vagrant-proxyconf plugin <https://github.com/tmatilai/vagrant-proxyconf>`_,
IRMA can be installed behind corporate proxy.

First, ``vagrant-proxyconf`` has to be installed:

.. code-block:: console

    $ vagrant plugin install vagrant-proxyconf

Then, the ``vagrant-proxyconf`` configuration has to be added to `ansible/Vagrantfile`.
Here is an example:

.. code-block:: ruby

  if Vagrant.has_plugin?("vagrant-proxyconf")
    config.proxy.http     = "http://corporate.proxy:3128"
    config.proxy.https    = "http://corporate.proxy:3128"
    config.proxy.no_proxy = "localhost,127.0.0.1"
  end

Finally, ``vagrant up`` can be launched, as usual.

It has to be noted that using such mechanism has two limitations:

- it is not working with Windows based boxes
- it is not working with tools that are not able do deal with environment based
  proxy definition (``http_proxy`` and ``https_proxy`` environment variables). For
  instance, AVG updater does not take into account such definition.
