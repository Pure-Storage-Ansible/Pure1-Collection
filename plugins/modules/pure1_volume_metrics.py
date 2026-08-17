#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2026, Simon Dodsley (simon@everpuredata.com)
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
module: pure1_volume_metrics
version_added: '1.6.0'
short_description: Collect volume metrics from Pure1
description:
  - Collect historical metric data (such as capacity or performance) for
    volumes from Pure1, keyed on volume serial number.
  - Pure1 exposes per-volume capacity and performance as time-series metrics
    rather than as fields on the volume object, so this module queries the
    Pure1 metrics history endpoint.
  - Use I(list_available) to discover which metric names are valid for volumes
    in your environment before requesting them with I(metrics).
options:
  array:
    description:
      - Filter to provide only volumes for a specifically named array.
    type: str
  volumes:
    description:
      - List of specific volume names to query.
      - If not specified, all volumes are queried.
    type: list
    elements: str
  metrics:
    description:
      - List of Pure1 volume metric names to collect.
      - Required unless I(list_available) is set.
      - Use I(list_available) to discover the valid metric names.
    type: list
    elements: str
  aggregation:
    description:
      - Aggregation to apply to the metric data.
    type: str
    choices: [ avg, max ]
    default: avg
  resolution:
    description:
      - The duration of time between individual data points, in milliseconds.
      - Defaults to one day.
    type: int
    default: 86400000
  window:
    description:
      - How far back, in seconds, to request metric data.
      - The most recent data point in the window is returned for each metric.
    type: int
    default: 86400
  list_available:
    description:
      - If set, return the list of metric names available for volumes instead
        of querying any metric data.
    type: bool
    default: false
author:
  - Everpure Ansible Team (@sdodsley) <pure-ansible-team@everpuredata.com>
extends_documentation_fragment:
  - everpure.pure1.everpure.p1
"""

EXAMPLES = r"""
- name: List the metric names available for volumes
  everpure.pure1.pure1_volume_metrics:
    list_available: true
  register: available

- name: Show available volume metric names
  debug:
    msg: "{{ available['pure1_volume_metrics']['available_metrics'] }}"

- name: Collect a capacity metric for all volumes
  everpure.pure1.pure1_volume_metrics:
    metrics:
      - volume_total_used
  register: usage

- name: Show per-volume metric data
  debug:
    msg: "{{ usage['pure1_volume_metrics']['serial_numbers'] }}"

- name: Collect multiple metrics for volumes on a single array
  everpure.pure1.pure1_volume_metrics:
    array: flasharray1
    metrics:
      - volume_total_used
      - volume_write_iops
"""

RETURN = r"""
pure1_volume_metrics:
  description: Returns the volume metric data collected from Pure1
  returned: always
  type: dict
  contains:
    available_metrics:
      description: List of metrics available for volumes (only when I(list_available) is set)
      type: list
      elements: dict
    serial_numbers:
      description: Per-volume metric data keyed on volume serial number
      type: dict
      contains:
        id:
          description: The globally unique Pure1 ID (NAID) of the volume
          type: str
        name:
          description: The volume name
          type: str
        metrics:
          description: Dictionary of requested metrics keyed on metric name
          type: dict
          contains:
            unit:
              description: The unit of the metric
              type: str
            timestamp:
              description: UTC millisecond epoch of the returned data point
              type: int
            value:
              description: The value of the most recent data point in the window
              type: float
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.everpure.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)
import time

# Pure1 metrics history allows up to 32 time series (metrics x resources) per call.
MAX_TIME_SERIES = 32


def list_volume_metrics(pure_1):
    metrics = list(pure_1.get_metrics(resource_types=["volumes"]).items)
    available = []
    for metric in metrics:
        available.append(
            {
                "name": metric.name,
                "unit": getattr(metric, "unit", None),
                "description": getattr(metric, "description", None),
                "resource_types": getattr(metric, "resource_types", None),
            }
        )
    return available


def resolve_volumes(module, pure_1):
    if module.params["array"]:
        volumes = list(
            pure_1.get_volumes(
                filter="arrays.name='" + module.params["array"] + "'"
            ).items
        )
    elif module.params["volumes"]:
        volumes = list(pure_1.get_volumes(names=module.params["volumes"]).items)
    else:
        volumes = list(pure_1.get_volumes().items)
    return volumes


def generate_metrics_dict(module, pure_1):
    metrics = module.params["metrics"]
    volumes = resolve_volumes(module, pure_1)

    # Seed the result with every in-scope volume so the report is complete even
    # when a volume has no data points for the requested window.
    volumes_info = {}
    vol_by_id = {}
    for volume in volumes:
        serial = volume.serial
        volumes_info[serial] = {
            "id": getattr(volume, "id", None),
            "name": volume.name,
            "metrics": {},
        }
        vol_by_id[volume.id] = serial

    end_time = int(time.time()) * 1000
    start_time = end_time - (module.params["window"] * 1000)

    # Chunk volumes so that metrics x volumes stays within the 32 series limit.
    vols_per_call = max(1, MAX_TIME_SERIES // len(metrics))
    volume_ids = list(vol_by_id.keys())

    for start in range(0, len(volume_ids), vols_per_call):
        batch = volume_ids[start : start + vols_per_call]
        try:
            response = pure_1.get_metrics_history(
                aggregation=module.params["aggregation"],
                resolution=module.params["resolution"],
                start_time=start_time,
                end_time=end_time,
                names=metrics,
                resource_ids=batch,
            )
        except Exception as err:
            module.warn("Failed to collect metrics for a batch: %s" % str(err))
            continue
        if getattr(response, "status_code", 200) != 200:
            module.warn(
                "Failed to collect metrics for a batch: %s"
                % getattr(response, "errors", response)
            )
            continue
        for series in list(response.items):
            if not getattr(series, "data", None) or not getattr(
                series, "resources", None
            ):
                continue
            serial = vol_by_id.get(series.resources[0].id)
            if serial is None:
                continue
            latest = series.data[-1]
            volumes_info[serial]["metrics"][series.name] = {
                "unit": getattr(series, "unit", None),
                "timestamp": latest[0],
                "value": latest[1],
            }
    return volumes_info


def main():
    argument_spec = pure1_argument_spec()
    argument_spec.update(
        dict(
            array=dict(type="str"),
            volumes=dict(type="list", elements="str"),
            metrics=dict(type="list", elements="str"),
            aggregation=dict(type="str", choices=["avg", "max"], default="avg"),
            resolution=dict(type="int", default=86400000),
            window=dict(type="int", default=86400),
            list_available=dict(type="bool", default=False),
        )
    )
    module = AnsibleModule(
        argument_spec,
        mutually_exclusive=[["array", "volumes"]],
        required_if=[["list_available", False, ["metrics"]]],
        supports_check_mode=True,
    )
    pure_1 = get_pure1(module)

    result = {}
    if module.params["list_available"]:
        result["available_metrics"] = list_volume_metrics(pure_1)
    else:
        result["serial_numbers"] = generate_metrics_dict(module, pure_1)

    module.exit_json(changed=False, pure1_volume_metrics=result)


if __name__ == "__main__":
    main()
