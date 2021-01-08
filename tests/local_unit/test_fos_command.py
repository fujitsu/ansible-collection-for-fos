from __future__ import absolute_import, division, print_function
__metaclass__ = type

import subprocess
import unittest


Cli = 'ansible-playbook -i '
Inventory = '/home/cicd/inventory/inventory '
PlaybookPath = 'tests/local_unit/playbooks/fos_command/'


class Test(unittest.TestCase):
    def test_fos_command_simple(self):
        command = Cli + Inventory + PlaybookPath + 'show_version.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            self.assertNotEqual(output.find('Current Runtime Version'), -1)

    def test_fos_command_wait_for(self):
        command = Cli + Inventory + PlaybookPath + 'wait_for.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            self.assertNotEqual(output.find('Current Runtime Version'), -1)

    def test_fos_command_wait_for_fails(self):
        command = Cli + Inventory + PlaybookPath + 'wait_for_fails.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if not retcode:
            self.fail(output)

    def test_fos_command_match_any(self):
        command = Cli + Inventory + PlaybookPath + 'match_any.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)
        else:
            self.assertNotEqual(output.find('Current Runtime Version'), -1)

    def test_fos_command_match_all_fails(self):
        command = Cli + Inventory + PlaybookPath + 'match_all_fails.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if not retcode:
            self.fail(output)


if __name__ == '__main__':
    unittest.main()
