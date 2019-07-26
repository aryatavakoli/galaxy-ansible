IMAGE = "centos/7"
Vagrant.configure("2") do |config|

  config.vm.provider "virtualbox" do |v|
    v.memory = 4096
    v.cpus = 4
  end

  # config.vbguest.auto_update = false
  # config.vm.synced_folder "./bccdc-galaxy-ansible", "/etc/ansible/", type: "rsync",
  #   rsync__exclude: ".git/"

  config.vm.define "galaxyservers" do |c|
    c.vm.box = IMAGE
    c.vm.hostname = "galaxyservers.test.ca"
    c.vm.network "private_network", ip: "192.168.50.12"
  end
    
config.vm.provision "shell", :inline => <<-SHELL
  yum update
  yum install -y python
SHELL

config.vm.provision 'ansible' do |ansible|
    ansible.become = true
    ansible.compatibility_mode = "2.0"
    ansible.config_file = 'ansible.cfg'
    ansible.inventory_path = 'hosts'
    ansible.galaxy_role_file = 'requirements.yml'
    ansible.galaxy_roles_path = 'roles'
    ansible.galaxy_command = 'ansible-galaxy install --role-file=%{role_file} --roles-path=%{roles_path} --force'
    ansible.playbook = "galaxy.yml"
  end
end
