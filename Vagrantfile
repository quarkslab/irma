# -*- mode: ruby -*-
# vi: set ft=ruby :

env = ENV.has_key?('VM_ENV') ? ENV['VM_ENV'] : "allinone"
code_path = ENV.has_key?('VM_PATH') ? ENV['VM_PATH'] : "../irma-frontend"

nodes_config = (JSON.parse(File.read(File.dirname(__FILE__) + "/environments/#{env}.json")))['nodes']
ansible_config = (JSON.parse(File.read(File.dirname(__FILE__) + "/environments/#{env}.json")))['ansible']

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v, override|
    config.vm.box = "chef/debian-7.4"
  end

  nodes_config.each do |node|
    node_name = node[0]
    node_values = node[1]

    config.vm.define node_name do |vm_config|
      vm_config.vm.hostname = node_values['hostname']

      if node_values['ip']
        print node_values['ip'], "\n"
        vm_config.vm.network "private_network", ip: node_values['ip']
      end

      if node_values['share_code']
        vm_config.vm.synced_folder code_path, "/var/www/prod.project.local/current", type: "rsync", owner: 'www-data', group: 'www-data', rsync__exclude: [
            ".git/",
            "venv/",
          ]
      end
    end

    #config.vm.provider "virtualbox" do |v|
      #v.gui = true
    #end
  end

  config.vm.provision :ansible do |ansible|
    ansible.playbook = 'playbook.yml'

    ansible.extra_vars = {
      vagrant: ansible_config['vagrant'],
      remote_user: ansible_config['user']
    }

    ansible.groups = ansible_config['groups']

    # ansible.tags = ['']
    # ansible.skip_tags = ['']
    # ansible.verbose = 'vvvv'
    # ansible.raw_arguments = ['--check','--diff']
  end

  config.ssh.forward_agent = true
end
