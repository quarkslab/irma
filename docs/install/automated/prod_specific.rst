Production environment
======================

IRMA will be installed on physical servers.

Requirements
------------

- One or multiple 64-bit `Debian <https://www.debian.org>`_ 9 servers.

1. Prep servers
---------------

Create an account for ansible provisioning, or use one which has already been
created. To speed up provisioning, you can:

- Authorize your SSH key for password-less authentication (optional):

.. code-block:: console

    *On your local machine*
    $ ssh-copy-id user@hostname # -i if you want to select your identity file


- If you don’t want to have to type your password for ``sudo`` command execution,
  add your user to sudoers, using ``visudo`` command (optional):

.. code-block:: console

    user ALL=(ALL) NOPASSWD: ALL


2. Configure the installation
-----------------------------

Modify ansible ``extra_vars`` especially the ``provisioning_ssh_key`` section,
you’ll need to add private keys from user for password-less connection to the
default IRMA server user.

.. warning:: Be careful, you’ll need to change all passwords from this configuration files (``password`` variables for most of them).

You’ll need to create a configuration file and adapt it to your infrastructure.

