# Ansible Network Collection for Fujitsu PSWITCH

## Collection contents

The Ansible Network Collection for Fujitsu PSWITCH includes a variety of Ansible content to help automate the management of Fujitsu PSWITCHS.

## Collection core modules

- **fos_command.py** — Run commands in Privileged EXEC modes

- **fos_config.py** — Manage configurations in Global Config modes

- **fos_facts.py** — Collect facts

- **fos_vlan.py** — Manage configurations in Vlan Config modes


## Installation
### From source

The [fujitsu/ansible-collection-for-fos repository](https://github.com/fujitsu/ansible-collection-for-fos) contains the code for the collection.

Install ansible.netcommon
```
ansible-galaxy collection install ansible.netcommon
```

Copy plugins
```
mkdir -p ~/.ansible/collections/ansible_collections/fujitsu/fos/
cp -r plugins/ ~/.ansible/
cp -r plugins/ ~/.ansible/collections/ansible_collections/fujitsu/fos/
```

### From Ansible Galaxy

Install the latest version of fos-ansible-collection
```
ansible-galaxy collection install fujitsu.fos
```

Install a specific version of fos-ansible-collection
```
ansible-galaxy collection install fujitsu.fos:1.0.0
```

Copy plugins
```
cp -r ~/.ansible/collections/ansible_collections/fujitsu/fos/plugins/ ~/.ansible/
```

## Version compatibility

* Ansible version 2.10 or later.
* Python 2.7 or higher and Python 3.5 or higher

## Using this collection

### Example
You can refer to the files in the example folder, modify the IP and other contents and execute:

```
ansible-playbook -i ./inventory ./playbook.yaml
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
```
