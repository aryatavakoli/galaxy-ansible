# BCCDC Galaxy-Ansible

#### Python 2.7 must be installed on the client machine that Ansible will deploy to.

**NOTE: These scripts only work on an Instance of CentOS 7. These Scripts will also disable SElinux**

## Table of Contents
- [Overview](#-overview)
	- [Scripts at a high level](#-scripts-at-a-high-level)
	- [Additional Info](#-additional-info)
- [Terminology](#-terminology)
- [Variables](#-variables)
	- [What they are](#-what-they-are)
	- [Where they go](#-where-they-go)
- [Installation](#-installation)
	- [Preparing the server](#-preparing-the-server)
	- [Running the scripts](#-running-the-scripts)
	- [Making sure it worked](#-making-sure-it-worked)
- [File Structure](#-file-structure)
- [Testing](#-testing)


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

Variable Name                                | Default Value                                                       | Usage
---                                          | ---                                                                 | ---
`create_db`                          | `false`                                                             | Whether or not a database should be created at the default.
`galaxy_admin_users`                 | `[empty string]`                                                    | The list of admin account emails, separated by commas, to put in the `admin_users` section of the `galaxy.yml` file.
`galaxy_root`                    | `/srv/galaxy`                                         | The root directory for the Galaxy instance to be installed to.
`galaxy_server_dir`                  | `{{galaxy_root}}/server`                                  | The directory that the Galaxy repo is checked out into, and that Galaxy is run from.
`galaxy_tool_list`                   | `[empty string]`                                                    | The list of tools, in a YAML format, to install to the Galaxy instance via Ephemeris. Tools are only installed if `install_tools == true`.
`galaxy_user`                        | `galaxy`                                                            | The name of the user that will run Galaxy.
`galaxy_user_group`                  | `galaxy`                                                         | A group of `galaxy_user`. Most Galaxy files created by this module will belong to this group.
`galaxy_commit_id`                     | `release_{{galaxy_release_number}}`                           | The branch of Galaxy to ensure is installed. It is better to just set `galaxy_release_number` and leave this as its default value unless the branch in not in the form of `release_xx.xx`.
`install_tools`                      | `false`                                                             | Whether or not to install the tools listed in `galaxy_tool_list` via Ephemeris.
`galaxy_api_key`                     | `''`                                                          | The Galaxy master API key to be put into the galaxy.yml config.
`galaxy_config_dir`                  | `{{galaxy_root}}/config`                                  | The directory containing all of the managed config files.
`galaxy_create_user`                 | `true`                                                             | Whether or not to create user `galaxy_user`. Set to `false` if user is managed through something like LDAP and/or another module.
`galaxy_database_connection`         | `postgresql:///{{galaxy_user_name}}?host=/var/run/postgresql` | The address to the main database for Galaxy to use.
`galaxy_release_number`              | `19.05`                                                             | The release *number* of Galaxy to be checked out; by default this value is appended to `release_` and then checked out.
`server_name`                        | `galaxy.ca`                                            | Name of the Galaxy server. Used to populate the `server_name` field in galaxy.yml, and the `config.ini` file used by the irida_import tool.
`galaxy_venv_dir`                           | `{{galaxy_root}}/venv`                                    | The location of the virtual environment Galaxy will run from within.
`ldap_enable`                          | `false`                                                             | Whether or not LDAP will be used for authorization and authenticationL.
`ldap_server`                          | `[empty string]`                                                             | Location of LDAP server
`ldap_search_user`                          | `[empty string]`                                                             | Search user name for LDAP server
`ldap_search_password`                          | `[empty string]`                                                             | Search user name password for LDAP server
`ldap_search_base`                          | `[empty string]`                                                             | Search base for LDAP server
`ldap_domain`                          | `[empty string]`                                                            | Domain for LDAP server
