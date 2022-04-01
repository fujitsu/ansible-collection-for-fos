# Ansible Network Collection for Fujitsu PSWITCH

## Collection contents

Collections are a distribution format for Ansible content that can include playbooks, roles, modules, and plugins. The Ansible Network Collection for Fujitsu PSWITCH (fos-ansible-collection) includes a variety of Ansible content to help automate the management of Fujitsu PSWITCHS.

## fos-ansible-collection core modules

- **fos_command.py** — Run commands in Privileged EXEC modes

- **fos_config.py** — Manage configurations in Global Config modes

- **fos_facts.py** — Collect facts

- **fos_vlan.py** — Manage configurations in Vlan Config modes

## Installation

### Install Ansible and dependency module

```
pip3 install ansible --user
pip3 install paramiko --user
```

Detailed information can be found on the [official page](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible).

### Install fos-ansible-collection

#### From source

This repository contains the entire code for fos-ansible-collection, so we can just copy the plugins to complete the installation.

Copy plugins
```
mkdir -p ~/.ansible/collections/ansible_collections/fujitsu/fos/
cp -r plugins/ ~/.ansible/
cp -r plugins/ ~/.ansible/collections/ansible_collections/fujitsu/fos/
```

#### From Ansible Galaxy

Ansible Galaxy is a repository that hosts and shares collections, since fos-ansible-collection has been uploaded and managed there, we can install the plugins directly using ansible-galaxy command.

Install the latest version of fos-ansible-collection
```
ansible-galaxy collection install fujitsu.fos
```

Install a specific version of fos-ansible-collection
```
ansible-galaxy collection install fujitsu.fos:1.0.0
```

Available versions can be found on the [fos-ansible-collection page of Ansible Galaxy](https://galaxy.ansible.com/fujitsu/fos).

Copy plugins
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

```
[host]
10.10.10.10

[host:vars]
ansible_ssh_user=****
ansible_ssh_pass=****
ansible_connection=network_cli
ansible_network_os=fos
```

**playbook.yaml**

```
- hosts: host
  gather_facts: no

  tasks:
  - name: "show version"
    fos_command:
      commands:
        - show version

  - name: "get hardware fact"
    fos_facts:
      gather_subset:
       - "hardware"

  - name: "configure interface settings"
    fos_config:
      lines:
        - lldp transmit
        - lldp receive
      parents: interface 0/16

  - name: "configure access port"
    fos_config:
      lines:
        - switchport access vlan 30
      parents: interface 0/36
```
