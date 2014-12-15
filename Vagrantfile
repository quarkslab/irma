# -*- mode: ruby -*-
# vi: set ft=ruby :

env = ENV.has_key?('VM_ENV') ? ENV['VM_ENV'] : "allinone_prod"

require 'yaml'
configuration = YAML.load_file(File.dirname(__FILE__) + "/environments/#{env}.yml")
servers = configuration['servers']
ansible_config = configuration['ansible_config'] || false

# set minimal Vagrant version
Vagrant.require_version ">= 1.5.0"

Vagrant.configure("2") do |config|
  config.ssh.forward_agent = true
  # see https://twitter.com/mitchellh/status/525704126647128064
  config.ssh.insert_key = false

  # Plugins section
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :machine
  end

  if Vagrant.has_plugin?("vagrant-vbguest")
    if ["demo"].include? env
      config.vbguest.no_install = true
    end
  end

  # Multi machine environment
  servers.each do |server|
    config.vm.define server['name'] do |machine|
      machine.vm.hostname = server['hostname']
      machine.vm.box = server['box']
      machine.vm.synced_folder '.', '/vagrant', disabled: true

      if server['ip']
        print server['ip'], "\n"
        machine.vm.network "private_network", ip: server['ip']
      end

      if server.has_key?('shares')
        server['shares'].each do |share|
          machine.vm.synced_folder share["share_from"], share["share_to"], type: "rsync", owner: share['share_user'], group: share['share_group'], rsync__exclude: share["share_exclude"]
        end
      end


      # Providers specific section
      machine.vm.provider "virtualbox" do |v|
        #v.gui = true
        v.cpus = server['cpus'] || 1
        v.memory = server['memory'] || 1024
        v.customize ["modifyvm", :id, "--cpuexecutioncap", server['cpuexecutioncap'] || 50]
      end
    end
  end

  if ansible_config
    config.vm.provision :ansible do |ansible|
      ansible.playbook = 'playbooks/playbook.yml'
      ansible.extra_vars = ansible_config['extra_vars']
      ansible.groups = ansible_config['groups']
      ansible.limit = 'all'

      #ansible.tags = ['']
      #ansible.skip_tags = ['']
      #ansible.verbose = 'vvvv'
      #ansible.raw_arguments = ['--check','--diff']
    end
  end
end
