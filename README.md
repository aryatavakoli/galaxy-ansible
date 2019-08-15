# BCCDC Galaxy-Ansible

#### Python 2.7 must be installed on the client machine that Galaxy will be deployed to.

**NOTE: These scripts only work on an Instance of CentOS 7. These Scripts will also disable SElinux**

Currently Functional Features:
- [x] Galaxy
- [x] miniconda
- [x] Tool-shed Imports
- [x] PostgreSQL
- [x] nginx
- [x] certbot
- [x] supervisor
- [ ] Galaxy-tools (Functional but needs to be reworked)
- [ ] SGE
- [ ] Interactive Enviroments
- [ ] ProFTP
- [ ] IRIDA Importer tool

## Table of Contents
- [Overview](#-overview)
	- [Scripts at a high level](#-scripts-at-a-high-level)
	- [Additional Info](#-additional-info)
- [Terminology](#-terminology)
- [Variables](#-variables)
	- [What they are](#-what-they-are)
- [Testing](#-testing)
- [Deploying](#-running)
- [Special Thanks](#-thanks)


### <a name="-scripts-at-a-high-level"></a> Scripts at a high level

A detailed explanation of each variable and their function will be discussed in the next section.

At a high level, the `galaxy.yml` does the following:

- The Ansible Playbook is executed on the target machine
    - Sets up CentOS via `centos-prep.yml`
        - Installs any required software.
        - Installs software to monitor the system. 
    - Disables `SElinux`
	- Enables `firewalld`
	- Creates, installs and enables postgresql if `create_db == true`
        - Done via the `galaxyproject.postgresql` and `natefoo.postgresql_objects` roles
        - Creates the `galaxy_user` for the database
	- Installs Galaxy
        - Done via the `galaxyproject.galaxy` role
        - Clone release of Galaxy specified by `galaxy_commit_id`
        - Automatically sets up several default variables.
 	- Installs Miniconda
		- Done via the `uchida.miniconda` role
    - Installs Supervisor
        - Done via the `usegalaxy-eu.supervisor`
        - Templates over configs
        - Makes `galaxy_user` the owner of `/var/run/supervisor`
        - Add Galaxy entry to supervisor's config
 	- Installs Nginx
		- Done via the `galaxyproject.nginx`
		- Install nginx configs, including configuration for serving Galaxy
		- Grant permissions
		- Add nginx entry to supervisor's config (TODO)
	- Installs Tools listed in `files/irida_tools_list.yml` if `galaxy_tool_list == true`
    - Uses pip to install `uWSGI` into the directory defined by `galaxy_venv_dir`


### <a name="-additional-info"></a> Additional info

The code that each role was based off of can be accessed below:
- [galaxyproject.galaxy](https://github.com/galaxyproject/ansible-galaxy)
- [galaxyproject.galaxy-tools](https://github.com/galaxyproject/ansible-galaxy-tools)
- [galaxyproject.interactive_environments](https://github.com/galaxyproject/ansible-interactive-environments)
- [galaxyproject.nginx](https://github.com/galaxyproject/ansible-nginx)
- [galaxyproject.postgresql](https://github.com/galaxyproject/ansible-postgresql)
- [natefoo.postgresql_objects](https://github.com/natefoo/ansible-postgresql-objects)
- [usegalaxy-eu.supervisor](https://github.com/usegalaxy-eu/ansible-role-supervisor)
- [usegalaxy-eu.certbot](https://github.com/usegalaxy-eu/ansible-certbot)
- [uchida.miniconda](https://github.com/uchida/ansible-miniconda-role)

## <a name="-variables"></a> Variables
### <a name="-what-they-are"></a> What they are
Variables for this ansible playbook can be found in `group_vars/galaxyserver.yml`. Some of these variables, what they do, and their default values are listed below. For a more comprehensive overview of these variables, refer to the README or `default/main.yml` in the `galaxyproject.galaxy` role

### Global Variables

These Variables **must** be defined before running the playbook

Variable Name                                | Default Value                                                       | Usage
---                                          | ---                                                                 | ---
`galaxy_release_number`              | `19.05`                                                             | The release *number* of Galaxy to be checked out; by default this value is appended to `release_` and then checked out.
`galaxy_user_name`                        | `galaxy`                                                            | The name of the user that will run Galaxy.
`galaxy_user_group`                  | `galaxy`                                                         | A group of `galaxy_user`. Most Galaxy files created by this module will belong to this group.
`install_path`                  | `/srv/galaxy`                                                         | The root directory where Galaxy is to be installed. Defines `galaxy_root` in `galaxyservers.yml`. The Galaxy role automatically uses `galaxy_root` to define `galaxy_server_dir`, `galaxy_venv_dir`, and `galaxy_config_dir`.
`uwsgi_socket`                  | `127.0.0.1:8080`                                                         | The IP address and the port that Galaxy listens to. Defines `uwsgi_pass` in `templates/nginx/galaxy.j2` and `socket` in `galaxyservers.yml`
`server_name`                  |`{{inventory_hostname}}`                                                         |  Name of the Galaxy server. Used to populate the `server_name` field in `galaxyservers.yml`, and the `config.ini` file. The default value will just assign `server_name` to the entries in `hosts` files. The default value is recommended.
`galaxy_admin_emails`                 | `[empty string]`                                                    | The list of admin account emails, separated by commas, to put in the `admin_users` section of the `galaxyservers.yml` file.
`default_admin_api_key`                 | `[empty string]`                                                    | The Galaxy master API key to be put into the `galaxyservers.yml` file. Only required if `galaxy_tools_install_tools == yes`


### Boolean Variables

These should be defined depending on your current Galaxy setup.

Variable Name                                | Default Value                                                       | Usage
---                                          | ---                                                                 | ---
`galaxy_create_user`                 | `true`                                                             | Whether or not to create user `galaxy_user`. Set to `false` if user is managed through something like LDAP and/or another module.
`galaxy_tools_install_tools`                          | `yes`                                                             | Whether or not to install the tools listed in `galaxy_tool_list` via Ephemeris. This determies if the `galaxyproject.galaxy-tools` role should be run or skipped
`create_db`                          | `false`                                                             | Determines if PostgreSQL should be installed on the server. This determines if `galaxyproject.postgresql` and `natefoo.postgresql_objects` roles are run or skipped.

### Galaxy Variables

Other variables Galaxy uses. The defaults for these can be found in the `defaults/main.yml` of `galaxyproject.galaxy`.

Variable Name                                | Default Value                                                       | Usage
---                                          | ---                                                                 | ---
`galaxy_root`                    | `{{install_path}}`                                         | The root directory for the Galaxy instance to be installed to.
`galaxy_server_dir`                  | `{{galaxy_root}}/server`                                  | The directory that the Galaxy repo is checked out into, and that Galaxy is run from.
`galaxy_commit_id`                     | `release_{{galaxy_release_number}}`                           | The branch of Galaxy to ensure is installed. It is better to just set `galaxy_release_number` and leave this as its default value unless the branch in not in the form of `release_xx.xx`.
`galaxy_config_dir`                  | `{{galaxy_root}}/config`                                  | The directory containing all of the managed config files.
`galaxy_database_connection`         | `postgresql:///{{galaxy_user_name}}?host=/var/run/postgresql` | The address to the main database for Galaxy to use.
`galaxy_venv_dir`                           | `{{galaxy_root}}/venv`                                    | The location of the virtual environment Galaxy will run from within.

## <a name="-testing"></a> Testing

Currently, testing is done via Vagrant. Installation of Vagrant, Ansible, and Virtualbox on your local machine can be found [here](https://github.com/aryatavakoli/kubernetes-vagrant)

### The Vagrantfile
All configurations for the testing enviroment are found in the `Vagrantfile`.

### Mapping IP Address and Hostname of the Vagrant VM
This line has to be added to `etc/hosts`:
```sh 
192.168.50.12 galaxyservers.test.ca
```
Alternatively, modify your hosts file automatically by installing [landrush](https://github.com/vagrant-landrush/landrush) with:
```sh 
$ vagrant plugin install landrush
```
### Run the playbook on Vagrant
```sh
$ vagrant up
```
## <a name="-running"></a> Deploying to a Remote Node

A SSH Key-pair must be generated for your machine and the Remote node. A good guide can be found [here](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-centos7)

### Clone this repo
```sh
$ git clone https://github.com/aryatavakoli/bccdc-galaxy-ansible.git
```

### Change Directory to this repo
```sh
$ cd bccdc-galay-ansible
```

### Add the hostname of your remote nodes to hosts

```sh
$ nano hosts
```
Add hostnames here:
```sh
[galaxyservers]
galaxyservers.test.ca #Vagrant VM
<Add Hostnames here>
```

### Install required roles to run playbook
```sh
$ ansible-galaxy install -r requirements.yml
```

Many of the roles here are derviced from the [this galaxy tutorial](https://galaxyproject.github.io/training-material/topics/admin/tutorials/ansible-galaxy/tutorial.html)

### Deploy and run playbook
```sh
$ ansible-playbook -i hosts galaxy.yml
```
