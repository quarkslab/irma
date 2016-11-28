Production environment
----------------------

This environment is used to install IRMA on production-ready Debian servers.

Requirements
````````````

- One or multiple 64-bit `Debian <https://www.debian.org>`_ 7 servers.

Preparing servers
`````````````````

Create an account that is going to be used to provision IRMA on the server via
Ansible, or use one which has already been created. To speed up provisioning,
you can:

- Authorize your SSH key for password-less authentication (optional):

.. code-block:: bash

    # On your local machine
    $ ssh-copy-id user@hostname # -i if you want to select your identity file

- If you do not want to have to type your password for ``sudo`` command,
  consider adding your user to sudoers, using ``visudo`` command (optional):

.. code-block:: bash

      user ALL=(ALL) NOPASSWD: ALL

Configure for your installation
```````````````````````````````

Modify settings in ``playbooks/group_vars/all`` especially the
``default_ssh_keys:`` section.  You will need to add your public keys for SSH
password-less connection to the default irma server user.

Configuration file used by the brain, the frontend and the probes applications
are generated with default values that are specified in
``playbooks/group_vars/brain``, ``playbooks/group_vars/frontend`` and
``playbooks/group_vars/probe`` respectively. Make sure to adapt
``xxx_deployment_configs`` variables accordingly to your installation. It is
recommended to change all the default passwords defined in ``group_vars/*``
configuration files (``password`` variables for most of them).

Finally, you will need to customize the ``hosts/example`` file and adapt it
to describe your own server infrastructure. There is three sections, one for
each server role (frontend, brain, probe). Please refer to `Ansible Inventory
documentation <http://docs.ansible.com/intro_inventory.html#inventory>`_ for
the expected syntax.

Run the Ansible Playbook
````````````````````````

To run the main playbook with the ``hosts/example`` file you have defined, use
the following command. Ansible will ask you the sudo password (``-K`` option).

.. code-block:: bash

    $ cd <IRMA_SRC_DIR>/ansible
    $ ansible-playbook -i ./hosts/example playbooks/playbook.yml -u <your_sudo_username> -K

To run one or more specific actions and avoid running all the playbook, you can
use tags. For example, if you want to re-provision Nginx, run the same command,
but append ``--tags=nginx``. You can combine multiple tags separated with
commas.

Deploy a new version of IRMA
````````````````````````````

Assuming that you have already provisioned and deployed a version of IRMA,
which you want to upgrade, you will need to run the deployment script:

.. code-block:: bash

    $ ansible-playbook -i ./hosts/example ./playbooks/deployment.yml -u irma

Make sure to replace ``irma`` with the default user if you have changed it in the
``group_vars/all`` file.

Access your IRMA installation
`````````````````````````````

Once the provisioning and the deployment have finished, you should be able to
perform scans and get their results via the frontend hostname you specified.


