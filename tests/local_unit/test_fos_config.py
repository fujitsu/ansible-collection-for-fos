from __future__ import absolute_import, division, print_function
__metaclass__ = type

import subprocess
import unittest
import re


Cli = 'ansible-playbook -i '
Inventory = '/home/cicd/inventory/inventory '
PlaybookPath = 'tests/local_unit/playbooks/fos_config/'


def find_updates(output):
    begain = output.find('"updates"')
    end = output.find(']', begain)
    updates = output[begain: end + 1]
    updates = updates.strip().split('\n')
    return updates


def get_running_config():
    command = Cli + Inventory + PlaybookPath + 'get_config.yaml -vvv'
    output = subprocess.getoutput(command)
    begain = output.find('"stdout_lines"')
    end = output.find(']', begain)
    config = output[begain: end + 1]
    return config


def get_part_config(config, begain, end, offset=0):
    begains = config.find(begain)
    ends = config.find(end, begains)
    return config[begains: ends + offset]


class Test(unittest.TestCase):

    def test_initial_config(self):
        command = Cli + Inventory + PlaybookPath + 'initial.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        config = get_running_config()
        self.assertNotEqual(config.find('"clock timezone 9 minutes 0"'), -1)

        config = get_part_config(config, begain='"interface 0/13"', end='"exit"', offset=len('"exit"'))
        self.assertNotEqual(config.find('"lldp transmit"'), -1)
        self.assertEqual(config.find('"lldp receive"'), -1)
        self.assertNotEqual(config.find('"lldp notification"'), -1)

    def test_fos_config_before(self):
        command = Cli + Inventory + PlaybookPath + 'initial.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        command = Cli + Inventory + PlaybookPath + 'before.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            updates = [
                '"updates": [',
                '        "clock timezone 8 minutes 0",',
                '        "interface 0/13",',
                '        "no lldp receive"',
                '    ]'
            ]
            self.assertEqual(find_updates(output), updates)

        config = get_running_config()
        self.assertNotEqual(config.find('"clock timezone 8 minutes 0"'), -1)

    def test_fos_config_no_change(self):
        command = Cli + Inventory + PlaybookPath + 'initial.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        command = Cli + Inventory + PlaybookPath + 'no_change.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            self.assertNotEqual(output.find('changed=0'), -1)

    def test_fos_config_backup(self):
        retcode, output = subprocess.getstatusoutput('rm -fr ~/pswitch')
        if retcode:
            self.fail(output)

        retcode, output = subprocess.getstatusoutput('mkdir -p ~/pswitch')
        if retcode:
            self.fail(output)

        command = Cli + Inventory + PlaybookPath + 'backup.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        retcode, output = subprocess.getstatusoutput('ls ~/pswitch')
        if retcode:
            self.fail(output)
        else:
            self.assertEqual(output, 'backup.cfg')

        retcode, output = subprocess.getstatusoutput('cat ~/pswitch/backup.cfg')
        if retcode:
            self.fail(output)
        else:
            self.assertEqual(output.find('!Current Configuration:'), 0)

        retcode, output = subprocess.getstatusoutput('rm -fr ~/pswitch')
        if retcode:
            self.fail(output)

    def test_fos_config_src(self):
        command = Cli + Inventory + PlaybookPath + 'initial.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        command = Cli + Inventory + PlaybookPath + 'src.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        config = get_part_config(config=get_running_config(), begain='"interface 0/13"', end='"exit"', offset=len('"exit"'))
        self.assertNotEqual(config.find('"lldp receive"'), -1)

    def test_fos_config_match_exact(self):
        command = Cli + Inventory + PlaybookPath + 'initial.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        command = Cli + Inventory + PlaybookPath + 'match_exact.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            updates = [
                '"updates": [',
                '        "interface 0/13",',
                '        "lldp transmit",',
                '        "lldp receive",',
                '        "lldp notification"',
                '    ]'
            ]
            self.assertEqual(find_updates(output), updates)

        config = get_part_config(config=get_running_config(), begain='"interface 0/13"', end='"exit"', offset=len('"exit"'))
        self.assertNotEqual(config.find('"lldp transmit"'), -1)
        self.assertNotEqual(config.find('"lldp receive"'), -1)
        self.assertNotEqual(config.find('"lldp notification"'), -1)

    def test_fos_config_replace_blocak(self):
        command = Cli + Inventory + PlaybookPath + 'initial.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        command = Cli + Inventory + PlaybookPath + 'replace_block.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            updates = [
                '"updates": [',
                '        "interface 0/13",',
                '        "lldp transmit",',
                '        "lldp receive",',
                '        "lldp notification"',
                '    ]'
            ]
            self.assertEqual(find_updates(output), updates)

        config = get_part_config(config=get_running_config(), begain='"interface 0/13"', end='"exit"', offset=len('"exit"'))
        self.assertNotEqual(config.find('"lldp transmit"'), -1)
        self.assertNotEqual(config.find('"lldp receive"'), -1)
        self.assertNotEqual(config.find('"lldp notification"'), -1)


if __name__ == '__main__':
    unittest.main()
