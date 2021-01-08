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
module: fos_config
version_added: "2.10"
short_description: Manage FUJITSU PSWITCH configuration sections
description:
  - fos configurations use a simple block indent file syntax
    for segmenting configuration into sections.  This module provides
    an implementation for working with PSWITCH configuration sections in
    a deterministic way.
options:
  lines:
    description:
      - The ordered set of commands that should be configured in the
        section.  The commands must be the exact same commands as found
        in the mode Global Config.  Be sure to note the configuration
        command syntax as some commands are automatically modified by the
        device config parser.
    type: list
    aliases: ['commands']
  parents:
    description:
      - The ordered set of parents that uniquely identify the section or hierarchy
        the commands should be checked against.  If the parents argument
        is omitted, the commands are checked against the set of top
        level or global commands.
    type: list
  src:
    description:
      - Specifies the source path to the file that contains the configuration
        or configuration template to load and all the configuration will be
        send to the device. The path to the source file can either be the
        full path on the Ansible control host or a relative path from the
        playbook.  This argument is mutually exclusive with I(lines), I(parents).
        When there are multiple settings, exit cannot be less in the src file.
    type: path
  before:
    description:
      - The ordered set of commands to push on to the command stack if
        a change needs to be made.  This allows the playbook designer
        the opportunity to perform configuration commands prior to pushing
        any changes without affecting how the set of commands are matched
        against the system.
    type: list
  after:
    description:
      - The ordered set of commands to append to the end of the command
        stack if a change needs to be made.  Just like with I(before) this
        allows the playbook designer to append a set of commands to be
        executed after the command set.
    type: list
  match:
    description:
      - Instructs the module on the way to perform the matching of
        the set of commands against the current device config.  If
        match is set to I(line), commands are matched line by line.  If
        match is set to I(strict), command lines are matched with respect
        to position.  If match is set to I(exact), command lines
        must be an equal match.  Finally, if match is set to I(none), the
        module will not attempt to compare the source configuration with
        the running configuration on the remote device.
    type: str
    choices: ['line', 'strict', 'exact', 'none']
    default: line
  replace:
    description:
      - Instructs the module on the way to perform the configuration
        on the device. If the replace argument is set to I(line) then
        the modified lines are pushed to the device in configuration
        mode.  If the replace argument is set to I(block) then the entire
        command block is pushed to the device in configuration mode if any
        line is not correct.
    type: str
    default: line
    choices: ['line', 'block']
  running_config:
    description:
      - The module, by default, will connect to the remote device and
        retrieve the current running-config to use as a base for comparing
        against the contents of source. There are times when it is not
        desirable to have the task get the current running-config for
        every task in a playbook.  The I(running_config) argument allows the
        implementer to pass in the configuration to use as the base
        config for comparison.
    type: str
    aliases: ['config']
  save:
    description:
      - The C(save) argument instructs the module to save the running-
        config to the startup-config at the conclusion of the module
        running.  If check mode is specified, this argument is ignored.
    type: bool
    default: 'no'
  backup:
    description:
      - This argument will cause the module to create a full backup of
        the current C(running-config) from the remote device before any
        changes are made. If the C(backup_options) value is not given,
        the backup file is written to the C(backup) folder in the playbook
        root directory or role root directory, if playbook is part of an
        ansible role. If the directory does not exist, it is created.
    type: bool
    default: 'no'
  backup_options:
    description:
      - This is a dict object containing configurable options related to backup file path.
        The value of this option is read only when C(backup) is set to I(yes), if C(backup) is set
        to I(no) this option will be silently ignored.
    suboptions:
      filename:
        description:
          - The filename to be used to store the backup configuration. If the the filename
            is not given it will be generated based on current time and date in format defined
            by config.<current-date>@<current-time>
        type: str
      dir_path:
        description:
          - This option provides the path ending with directory name in which the backup
            configuration file will be stored. The backup path needs to be created in advance.
        type: path
    type: dict
"""
EXAMPLES = """
- name: configure interface settings
  fos_config:
    lines:
      - lldp transmit
      - lldp receive
    parents: interface 0/16

- name: save running config to startup config
  fos_config:
    save: True

- name: backup configuration file
  fos_config:
    backup: yes
    backup_options:
      filename: backup.cfg
      dir_path: /home/user
"""


import json
import os
import time

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible_collections.fujitsu.fos.plugins.module_utils.network.fos import run_commands, get_config, load_config
from ansible_collections.fujitsu.fos.plugins.module_utils.network.fos import get_connection
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import NetworkConfig, dumps


def get_candidate_config(module):
    candidate = ''
    if module.params['src']:
        candidate_obj = NetworkConfig(indent=0)
        candidate_obj.loadfp(module.params['src'])
        candidate = dumps(candidate_obj, 'raw')

    elif module.params['lines']:
        candidate_obj = NetworkConfig(indent=4)
        parents = module.params['parents'] or list()
        candidate_obj.add(module.params['lines'], parents=parents)
        candidate = dumps(candidate_obj, 'raw')

    return candidate


def get_running_config(module, current_config=None, flags=None):
    running = module.params['running_config']
    if not running:
        if current_config:
            running = current_config
        else:
            running = get_config(module)

    return running


def main():
    """ main entry point for module execution
    """
    backup_spec = dict(
        filename=dict(),
        dir_path=dict(type='path')
    )
    argument_spec = dict(
        src=dict(type='path'),

        lines=dict(aliases=['commands'], type='list'),
        parents=dict(type='list'),

        before=dict(type='list'),
        after=dict(type='list'),

        match=dict(default='line', choices=['line', 'strict', 'exact', 'none']),
        replace=dict(default='line', choices=['line', 'block']),

        running_config=dict(aliases=['config']),

        backup=dict(type='bool', default=False),
        backup_options=dict(type='dict', options=backup_spec),
        save=dict(type='bool', default=False)
    )

    mutually_exclusive = [
        ('lines', 'src'),
        ('parents', 'src'),
    ]

    required_if = [
        ('match', 'strict', ['lines']),
        ('match', 'exact', ['lines']),
        ('replace', 'block', ['lines']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        required_if=required_if,
        supports_check_mode=True,
    )

    result = {'changed': False}

    warnings = list()
    result['warnings'] = warnings

    config = None
    contents = None
    connection = get_connection(module)

    if module.params['backup']:
        filename = ''
        backup_path = ''
        contents = get_config(module)
        result['__backup__'] = contents
        if module.params['backup_options']:
            filename = module.params['backup_options']['filename']
            backup_path = module.params['backup_options']['dir_path']
        if not filename:
            tstamp = time.strftime('%Y-%m-%d@%H:%M:%S', time.localtime(time.time()))
            filename = 'config.%s' % (tstamp)
        if not backup_path:
            warnings.append('The backup path needs to be specified.')
        else:
            if not os.path.exists(backup_path):
                warnings.append('The backup path needs to be created in advance.')
            else:
                with open(backup_path + '/' + filename, 'w') as f:
                    f.write(contents)

    if module.params['lines']:
        match = module.params['match']
        replace = module.params['replace']
        path = module.params['parents']

        candidate = get_candidate_config(module)
        running = get_running_config(module, contents)
        try:
            response = connection.get_diff(candidate=candidate, running=running, diff_match=match, path=path, diff_replace=replace)
        except ConnectionError as exc:
            module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))

        config_diff = response['config_diff']

        if config_diff:
            commands = config_diff.split('\n')

            if module.params['before']:
                commands[:0] = module.params['before']

            if module.params['after']:
                commands.extend(module.params['after'])

            result['commands'] = commands
            result['updates'] = commands
            if not module.check_mode:
                if commands:
                    connection.edit_config(candidate=commands)

            result['changed'] = True

    if module.params['src']:
        commands = get_candidate_config(module).split('\n')

        if module.params['before']:
            commands[:0] = module.params['before']

        if module.params['after']:
            commands.extend(module.params['after'])

        result['commands'] = commands
        result['updates'] = commands
        if not module.check_mode:
            if commands:
                connection.edit_config(candidate=commands)

    running_config = module.params['running_config']
    startup_config = None

    if module.params['save']:
        result['changed'] = True
        if not module.check_mode:
            cmd = {r'command': 'copy system:running-config nvram:startup-config',
                   r'prompt': r'Are you sure you want to save', 'answer': 'y'}
            run_commands(module, [cmd])
            result['saved'] = True
        else:
            module.warn('Skipping command `copy system:running-config nvram:startup-config`'
                        'due to check_mode.  Configuration not copied to '
                        'non-volatile storage')

    if module._diff:
        if not running_config:
            output = run_commands(module, 'show running-config')
            contents = output[0]
        else:
            contents = running_config

        running_config = NetworkConfig(indent=4, contents=contents)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
