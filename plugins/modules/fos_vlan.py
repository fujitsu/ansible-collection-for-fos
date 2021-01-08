#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2020 FUJITSU LIMITED.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: fos_vlan
version_added: "2.10"
short_description: Manage FUJITSU PSWITCH Vlan Config
description:
- This module provides declarative management of VLANs on Fujitsu PSWITCH network devices.
options:
  commands:
    description:
      - List of commands to send to the remote PSWITCH device over the
        configured provider. The resulting output from the command
        is returned.
    type: list
    required: true
"""

EXAMPLES = """
- name: Create vlan
  fos_vlan:
    commands:
      - vlan 4000

- name: Create vlan
  fos_vlan:
    commands:
      - vlan name 4000 test
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - vlan 4000
    - vlan name 4000 test
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.fujitsu.fos.plugins.module_utils.network.fos import get_connection


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        commands=dict(type='list', required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    warnings = list()

    result = {"changed": False}

    if warnings:
        result["warnings"] = warnings

    connection = get_connection(module)
    commands = module.params['commands']
    result["commands"] = commands

    if not module.check_mode:
        if commands:
            connection.edit_vlan(candidate=commands)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
