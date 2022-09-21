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
module: pure1_alerts
version_added: '1.1.0'
short_description: Collect array alerts from Pure1 based on severity
description:
  - Collect array alerts based on severity. Select whole fleet or by appliance
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  name:
    description:
      - Name of appliance to obtain alert drtails.
      - If not provided, the whole fleet with be used
    type: str
  severity:
    description: Severity of alerts to select
    type: str
    choices: [ info, warning, critical, hidden ]
    required: true
  state:
    description: Stae of the alert
    type: str
    default: open
    choices: [ open, closed ]
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect critical alerts for arrayt foo
  purestorage.pure1.pure1_alerts:
    name: foo
    severity: critical
"""

RETURN = r"""
alert_info:
  description: Returns information on appliance alerts
  returned: always
  type: complex
  sample: {
     "alert_info": {
        "0": {
            "appliance_name": "pure-fa1.acme.com",
            "category": "array",
            "closed": "2021-10-04 16:52:23",
            "code": 25,
            "component_name": "array.capacity",
            "component_type": "storage",
            "created": "2020-07-22 19:41:17",
            "notified": "2021-10-04 06:49:34",
            "summary": "storage array.capacity high utilization",
            "updated": "2021-10-04 14:36:14"
        },
        "1": {
            "appliance_name": "pure-fa2.acme.com",
            "category": "array",
            "code": 25,
            "component_name": "array.capacity",
            "component_type": "storage",
            "created": "2021-08-05 15:15:14",
            "notified": "2021-10-04 12:40:07",
            "summary": "storage array.capacity high utilization",
            "updated": "2021-10-04 15:50:15"
        },
    }
}
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)
import time


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str"),
            severity=dict(
                type="str",
                choices=["info", "warning", "critical", "hidden"],
                required=True,
            ),
            state=dict(default="open", type="str", choices=["open", "closed"]),
        )
    )

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)
    index = 0
    alert_info = {}
    if module.params["name"]:
        alerts = list(
            pure_1.get_alerts(
                filter="arrays.name='"
                + module.params["name"]
                + "' and severity='"
                + module.params["severity"]
                + "' and state='"
                + module.params["state"]
                + "'"
            ).items
        )
        if not alerts:
            module.fail_json(
                msg="No {0} alerts of severity {1} for array {2} found.".format(
                    module.params["state"],
                    module.params["severity"],
                    module.params["name"],
                )
            )
    else:
        alerts = list(
            pure_1.get_alerts(
                filter="severity='"
                + module.params["severity"]
                + "' and state='"
                + module.params["state"]
                + "'"
            ).items
        )
        if not alerts:
            module.fail_json(
                msg="Failed to get any {0} alerts of severity {1} for the fleet.".format(
                    module.params["state"], module.params["severity"]
                )
            )

    for alert in range(0, len(alerts)):
        alert_info[index] = {
            "component_type": getattr(alerts[alert], "component_type", None),
            "component_name": getattr(alerts[alert], "component_name", None),
            "code": alerts[alert].code,
            "category": getattr(alerts[alert], "category", None),
            "summary": alerts[alert].summary,
        }
        if getattr(alerts[alert], "created", 0) != 0:
            alert_info[index]["created"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(int(alerts[alert].created) / 1000)
            )
        if getattr(alerts[alert], "updated", 0) != 0:
            alert_info[index]["updated"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(int(alerts[alert].updated) / 1000)
            )
        if getattr(alerts[alert], "notified", 0) != 0:
            alert_info[index]["notified"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(int(alerts[alert].notified) / 1000)
            )
        if module.params["state"] == "closed":
            if getattr(alerts[alert], "closed", 0) != 0:
                alert_info[index]["closed"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(int(alerts[alert].closed) / 1000),
                )
        if not module.params["name"]:
            alert_info[index]["appliance_name"] = alerts[alert].arrays[0].name
        index += 1

    module.exit_json(changed=False, alert_info=alert_info)


if __name__ == "__main__":
    main()
