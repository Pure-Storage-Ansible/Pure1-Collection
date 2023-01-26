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
module: pure1_network_interfaces
version_added: '1.1.0'
short_description: Collect array netowrk interface details from Pure1
description:
  - Collect array network interface details from a Pure1.
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
      - Name of appliance to obtain network interface drtails.
    type: str
    required: true
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect network interface details for array foo
  purestorage.pure1.pure1_network_interfaces:
    name: foo
"""

RETURN = r"""
network_info:
  description: Returns information on appliance network port configurations
  returned: always
  type: complex
  sample: {
        "sn1-x70-f06-27": {
            "ct0.eth0": {
                "address": "1.2.3.25",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "24:a9:37:01:e5:36",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "management"
                ],
                "speed": 1,
                "subinterfaces": []
            },
            "ct0.eth1": {
                "address": "",
                "enabled": false,
                "gateway": "",
                "mac_address": "24:a9:37:01:e5:37",
                "mtu": 1500,
                "netmask": "",
                "services": [
                    "management"
                ],
                "speed": 1,
                "subinterfaces": []
            },
            "ct0.eth2": {
                "address": "1.2.3.100",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "24:a9:37:01:e5:38",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "replication",
                    "iscsi"
                ],
                "speed": 10,
                "subinterfaces": []
            },
            "ct0.eth3": {
                "address": "1.2.3.101",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "24:a9:37:01:e5:39",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "replication",
                    "iscsi"
                ],
                "speed": 10,
                "subinterfaces": []
            },
            "ct0.eth8": {
                "address": "",
                "enabled": false,
                "gateway": "",
                "mac_address": "3c:fd:fe:a8:ea:c9",
                "mtu": 1500,
                "netmask": "",
                "services": [
                    "iscsi"
                ],
                "speed": 40,
                "subinterfaces": []
            },
            "ct0.eth9": {
                "address": "",
                "enabled": false,
                "gateway": "",
                "mac_address": "3c:fd:fe:a8:ea:c8",
                "mtu": 1500,
                "netmask": "",
                "services": [
                    "iscsi"
                ],
                "speed": 40,
                "subinterfaces": []
            },
            "ct1.eth0": {
                "address": "1.2.3.26",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "24:a9:37:01:e5:24",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "management"
                ],
                "speed": 1,
                "subinterfaces": []
            },
            "ct1.eth1": {
                "address": "",
                "enabled": false,
                "gateway": "",
                "mac_address": "24:a9:37:01:e5:25",
                "mtu": 1500,
                "netmask": "",
                "services": [
                    "management"
                ],
                "speed": 1,
                "subinterfaces": []
            },
            "ct1.eth2": {
                "address": "1.2.3.102",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "24:a9:37:01:e5:26",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "replication",
                    "iscsi"
                ],
                "speed": 10,
                "subinterfaces": []
            },
            "ct1.eth3": {
                "address": "1.2.3.103",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "24:a9:37:01:e5:27",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "replication",
                    "iscsi"
                ],
                "speed": 10,
                "subinterfaces": []
            },
            "ct1.eth8": {
                "address": "",
                "enabled": false,
                "gateway": "",
                "mac_address": "3c:fd:fe:aa:c7:31",
                "mtu": 1500,
                "netmask": "",
                "services": [
                    "iscsi"
                ],
                "speed": 40,
                "subinterfaces": []
            },
            "ct1.eth9": {
                "address": "",
                "enabled": false,
                "gateway": "",
                "mac_address": "3c:fd:fe:aa:c7:30",
                "mtu": 1500,
                "netmask": "",
                "services": [
                    "iscsi"
                ],
                "speed": 40,
                "subinterfaces": []
            },
            "filevif": {
                "address": "1.2.3.200",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "c2:37:f1:a7:87:91",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "file"
                ],
                "speed": 10,
                "subinterfaces": [
                    "ct1.eth2",
                    "ct0.eth2"
                ]
            },
            "vir0": {
                "address": "1.2.3.24",
                "enabled": true,
                "gateway": "1.2.3.1",
                "mac_address": "06:2b:46:2a:17:24",
                "mtu": 1500,
                "netmask": "255.255.255.0",
                "services": [
                    "management"
                ],
                "speed": 1,
                "subinterfaces": []
            }
        }
    }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(dict(name=dict(type="str", required=True)))

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    network_info = {}

    interfaces = list(
        pure_1.get_network_interfaces(
            filter="arrays.name='" + module.params["name"] + "'"
        ).items
    )
    if not interfaces:
        module.fail_json(
            msg="Failed to get netowrk interfaces information. Check provided array name."
        )
    network_info[module.params["name"]] = {}

    for iface in range(0, len(interfaces)):
        port_name = interfaces[iface].name
        network_info[module.params["name"]][port_name] = {
            "services": interfaces[iface].services,
            "enabled": interfaces[iface].enabled,
            "gateway": getattr(interfaces[iface], "gateway", ""),
            "mtu": getattr(interfaces[iface], "mtu", ""),
            "netmask": getattr(interfaces[iface], "netmask", ""),
            "address": getattr(interfaces[iface], "address", ""),
            "subinterfaces": interfaces[iface].subinterfaces,
            "mac_address": getattr(interfaces[iface], "hwaddr", ""),
            "speed": round(getattr(interfaces[iface], "speed", 0) / 1000000000),
        }

    module.exit_json(changed=False, network_info=network_info)


if __name__ == "__main__":
    main()
