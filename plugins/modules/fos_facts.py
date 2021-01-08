#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2020 FUJITSU LIMITED.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fos_facts
version_added: "2.10"
short_description: Collect facts from remote devices running FUJITSU PSWITCH
description:
  - Collects a base set of device facts from a remote device that
    is running PSWITCH.  This module prepends all of the
    base network fact keys with C(ansible_net_<fact>).  The facts
    module will always collect a base set of facts from the device
    and can enable or disable collection of additional facts.
options:
  gather_subset:
    description:
      - When supplied, this argument will restrict the facts collected
        to a given subset.  Possible values for this argument include
        all, hardware, config, and interfaces.  Can specify a list of
        values to include a larger subset.  Values can also be used
        with an initial C(M(!)) to specify that a specific subset should
        not be collected.
    default: [ '!config' ]
    type: list
"""

EXAMPLES = """
# Collect all facts from the device
- fos_facts:
    gather_subset: all

# Collect only the config and default facts
- fos_facts:
    gather_subset:
      - config

# Do not collect hardware facts
- fos_facts:
    gather_subset:
      - "!hardware"
"""

RETURN = """
ansible_net_gather_subset:
  description: The list of fact subsets collected from the device
  returned: always
  type: list

#default
ansible_net_runtime_version:
  description: The current runtime version of the remote device
  returned: always
  type: str
ansible_net_bootloader_version:
  description: The bootloader version of the remote device
  returned: always
  type: str
ansible_net_hostname:
  description: The configured hostname of the device
  returned: always
  type: str

#hardware
ansible_net_memfree_mb:
  description: The available free memory on the remote device in Mb
  returned: when hardware is configured
  type: int
ansible_net_memtotal_mb:
  description: The total memory on the remote device in Mb
  returned: when hardware is configured
  type: int
ansible_net_model:
  description: The model name returned from the device
  returned: always
  type: str
ansible_net_burned_in_mac:
  description: The burned in mac of the remote device
  returned: always
  type: str

# config
ansible_net_config:
  description: The current active config from the device
  returned: when config is configured
  type: str

"""

import re

from ansible_collections.fujitsu.fos.plugins.module_utils.network.fos import run_commands
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible.module_utils.six.moves import zip


class FactsBase(object):

    COMMANDS = list()

    def __init__(self, module):
        self.module = module
        self.facts = dict()
        self.responses = None

    def populate(self):
        self.responses = run_commands(self.module, commands=self.COMMANDS, check_rc=False)

    def run(self, cmd):
        return run_commands(self.module, commands=cmd, check_rc=False)


class Default(FactsBase):

    COMMANDS = ['show version', 'show hosts']

    def populate(self):
        super(Default, self).populate()
        data = self.responses[0]
        if data:
            self.facts['runtime_version'] = self.parse_runtime_version(data)
            self.facts['bootloader_version'] = self.parse_bootloader_version(data)

        data = self.responses[1]
        if data:
            self.facts['hostname'] = self.parse_hostname(data)

    def parse_runtime_version(self, data):
        match = re.search(r'Current Runtime Version[\.]+ \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_bootloader_version(self, data):
        match = re.search(r'Bootloader Version[\.]+ \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_hostname(self, data):
        match = re.search(r'Host name[\.]+ \s*(.+)', data, re.M)
        if match:
            return match.group(1)


class Hardware(FactsBase):

    COMMANDS = [
        'show process cpu',
        'show hardware'
    ]

    def populate(self):
        super(Hardware, self).populate()
        data = self.responses[0]
        if data:
            memalloc = self.parse_memallocate_mb(data)
            memfree = self.parse_memfree_mb(data)
            self.facts['memtotal_mb'] = (int(memalloc) + int(memfree)) // 1024
            self.facts['memfree_mb'] = int(memfree) // 1024

        data = self.responses[1]
        if data:
            self.facts['type'] = self.parse_machine_type(data)
            self.facts['model'] = self.parse_machine_model(data)
            self.facts['serial_bunber'] = self.parse_serial_number(data)
            self.facts['burned_in_mac'] = self.parse_burned_in_mac_address(data)

    def parse_memfree_mb(self, data):
        match = re.search(r'free      \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_memallocate_mb(self, data):
        match = re.search(r'alloc     \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_machine_type(self, data):
        match = re.search(r'Machine Type[\.]+ \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_machine_model(self, data):
        match = re.search(r'Machine Model[\.]+ \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_serial_number(self, data):
        match = re.search(r'Serial Number[\.]+ \s*(.+)', data)
        if match:
            return match.group(1)

    def parse_burned_in_mac_address(self, data):
        match = re.search(r'Burned In MAC Address[\.]+ \s*(.+)', data)
        if match:
            return match.group(1)


class Config(FactsBase):

    COMMANDS = ['show running-config']

    def populate(self):
        super(Config, self).populate()
        data = self.responses[0]
        if data:
            self.facts['config'] = data


FACT_SUBSETS = dict(
    default=Default,
    hardware=Hardware,
    config=Config,
)

VALID_SUBSETS = frozenset(FACT_SUBSETS.keys())

warnings = list()


def main():
    argument_spec = dict(
        gather_subset=dict(default=['!config'], type='list')
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    gather_subset = module.params['gather_subset']

    runable_subsets = set()
    exclude_subsets = set()

    for subset in gather_subset:
        if subset == 'all':
            runable_subsets.update(VALID_SUBSETS)
            continue

        if subset.startswith('!'):
            subset = subset[1:]
            if subset == 'all':
                exclude_subsets.update(VALID_SUBSETS)
                continue
            exclude = True
        else:
            exclude = False

        if subset not in VALID_SUBSETS:
            module.fail_json(msg='Bad subset')

        if exclude:
            exclude_subsets.add(subset)
        else:
            runable_subsets.add(subset)

    if not runable_subsets:
        runable_subsets.update(VALID_SUBSETS)

    runable_subsets.difference_update(exclude_subsets)
    runable_subsets.add('default')

    facts = dict()
    facts['gather_subset'] = list(runable_subsets)

    instances = list()
    for key in runable_subsets:
        instances.append(FACT_SUBSETS[key](module))

    for inst in instances:
        inst.populate()
        facts.update(inst.facts)

    ansible_facts = dict()
    for key, value in iteritems(facts):
        key = 'ansible_net_%s' % key
        ansible_facts[key] = value

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()
