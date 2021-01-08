from __future__ import absolute_import, division, print_function
__metaclass__ = type

import subprocess
import unittest
import re


Cli = 'ansible-playbook -i '
Inventory = '/home/cicd/inventory/inventory '
PlaybookPath = 'tests/local_unit/playbooks/fos_vlan/'


def get_vlan():
    command = Cli + Inventory + PlaybookPath + 'get_vlan.yaml -vvv'
    output = subprocess.getoutput(command)
    begain = output.find('"stdout_lines"')
    end = output.find(']', begain)
    vlan = output[begain: end + 1]

    if vlan.find('"VLAN does not exist."') != -1:
        return False
    else:
        return True


class Test(unittest.TestCase):

    def test_create_vlan(self):
        command = Cli + Inventory + PlaybookPath + 'delete_vlan.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        self.assertEqual(get_vlan(), False)

        command = Cli + Inventory + PlaybookPath + 'create_vlan.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        self.assertEqual(get_vlan(), True)

        command = Cli + Inventory + PlaybookPath + 'delete_vlan.yaml -vvv'
        retcode, output = subprocess.getstatusoutput(command)
        if retcode:
            self.fail(output)

        self.assertEqual(get_vlan(), False)


if __name__ == '__main__':
    unittest.main()
