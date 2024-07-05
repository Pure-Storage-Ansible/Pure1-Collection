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
module: pure1_volumes
version_added: '1.3.0'
short_description: Collect volumes information from Pure1
description:
  - Collect volumes information from a Pure1 keyed on volume serial number.
options:
  array:
    description:
      - Filter to provide only volumes for a specifically named array
    type: str
author:
  - Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect all volumes information
  purestorage.pure1.pure1_volumes:
    register: pure1_volumes

- name: collect only volumes information for array X
  purestorage.pure1.pure1_volumes:
    array: X
    register: pure1_volumes

- name: show volumes information
  debug:
    msg: "{{ pure1_info['pure1_volumes']['serial_numbers'] }}"

"""

RETURN = r"""
pure1_volumes:
  description: Returns the volumes information collected from Pure1
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)
import time


def generate_volumes_dict(module, pure_1):
    volumes_info = {}
    if module.params["array"]:
        volumes = list(
            pure_1.get_volumes(
                filter="arrays.name='" + module.params["array"] + "'"
            ).items
        )
    else:
        volumes = list(pure_1.get_volumes().items)
    for volume in range(0, len(volumes)):
        serial = volumes[volume].serial
        created = time.strftime(
            "%Y-%m-%d %H:%M:%S UTC",
            time.gmtime(volumes[volume].created / 1000),
        )
        volumes_info[serial] = {
            "name": volumes[volume].name,
            "created": created,
            "eradicated": volumes[volume].eradicated,
            "destroyed": volumes[volume].destroyed,
            "provisioned": volumes[volume].provisioned,
            "source": [],
            "serial": getattr(volumes[volume], "serial", None),
            "pod": [],
            "array": {
                "name": volumes[volume].arrays[0].name,
                "fqdn": volumes[volume].arrays[0].fqdn,
            },
        }
        if getattr(volumes[volume], "source", None):
            volumes_info[serial]["source"] = volumes[volume].source.name
        if getattr(volumes[volume], "pod", None):
            volumes_info[serial]["pod"] = volumes[volume].pod.name
    return volumes_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(dict(array=dict(type="str")))
    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    volumes = {}

    volumes["serial_numbers"] = generate_volumes_dict(module, pure_1)

    module.exit_json(changed=False, pure1_volumes=volumes)


if __name__ == "__main__":
    main()
