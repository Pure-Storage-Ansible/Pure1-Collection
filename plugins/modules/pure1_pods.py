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
module: pure1_pods
version_added: '1.3.0'
short_description: Collect FlashArray pod information from Pure1
description:
  - Collect FlashArray pod information from a Pure1
options:
  array:
    description:
      - Filter to provide only pods for a specifically named array
    type: str
author:
  - Pure Storage Ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect all pod information
  purestorage.pure1.pure1_pods:
    register: pure1_pods

- name: collect only pod information for array X
  purestorage.pure1.pure1_pods:
    array: X
    register: pure1_pods

- name: show pods information
  debug:
    msg: "{{ pure1_info['pure1_pods']['pods'] }}"
"""

RETURN = r"""
pure1_pods:
  description: Returns the pod information collected from Pure1
  returned: always
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)


def generate_pods_dict(module, pure_1):
    pods_info = {}
    if module.params["array"]:
        pods = list(
            pure_1.get_pods(filter="arrays.name='" + module.params["array"] + "'").items
        )
    else:
        pods = list(pure_1.get_pods().items)
    for pod in range(0, len(pods)):
        array = pods[pod].arrays[0].name
        pods_info[array] = []
    for pod in range(0, len(pods)):
        array = pods[pod].arrays[0].name
        pod_name = pods[pod].name
        pod_details = {
            pod_name: {
                "mediator": getattr(pods[pod], "mediator", None),
                "source": [],
            }
        }
        if getattr(pods[pod], "source", None):
            pod_details[pod_name]["source"] = pods[pod].source.name
        pods_info[array].append(pod_details)
    return pods_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(dict(array=dict(type="str")))
    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    pods = {}

    pods["pods"] = generate_pods_dict(module, pure_1)

    module.exit_json(changed=False, pure1_pods=pods)


if __name__ == "__main__":
    main()
