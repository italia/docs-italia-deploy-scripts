# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.network "forwarded_port", guest: 80, host: 8880

  config.vm.define "default"
  config.vm.provision "ansible" do |ansible|
    ansible.verbose = "v"
    ansible.playbook = "vagrant.yml"
    ansible.host_vars = {
      "default" => {"ansible_python_interpreter" => "/usr/bin/python3"}
    }
  end
end
