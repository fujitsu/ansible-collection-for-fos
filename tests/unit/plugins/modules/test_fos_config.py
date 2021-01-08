#
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

from ansible_collections.fujitsu.fos.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.fujitsu.fos.plugins.modules import fos_config
from ansible_collections.fujitsu.fos.plugins.cliconf.fos import Cliconf
from ansible_collections.fujitsu.fos.tests.unit.plugins.modules.utils import set_module_args
from .fos_module import TestFosModule, load_fixture


class TestFosConfigModule(TestFosModule):

    module = fos_config

    def setUp(self):
        super(TestFosConfigModule, self).setUp()

        self.mock_get_config = patch('ansible_collections.fujitsu.fos.plugins.modules.fos_config.get_config')
        self.get_config = self.mock_get_config.start()

        self.mock_load_config = patch('ansible_collections.fujitsu.fos.plugins.modules.fos_config.load_config')
        self.load_config = self.mock_load_config.start()

        self.mock_get_connection = patch('ansible_collections.fujitsu.fos.plugins.modules.fos_config.get_connection')
        self.get_connection = self.mock_get_connection.start()

        self.conn = self.get_connection()
        self.conn.edit_config = MagicMock()

        self.mock_run_commands = patch('ansible_collections.fujitsu.fos.plugins.modules.fos_config.run_commands')
        self.run_commands = self.mock_run_commands.start()

        self.cliconf_obj = Cliconf(MagicMock())
        self.running_config = load_fixture('fos_config', 'config.cfg')

    def tearDown(self):
        super(TestFosConfigModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_load_config.stop()
        self.mock_get_connection.stop()
        self.mock_run_commands.stop()

    def load_fixtures(self, commands=None):
        self.get_config.return_value = load_fixture('fos_config', 'config.cfg')
        self.load_config.return_value = None

    def test_fos_config_no_change(self):
        lines = ['clock timezone 9 minutes 0']
        args = dict(lines=lines)
        set_module_args(args)

        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff('\n'.join(lines), self.running_config)
        )
        self.execute_module()

    def test_fos_config_lines(self):
        lines = ['clock timezone 8 minutes 0', 'ip routing']
        args = dict(lines=lines)
        set_module_args(args)

        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                '\n'.join(lines), self.running_config
            )
        )
        config = ['clock timezone 8 minutes 0']
        self.execute_module(changed=True, commands=config)

    def test_fos_config_parents(self):
        lines = ['lldp transmit', 'lldp notification']
        parents = ['interface 0/12']
        args = dict(lines=lines, parents=parents)
        candidate = parents + lines
        set_module_args(args)

        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                '\n'.join(candidate), self.running_config
            )
        )
        config = [
            'interface 0/12',
            'lldp transmit',
            'lldp notification',
        ]
        self.execute_module(changed=True, commands=config, sort=False)

    def test_fos_config_before(self):
        lines = ['clock timezone 8 minutes 0', 'ip routing']
        before = ['before command']
        args = dict(lines=lines, before=before)
        set_module_args(args)

        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                '\n'.join(lines), self.running_config
            )
        )
        config = ['before command', 'clock timezone 8 minutes 0']
        result = self.execute_module(changed=True, commands=config)
        self.assertEqual('before command', result['commands'][0])

    def test_fos_config_after(self):
        lines = ['clock timezone 8 minutes 0', 'ip routing']
        args = dict(lines=lines, after=['after command'])

        set_module_args(args)
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                '\n'.join(lines), self.running_config
            )
        )
        config = ['after command', 'clock timezone 8 minutes 0']
        result = self.execute_module(changed=True, commands=config)
        self.assertEqual('after command', result['commands'][-1])

    def test_fos_config_src_and_lines_fails(self):
        args = dict(src='foo', lines='foo')
        set_module_args(args)
        self.execute_module(failed=True)

    def test_fos_config_match_exact_requires_lines(self):
        args = dict(match='exact')
        set_module_args(args)
        self.execute_module(failed=True)

    def test_fos_config_match_strict_requires_lines(self):
        args = dict(match='strict')
        set_module_args(args)
        self.execute_module(failed=True)

    def test_fos_config_replace_block_requires_lines(self):
        args = dict(replace='block')
        set_module_args(args)
        self.execute_module(failed=True)

    def test_fos_config_backup_returns__backup__(self):
        args = dict(backup=True)
        set_module_args(args)
        result = self.execute_module()
        self.assertIn('__backup__', result)

    def test_fos_config_save(self):
        set_module_args(dict(save=True))
        self.execute_module(changed=True)
        self.assertEqual(self.run_commands.call_count, 1)
        self.assertEqual(self.get_config.call_count, 0)
        self.assertEqual(self.load_config.call_count, 0)
        args = self.run_commands.call_args[0][1]
        self.assertDictContainsSubset({'command': 'copy system:running-config nvram:startup-config'}, args[0])
