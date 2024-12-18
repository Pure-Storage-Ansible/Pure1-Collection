#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2024, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: pure1_drives
version_added: '1.5.0'
short_description: Collect array drives information from Pure1
description:
  - Collect array drives information from a Pure1
options:
  array:
    description:
      - Filter to provide only drives for a specifically named array or blade
    type: str
author:
  - Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect all drives information
  purestorage.pure1.pure1_drives:
    register: pure1_drives

- name: collect only drives information for array X
  purestorage.pure1.pure1_drives:
    array: X
    register: pure1_drives

- name: show drives information
  debug:
    msg: "{{ pure1_info['pure1_drives']['drives'] }}"
"""

RETURN = r"""
pure1_drives:
  description: Returns array drives information collected from Pure1
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)


def generate_drives_dict(module, pure_1):
    drives_info = {}
    if module.params["array"]:
        res = pure_1.get_drives(filter="arrays.name='" + module.params["array"] + "'")
        if res.status_code == 200 and res.total_item_count != 0:
            drives = list(res.items)
        else:
            module.warn(
                "No drives information available for array {0}".format(
                    module.params["array"]
                )
            )
            module.exit_json(changed=False)
    else:
        drives = list(pure_1.get_drives().items)
    for drive in range(0, len(drives)):
        array = drives[drive].arrays[0].name
        drives_info[array] = []
    for drive in range(0, len(drives)):
        array = drives[drive].arrays[0].name
        drive_name = drives[drive].name
        drive_details = {
            drive_name: {
                "capacity": getattr(drives[drive], "capacity", None),
                "protocol": getattr(drives[drive], "protocol", None),
                "status": getattr(drives[drive], "status", None),
                "type": getattr(drives[drive], "type", None),
            }
        }
        drives_info[array].append(drive_details)
    return drives_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(dict(array=dict(type="str")))
    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    drives = {}

    drives["drives"] = generate_drives_dict(module, pure_1)

    module.exit_json(changed=False, pure1_drives=drives)


if __name__ == "__main__":
    main()
