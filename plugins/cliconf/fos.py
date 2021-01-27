#
# (c) 2020 Red Hat Inc.
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
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
cliconf: fos
short_description: Use fos cliconf to run command on FUJITSU PSWITCH platform
description:
  - This os10 plugin provides low level abstraction apis for
    sending and receiving CLI commands from FUJITSU PSWITCH.
version_added: 2.10
"""

import re
import json

from ansible_collections.fujitsu.fos.plugins.module_utils.network.fos import load_running_config
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import NetworkConfig, dumps
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    @enable_mode
    def edit_config(self, candidate=None, commit=True, replace=None, comment=None):
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(operations, candidate, commit, replace, comment)

        results = []
        requests = []
        if commit:
            if not self._connection.get_prompt().endswith(b'(Config)#'):
                self.send_command('configure')
            for line in to_list(candidate):
                if not isinstance(line, Mapping):
                    line = {'command': line}

                cmd = line['command']
                if cmd != 'end' and cmd[0] != '!':
                    results.append(self.send_command(**line))
                    requests.append(cmd)

            self.send_command('end')
        else:
            raise ValueError('check mode is not supported')

        resp['request'] = requests
        resp['response'] = results
        return resp

    @enable_mode
    def edit_vlan(self, candidate=None, commit=True, replace=None, comment=None):
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(operations, candidate, commit, replace, comment)

        results = []
        requests = []
        if commit:
            if not self._connection.get_prompt().endswith(b'(Vlan)#'):
                self.send_command('vlan database')
            for line in to_list(candidate):
                if not isinstance(line, Mapping):
                    line = {'command': line}

                cmd = line['command']
                if cmd != 'end' and cmd[0] != '!':
                    results.append(self.send_command(**line))
                    requests.append(cmd)

            self.send_command('end')
        else:
            raise ValueError('check mode is not supported')

        resp['request'] = requests
        resp['response'] = results
        return resp

    def get(self, command=None, prompt=None, answer=None, sendonly=False, output=None, newline=True, check_all=False):
        if not command:
            raise ValueError('must provide value of command to execute')
        if output:
            raise ValueError("'output' value %s is not supported for get" % output)

        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result['rpc'] += ['get_diff', 'run_commands', 'get_defaults_flag']
        result['device_operations'] = self.get_device_operations()
        result.update(self.get_option_values())
        return json.dumps(result)

    @enable_mode
    def get_config(self, source='running', flags=None, format=None):
        if source not in ('running', 'startup'):
            raise ValueError("fetching configuration from %s is not supported" % source)

        if format:
            raise ValueError("'format' value %s is not supported for get_config" % format)

        if not flags:
            flags = []
        if source == 'running':
            cmd = 'show running-config '
        else:
            cmd = 'show multiconfig startup-config '

        cmd += ' '.join(to_list(flags))
        cmd = cmd.strip()

        return self.send_command(cmd)

    def get_defaults_flag(self):
        out = self.get('show running-config ?')
        out = to_text(out, errors='surrogate_then_replace')

        commands = set()
        for line in out.splitlines():
            if line.strip():
                commands.add(line.strip().split()[0])

        if 'all' in commands:
            return 'all'
        else:
            return 'full'

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'fos'
        if self._connection.get_prompt().endswith(b'>'):
            reply = self.get(command='enable')
        reply = self.get(command='show version')
        data = to_text(reply, errors='surrogate_or_strict').strip()
        match = re.search(r'^Current Runtime Version\.+ (.+)', data, re.M)
        if match:
            device_info['network_os_version'] = match.group(1)

        reply = self.get(command='show hardware')
        data = to_text(reply, errors='surrogate_or_strict').strip()
        match = re.search(r'^Machine Type[\.]+ \s*(.+)', data)
        if match:
            device_info['network_os_type'] = match.group(1)
        match = re.search(r'^Machine Model[\.]+ \s*(.+)', data)
        if match:
            device_info['network_os_model'] = match.group(1)

        reply = self.get(command='show hosts')
        data = to_text(reply, errors='surrogate_or_strict').strip()
        match = re.search(r'^Host name\.+ (.+)', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    def get_device_operations(self):
        return {
            'supports_commit': False,
            'supports_rollback': False,
            'supports_defaults': True,
            'supports_onbox_diff': False,
            'supports_commit_comment': False,
            'supports_diff_match': True,
            'supports_replace': False
        }

    def get_diff(self, candidate=None, running=None, diff_match='line', path=None, diff_replace='line'):
        diff = {}
        device_operations = self.get_device_operations()
        option_values = self.get_option_values()

        if candidate is None and device_operations['supports_generate_diff']:
            raise ValueError("candidate configuration is required to generate diff")

        if diff_match not in option_values['diff_match']:
            raise ValueError("'match' value %s in invalid, valid values are %s" % (diff_match, ', '.join(option_values['diff_match'])))

        if diff_replace not in option_values['diff_replace']:
            raise ValueError("'replace' value %s in invalid, valid values are %s" % (diff_replace, ', '.join(option_values['diff_replace'])))

        # prepare candidate configuration
        candidate_obj = NetworkConfig(indent=4, contents=candidate)

        if running and diff_match != "none" and diff_replace != "config":
            running_obj = load_running_config(running=running)
            configdiffobjs = candidate_obj.difference(
                running_obj, path=path, match=diff_match, replace=diff_replace
            )

        else:
            configdiffobjs = candidate_obj.items

        diff["config_diff"] = (
            dumps(configdiffobjs, "commands") if configdiffobjs else ""
        )

        return diff

    def get_option_values(self):
        return {
            'format': ['text'],
            'diff_match': ['line', 'strict', 'exact', 'none'],
            'diff_replace': ['line', 'block'],
            'output': []
        }

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {'command': cmd}

            output = cmd.pop('output', None)
            if output:
                raise ValueError("'output' value %s is not supported for run_commands" % output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, 'err', to_text(e))

            responses.append(out)

        return responses

    # This function is used to send key (or key string) and NOT wait response
    def send_data(self, data=None):
        if data is None:
            return
        self.send_command(data, sendonly=True)
