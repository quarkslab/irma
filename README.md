IRMA Ansible Provisioning
================================

Requirements
------------

This playbook requires Ansible 1.6 or higher. It has been tested for Debian 7 system.

Another requirements:
- Users role from [mivok/ansible-users](https://github.com/mivok/ansible-users)
- OpenSSH role from [Ansibles/openssh](https://github.com/Ansibles/openssh)
- NodeJS role from [JasonGiedymin/nodejs](https://github.com/AnsibleShipyard/ansible-nodejs)
- Nginx role from [jdauphant/ansible-role-nginx](https://github.com/jdauphant/ansible-role-nginx)


Installation
------------

Run:
```
$ ansible-galaxy install -r galaxy.yml -p ./roles
```

Configuration
-------------

You need to add your public SSH key to the file `vars/defaults.yml` (in the `users : ssh_key` section) to be able to connect as `www-data` on the instance.


Execution using Vagrant
-----------------------

Run:
```
$ vagrant up
```
