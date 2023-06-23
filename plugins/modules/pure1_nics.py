#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Simon Dodsley (simon@purestorage.com)
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
module: pure1_nics
version_added: '1.3.0'
short_description: Collect network interface information from Pure1
description:
  - Collect network interface information from a Pure1
options:
  array:
    description:
      - Filter to provide only network interfaces for a specifically named array or blade
    type: str
author:
  - Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect all network interface information
  purestorage.pure1.pure1_nics:
    register: pure1_nics

- name: collect only network interface information for array X
  purestorage.pure1.pure1_nics:
    array: X
    register: pure1_nics

- name: show network interface information
  debug:
    msg: "{{ pure1_info['pure1_nics']['nics'] }}"

"""

RETURN = r"""
pure1_nics:
  description: Returns the network interface information collected from Pure1
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)


def generate_nics_dict(module, pure_1):
    nics_info = {}
    if module.params["array"]:
        nics = list(
            pure_1.get_network_interfaces(
                filter="arrays.name='" + module.params["array"] + "'"
            ).items
        )
    else:
        nics = list(pure_1.get_network_interfaces().items)
    for nic in range(0, len(nics)):
        array = nics[nic].arrays[0].name
        nics_info[array] = []
    for nic in range(0, len(nics)):
        array = nics[nic].arrays[0].name
        nic_name = nics[nic].name
        nic_details = {
            nic_name: {
                "address": getattr(nics[nic], "address", None),
                "gateway": getattr(nics[nic], "gateway", None),
                "hwaddr": getattr(nics[nic], "hwaddr", None),
                "netmask": getattr(nics[nic], "netmask", None),
                "mtu": getattr(nics[nic], "mtu", None),
                "speed": round(getattr(nics[nic], "speed", 0) / 1000000000),
                "enabled": nics[nic].enabled,
                "services": [],
                "subinterfaces": [],
            }
        }
        if getattr(nics[nic], "services", None):
            nic_details[nic_name]["services"] = nics[nic].services
        if getattr(nics[nic], "subinterfaces", None):
            nic_details[nic_name]["subinterfaces"] = nics[nic].subinterfaces
        nics_info[array].append(nic_details)
    return nics_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(dict(array=dict(type="str")))
    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    nics = {}

    nics["nics"] = generate_nics_dict(module, pure_1)

    module.exit_json(changed=False, pure1_nics=nics)


if __name__ == "__main__":
    main()
