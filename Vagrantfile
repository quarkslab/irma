# -*- mode: ruby -*-
# vi: set ft=ruby :

env = ENV.has_key?('VM_ENV') ? ENV['VM_ENV'] : "allinone"
code_path = ENV.has_key?('VM_PATH') ? ENV['VM_PATH'] : "../irma-frontend"

require File.dirname(__FILE__) + "/environments/#{env}.rb"

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |v, override|
    config.vm.box = "chef/debian-7.4"
  end

  VirtualMachines::VMS.each do |host|
    config.vm.define host[:name] do |vm_config|
      vm_config.vm.hostname = host[:hostname]

      if host[:network]
        print host[:network], "\n"
        vm_config.vm.network "private_network", ip: host[:network]
      end

      if host[:share_code]
        vm_config.vm.synced_folder code_path, "/var/www/prod.project.local/current", type: "rsync", owner: 'www-data', group: 'www-data', rsync__exclude: [
            ".git/",
          ]
      end
    end

    #config.vm.provider "virtualbox" do |v|
      #v.gui = true
    #end

    config.vm.provision :ansible do |ansible|
      ansible.playbook = 'playbook.yml'
      ansible.extra_vars = {
        vagrant: host[:ansible_vagrant],
        remote_user: host[:ansible_user]
      }

      # ansible.tags = ['']
      # ansible.skip_tags = ['']
      # ansible.verbose = 'vvvv'
      # ansible.raw_arguments = ['--check','--diff']
    end
  end

  config.ssh.forward_agent = true
end
