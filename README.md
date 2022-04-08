# Ansible Network Collection for Fujitsu PSWITCH

## Collection contents

Collections are a distribution format for Ansible content that can include playbooks, roles, modules, and plugins, they are usually hosted and shared by a repository called [Ansible Galaxy](https://galaxy.ansible.com). The Ansible Network Collection for Fujitsu PSWITCH (fos-ansible-collection), which also has been uploaded and managed there, contains a variety of Ansible content to help automate the management for Fujitsu PSWITCHs, and you can get it in either of two ways: install from source or install from Ansible Galaxy.

## fos-ansible-collection core modules

- **fos_command.py** — Run commands in Privileged EXEC modes

- **fos_config.py** — Manage configurations in Global Config modes

- **fos_facts.py** — Collect facts

- **fos_vlan.py** — Manage configurations in VLAN Config modes

## Installation

Overall steps:

1. Install Ansible and dependency module.
2. Install fos-ansible-collection.

### Install Ansible and dependency module

Before installing fos-ansible-collection, please make sure Ansible and the dependency module are available in your environment.

Command reference:

```
pip3 install ansible --user
pip3 install paramiko --user
```

Please refer to the [Ansible official page](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible) for more information.

### Install fos-ansible-collection

There are two installation paths available: from source or from Ansible Galaxy, please choose one between them to complete the installation.

#### From source

This repository contains the entire code for fos-ansible-collection, so we can just copy the plugins to complete the installation.

Copy plugins:

```
mkdir -p ~/.ansible/collections/ansible_collections/fujitsu/fos/
cp -r plugins/ ~/.ansible/
cp -r plugins/ ~/.ansible/collections/ansible_collections/fujitsu/fos/
```

#### From Ansible Galaxy

Ansible Galaxy is a repository that hosts and shares collections, since fos-ansible-collection has been uploaded and managed there, we can install the plugins directly using ansible-galaxy command.

Install the latest version of fos-ansible-collection:

```
ansible-galaxy collection install fujitsu.fos
```

Or, install a specific version of fos-ansible-collection:

```
ansible-galaxy collection install fujitsu.fos:1.0.0
```

Available versions can be found on the [Ansible Galaxy fos-ansible-collection page](https://galaxy.ansible.com/fujitsu/fos).

Then copy plugins:

```
cp -r ~/.ansible/collections/ansible_collections/fujitsu/fos/plugins/ ~/.ansible/
```

## Version compatibility

* Ansible version 2.10 or later.
* Python 2.7 or higher and Python 3.5 or higher

## Usage

### Example
You can refer to the files in the example folder, modify the IP and other contents and execute:

```
ansible-playbook -i ./inventory ./playbook.yaml
```

Note: Before using above command, you need to ssh to the switch once to complete the key fingerprint authentication.

```
ssh username@10.10.10.10
```

```
The authenticity of host '10.10.10.10 (10.10.10.10)' can't be established.
ED25519 key fingerprint is SHA256:*******************************************.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

**inventory**

This file provides the PSWITCH connection information, such as IP address, username and password etc.

```
[host]  # The hostname you named for the PSWITCH in this file.
10.10.10.10  # The PSWITCH IP address.

[host:vars]  # The "host" here should be the same as the hostname above.
ansible_ssh_user=****  # The PSWITCH ssh username.
ansible_ssh_pass=****  # The PSWITCH ssh password for above username.
ansible_connection=network_cli  # Specify the connection method, for PSWITCH it should be "network_cli".
ansible_network_os=fos  # Specify the network OS, for PSWITCH it should be "fos".
```

**playbook.yaml**

This file contains the network content you want to configure, such as configuring interface settings, adding a port to a VLAN etc.

```
- hosts: host  # The hostname of the PSWITCH, it should be the same as in inventory.
  gather_facts: no  # Specify if the fact modules are executed in parallel or serially and in order.

  tasks:  # The task array that you want to run.
  - name: "show version"  # The task name.
    fos_command:  # This module is used to run commands on PSWITCH.
      commands:  # List of commands to send to PSWITCH.
        - show version  # Show PSWITCH version.

  - name: "get hardware fact"  # The task name.
    fos_facts:  # This module is used to collect facts from PSWITCH.
      gather_subset:  # Restrict the facts collected to a given subset.
       - "hardware"  # Given the restricted subset.

  - name: "configure interface settings"  # The task name.
    fos_config:  # This module is used to manage PSWITCH configuration.
      lines:  # The ordered set of commands that should be configured.
        - lldp transmit  # Enable lldp transmit.
        - lldp receive  # Enable lldp receive.
      parents: interface 0/16  # Specifiy the port to be configured.

  - name: "configure access port"  # The task name.
    fos_config:  # This module is used to manage PSWITCH configuration.
      lines:  # The ordered set of commands that should be configured.
        - switchport access vlan 30  # Add the port to the specific VLAN.
      parents: interface 0/36  # Specifiy the port to be configured.
```

For the complete usage of each module, please refer to the output of the following commands:

```
ansible-doc fos_command
ansible-doc fos_config
ansible-doc fos_facts
ansible-doc fos_vlan
```
