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
module: pure1_info
version_added: '1.0.0'
short_description: Collect information from Pure1
description:
  - Collect information from a Pure1.
  - By default, the module will collect basic
    information including counts for appliances, volumes, filesystems, snapshots
    and buckets. Fleet capacity and data reduction rates are also provided.
  - Additional information can be collected based on the configured set of arguements.
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  gather_subset:
    description:
      - When supplied, this argument will define the information to be collected.
        Possible values for this include all, minimum, appliances, subscriptions
    type: list
    elements: str
    required: false
    default: minimum
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect default set of information
  pure1_info:
    register: pure1_info

- name: show default information
  debug:
    msg: "{{ pure1_info['pure1_info']['default'] }}"

- name: collect all information
  pure1_info:
    gather_subset:
      - all
- name: show all information
  debug:
    msg: "{{ pure1_info['pure1_info'] }}"
"""

RETURN = r"""
pure1_info:
  description: Returns the information collected from Pure1
  returned: always
  type: complex
  sample: {
        "appliances": {
            "FlashArray": {
                "CBS-AZURE": {
                    "fqdn": "",
                    "model": "CBS-V10MUR1",
                    "os_version": "6.1.4"
                },
                "pure-fa1": {
                    "fqdn": "pure-fa1.acme.com",
                    "model": "FA-405",
                    "os_version": "5.3.12"
                },
                "pure-fa2": {
                    "fqdn": "pue-fa2.acme.com",
                    "model": "FA-C60",
                    "os_version": "6.1.6"
                }
            },
            "FlashBlade": {
                "pure-fb1": {
                    "fqdn": "pure-fb1.com",
                    "model": "FlashBlade",
                    "os_version": "3.2.0"
                }
            }
        },
        "default": {
            "FlashArrays": 3,
            "FlashBlades": 1,
            "ObjectEngines": 0,
            "buckets": 45,
            "directories": 7,
            "filesystem_snapshots": 272,
            "filesystems": 295,
            "object_store_accounts": 25,
            "pods": 30,
            "volume_snapshots": 20501,
            "volumes": 1748
        }
    }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)
import time


def generate_default_dict(pure_1):
    default_info = {}
    fb_count = fa_count = os_count = 0
    appliances = list(pure_1.get_arrays().items)
    for appliance in range(0, len(appliances)):
        if appliances[appliance].os in ["Purity//FA", "Purity"]:
            fa_count += 1
        elif appliances[appliance].os == "Purity//FB":
            fb_count += 1
        elif appliances[appliance].os == "Elasticity":
            os_count += 1
    default_info["FlashArrays"] = fa_count
    default_info["FlashBlades"] = fb_count
    default_info["ObjectEngines"] = os_count
    default_info["volumes"] = pure_1.get_volumes().total_item_count
    default_info["volume_snapshots"] = pure_1.get_volume_snapshots().total_item_count
    default_info["filesystems"] = pure_1.get_file_systems().total_item_count
    default_info[
        "filesystem_snapshots"
    ] = pure_1.get_file_system_snapshots().total_item_count
    default_info["buckets"] = pure_1.get_buckets().total_item_count
    default_info["directories"] = pure_1.get_directories().total_item_count
    default_info["pods"] = pure_1.get_pods().total_item_count
    default_info[
        "object_store_accounts"
    ] = pure_1.get_object_store_accounts().total_item_count
    return default_info


def generate_subscriptions_dict(pure_1):
    subscriptions_info = {}
    subscriptions = list(pure_1.get_subscriptions().items)
    if subscriptions:
        for subscription in range(0, len(subscriptions)):
            name = subscriptions[subscription].name
            start_time = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(subscriptions[subscription].start_date / 1000),
            )
            end_time = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(subscriptions[subscription].expiration_date / 1000),
            )
            subscriptions_info[name] = {
                "start_date": start_time,
                "expiration_date": end_time,
                "service": subscriptions[subscription].service,
                "status": subscriptions[subscription].status,
            }
    return subscriptions_info


def generate_appliances_dict(module, pure_1):
    names_info = {"FlashArray": {}, "FlashBlade": {}, "ObjectStore": {}}
    appliances = list(pure_1.get_arrays().items)
    for appliance in range(0, len(appliances)):
        name = appliances[appliance].name
        try:
            fqdn = appliances[appliance].fqdn
        except AttributeError:
            fqdn = ""
        if appliances[appliance].os in ["Purity//FA", "Purity"]:
            names_info["FlashArray"][name] = {
                "os_version": appliances[appliance].version,
                "model": appliances[appliance].model,
                "fqdn": fqdn,
            }
        elif appliances[appliance].os == "Elasticity":
            names_info["ObjectEngine"][name] = {
                "os_version": appliances[appliance].version,
                "model": appliances[appliance].model,
                "fqdn": fqdn,
            }
        elif appliances[appliance].os == "Purity//FB":
            names_info["FlashBlade"][name] = {
                "os_version": appliances[appliance].version,
                "model": appliances[appliance].model,
                "fqdn": fqdn,
            }
        else:
            module.warning(
                "Unknown operating system detected: {0}.".format(
                    appliances[appliance].os
                )
            )
    return names_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(
        dict(gather_subset=dict(default="minimum", type="list", elements="str"))
    )

    module = AnsibleModule(argument_spec, supports_check_mode=False)
    pure_1 = get_pure1(module)

    subset = [test.lower() for test in module.params["gather_subset"]]
    valid_subsets = (
        "all",
        "minimum",
        "appliances",
        "subscriptions",
    )
    subset_test = (test in valid_subsets for test in subset)
    if not all(subset_test):
        module.fail_json(
            msg="value must gather_subset must be one or more of: %s, got: %s"
            % (",".join(valid_subsets), ",".join(subset))
        )

    info = {}

    if "minimum" in subset or "all" in subset:
        info["default"] = generate_default_dict(pure_1)
    if "appliances" in subset or "all" in subset:
        info["appliances"] = generate_appliances_dict(module, pure_1)
    if "subscriptions" in subset or "all" in subset:
        info["subscriptions"] = generate_subscriptions_dict(pure_1)

    module.exit_json(changed=False, pure1_info=info)


if __name__ == "__main__":
    main()
