# (c) 2020 Red Hat Inc.
#
# Copyright 2020 FUJITSU LIMITED.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.fujitsu.fos.tests.unit.compat.mock import patch
from ansible_collections.fujitsu.fos.tests.unit.plugins.modules.utils import set_module_args
from .fos_module import TestFosModule, load_fixture
from ansible_collections.fujitsu.fos.plugins.modules import fos_facts


class TestFosFacts(TestFosModule):

    module = fos_facts

    def setUp(self):
        super(TestFosFacts, self).setUp()

        self.mock_run_command = patch('ansible_collections.fujitsu.fos.plugins.modules.fos_facts.run_commands')
        self.run_command = self.mock_run_command.start()

    def tearDown(self):
        super(TestFosFacts, self).tearDown()
        self.mock_run_command.stop()

    def load_fixtures(self, commands=None):

        def load_from_file(*args, **kwargs):
            module = args
            commands = kwargs['commands']
            output = list()

            for item in commands:
                try:
                    obj = json.loads(item)
                    command = obj['command']
                except ValueError:
                    command = item
                filename = str(command).replace(' ', '_')
                output.append(load_fixture('fos_facts', filename))
            return output

        self.run_command.side_effect = load_from_file

    def test_fos_facts_gather_subset_default(self):
        set_module_args({'gather_subset': 'default'})
        result = self.execute_module()
        ansible_facts = result['ansible_facts']
        self.assertIn('default', ansible_facts['ansible_net_gather_subset'])
        self.assertIn('1.3.67', ansible_facts['ansible_net_runtime_version'])
        self.assertIn('1.0.0', ansible_facts['ansible_net_bootloader_version'])
        self.assertEquals('admin', ansible_facts['ansible_net_hostname'])

    def test_fos_facts_gather_subset_config(self):
        set_module_args({'gather_subset': 'config'})
        result = self.execute_module()
        ansible_facts = result['ansible_facts']
        self.assertIn('default', ansible_facts['ansible_net_gather_subset'])
        self.assertIn('config', ansible_facts['ansible_net_gather_subset'])
        self.assertEquals('admin', ansible_facts['ansible_net_hostname'])
        self.assertIn('ansible_net_config', ansible_facts)

    def test_fos_facts_gather_subset_hardware(self):
        set_module_args({'gather_subset': 'hardware'})
        result = self.execute_module()
        ansible_facts = result['ansible_facts']
        self.assertIn('default', ansible_facts['ansible_net_gather_subset'])
        self.assertIn('hardware', ansible_facts['ansible_net_gather_subset'])
        self.assertEquals(1328, ansible_facts['ansible_net_memfree_mb'])
        self.assertEquals(3949, ansible_facts['ansible_net_memtotal_mb'])
        self.assertEquals('ET-7648BRA-FOS', ansible_facts['ansible_net_model'])
        self.assertEquals('00:30:AB:F4:CA:DA', ansible_facts['ansible_net_burned_in_mac'])
