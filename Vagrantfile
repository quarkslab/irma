# -*- mode: ruby -*-
# vi: set ft=ruby :

env = ENV.has_key?('VM_ENV') ? ENV['VM_ENV'] : "dev"

require 'yaml'
configuration = YAML.load_file(File.dirname(__FILE__) + "/environments/#{env}.yml")
servers = configuration['servers']
ansible_config = configuration['ansible_config']

# set minimal Vagrant version
Vagrant.require_version ">= 1.1.0"

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v, override|
    config.vm.box = "chef/debian-7.4"
  end

  config.ssh.forward_agent = true

  servers.each do |server|
    config.vm.define server['name'] do |machine|
      machine.vm.hostname = server['hostname']

      if server['ip']
        print server['ip'], "\n"
        machine.vm.network "private_network", ip: server['ip']
      end

      if server['share_code']
        machine.vm.synced_folder server["share_from"], server["share_to"], type: "rsync", owner: server['share_user'], group: server['share_group'], rsync__exclude: server["share_exclude"]
      end
    end
  end

  config.vm.provision :ansible do |ansible|
    ansible.playbook = 'playbook.yml'
    ansible.extra_vars = ansible_config['extra_vars']
    ansible.groups = ansible_config['groups']
    ansible.limit = 'all'

    # ansible.tags = ['']
    # ansible.skip_tags = ['']
    # ansible.verbose = 'vvvv'
    # ansible.raw_arguments = ['--check','--diff']
  end
end
