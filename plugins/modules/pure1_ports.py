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
module: pure1_ports
version_added: '1.3.0'
short_description: Collect FlashArray port information from Pure1
description:
  - Collect FlashArray port information from a Pure1
options:
  array:
    description:
      - Filter to provide only ports for a specifically named array
    type: str
author:
  - Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect all ports information
  purestorage.pure1.pure1_ports:
    register: pure1_ports

- name: collect only ports information for array X
  purestorage.pure1.pure1_ports:
    array: X
    register: pure1_ports

- name: show ports information
  debug:
    msg: "{{ pure1_info['pure1_ports']['ports'] }}"
"""

RETURN = r"""
pure1_ports:
  description: Returns the ports information collected from Pure1
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)


def generate_ports_dict(module, pure_1):
    ports_info = {}
    if module.params["array"]:
        ports = list(
            pure_1.get_ports(
                filter="arrays.name='" + module.params["array"] + "'"
            ).items
        )
    else:
        ports = list(pure_1.get_ports().items)
    for port in range(0, len(ports)):
        array = ports[port].arrays[0].name
        ports_info[array] = []
    for port in range(0, len(ports)):
        array = ports[port].arrays[0].name
        port_name = ports[port].name
        port_details = {
            port_name: {
                "iqn": getattr(ports[port], "iqn", None),
                "nqn": getattr(ports[port], "nqn", None),
                "wwn": getattr(ports[port], "wwn", None),
                "portal": getattr(ports[port], "portal", None),
                "failover": getattr(ports[port], "failover", None),
            }
        }
        ports_info[array].append(port_details)
    return ports_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(dict(array=dict(type="str")))
    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    ports = {}

    ports["ports"] = generate_ports_dict(module, pure_1)

    module.exit_json(changed=False, pure1_ports=ports)


if __name__ == "__main__":
    main()
