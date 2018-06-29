Windows provisioning
====================


Generate Windows base box
-------------------------

.. code-block:: console

    $ git clone https://github.com/boxcutter/windows
    $ cd windows
    $ make virtualbox/eval-win10x64-enterprise

Adding to Vagrant boxes
-----------------------

.. code-block:: console

    $ vagrant box add --name eval-win10x64-enterprise box/virtualbox/eval-win10x64-enterprise*.box

Creating an instance of the base box
------------------------------------

.. code-block:: console

    $ VM_ENV=<your_env> vagrant up

Provisioning with ansible
-------------------------

In the config file don't forget to add ``windows: true`` in the server. Example:


.. code-block:: yaml
    :emphasize-lines: 5

    servers:
      - name: mcafee-win.irma
        ip: 172.16.1.33
        box: eval-win10x64-enterprise
        ansible_groups: [mcafee-win]
        windows: true


Provisioning a windows host is done the same way as other hosts:

.. code-block:: console

    (venv)$ python irma-ansible.py environments/allinone_prod.yml playbooks/playbook.yml
