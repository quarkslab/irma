IRMA Ansible Provisioning
=========================

Requirements
------------

This playbook requires Ansible 1.6 or higher. It has been tested for Debian 7 system.

Another requirements:
- Users role from [mivok/ansible-users](https://github.com/mivok/ansible-users)
- OpenSSH role from [Ansibles/openssh](https://github.com/Ansibles/openssh)
- NodeJS role from [JasonGiedymin/nodejs](https://github.com/AnsibleShipyard/ansible-nodejs)
- Nginx role from [jdauphant/ansible-role-nginx](https://github.com/jdauphant/ansible-role-nginx)
- uWSGI role from [gdamjan/ansible-uwsgi](https://github.com/gdamjan/ansible-uwsgi)
- MongoDB role from [Stouts/Stouts.mongodb](https://github.com/Stouts/Stouts.mongodb)


Installation
------------

To install dependencies (see requirements), simply run:

```
$ ansible-galaxy install -r galaxy.yml -p ./roles
```


### Vagrant

If you’re interesting in using [Vagrant](http://vagrantup.com), be sure to have the following directory layout:

```
...
|
+--- irma-frontend
|
+--- irma-ansible-provisioning
```

To initialize and provision the Virtualbox VM, run in the irma-ansible-provisioning directory `vagrant up`.

/!\ Make sure you’ve got a `config/frontend.ini` file up to date, before provisioning. An example file is available there:
`config/frontend.ini.sample`.

Then, you’ll need to manually “deploy” the application, run `vagrant ssh` to connect to the VM, and then:
```
$ sudo su www-data
$ cd /var/wwww/prod.project.local/current

  # API Installation
$ virtualenv venv
$ venv/bin/pip install -r install/requirements.txt

  # Web application installation
$ cd web
$ npm install
$ node_modules/.bin/bower install
$ node_modules/.bin/gulp dist
```

Then, for proper use, update your `/etc/hosts` file and add:
```
172.16.1.30    www.allinone.irma.local
```

Then, with your web browser, IRMA allinone is available at [www.allinone.irma.local](http://www.allinone.irma.local).


Configuration
-------------

You need to add your public SSH key to the file `vars/defaults.yml` (in the `users : ssh_key` section) to be able to connect as `www-data` on the instance.
