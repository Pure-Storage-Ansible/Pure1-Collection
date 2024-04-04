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
    and buckets. Fileset capacity and data reduction rates are also provided.
  - Additional information can be collected based on the configured set of arguements.
author:
  - Pure Storage ansible Team (@sdodsley) <pure-ansible-team@purestorage.com>
options:
  gather_subset:
    description:
      - When supplied, this argument will define the information to be collected.
        Possible values for this include all, minimum, appliances, subscriptions,
        contracts, environmental and invoices.
    type: list
    elements: str
    required: false
    default: minimum
extends_documentation_fragment:
  - purestorage.pure1.purestorage.p1
"""

EXAMPLES = r"""
- name: collect default set of information
  purestorage.pure1.pure1_info:
    register: pure1_info

- name: show default information
  debug:
    msg: "{{ pure1_info['pure1_info']['default'] }}"

- name: collect all information
  purestorage.pure1.pure1_info:
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
  type: dict
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.purestorage.pure1.plugins.module_utils.pure1 import (
    get_pure1,
    pure1_argument_spec,
)
import datetime
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
    default_info["filesystem_snapshots"] = (
        pure_1.get_file_system_snapshots().total_item_count
    )
    default_info["buckets"] = pure_1.get_buckets().total_item_count
    default_info["directories"] = pure_1.get_directories().total_item_count
    default_info["pods"] = pure_1.get_pods().total_item_count
    default_info["object_store_accounts"] = (
        pure_1.get_object_store_accounts().total_item_count
    )
    return default_info


def generate_subscription_assets_dict(pure_1):
    assets_info = {}
    assets = list(pure_1.get_subscription_assets().items)
    if assets:
        for asset in range(0, len(assets)):
            name = assets[asset].name
            activation = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(assets[asset].activation_date / 1000),
            )
            assets_info[name] = {
                "install_location": assets[asset].install_location,
                "activation_date": activation,
                "version": assets[asset].version,
                "model": assets[asset].model,
                "chassis_sn": assets[asset].chassis_serial_number,
                "effective_use": assets[asset].effective_use,
                "utilization": assets[asset].utilization,
                "total_usable": assets[asset].total_usable,
                "total_reduction": assets[asset].total_reduction,
                "subscription_name": assets[asset].subscription.name,
                "subscription_id": assets[asset].subscription.id,
                "license_name": assets[asset].license.name,
                "license_id": assets[asset].license.id,
            }
    return assets_info


def generate_subscription_licenses_dict(pure_1):
    licenses_info = {}
    licenses = list(pure_1.get_subscription_licenses().items)
    if licenses:
        for license in range(0, len(licenses)):
            name = licenses[license].name
            start_date = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(licenses[license].start_date / 1000),
            )
            expiration_date = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(licenses[license].expiration_date / 1000),
            )
            last_updated = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC",
                time.gmtime(licenses[license].last_updated_date / 1000),
            )
            licenses_info[name] = {
                "start_date": start_date,
                "expiration_date": expiration_date,
                "last_updated": last_updated,
                "marketplace_partner": licenses[license].marketplace_partner.name,
                "service_tier": licenses[license].service_tier,
                "location": licenses[license].location,
                "pre_ratio": licenses[license].pre_ratio,
                "energy_usage": licenses[license].energy_usage,
                "subscription": licenses[license].subscription.name,
                "average_on_demand": {
                    "data": licenses[license].average_on_demand.data,
                    "unit": licenses[license].average_on_demand.unit,
                    "metric": licenses[license].average_on_demand.metric.name,
                },
                "reservation": {
                    "data": licenses[license].reservation.data,
                    "unit": licenses[license].reservation.unit,
                    "metric": licenses[license].reservation.metric.name,
                },
                "usage": {
                    "data": licenses[license].usage.data,
                    "unit": licenses[license].usage.unit,
                    "metric": licenses[license].usage.metric.name,
                },
                "quarter_on_demand": {
                    "data": licenses[license].quarter_on_demand.data,
                    "unit": licenses[license].quarter_on_demand.unit,
                    "metric": licenses[license].quarter_on_demand.metric.name,
                },
                "resources": {},
            }
            for resource in range(0, len(licenses[license].resources)):
                res_name = licenses_info[license].resources[resource].name
                res_start_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S UTC",
                    time.gmtime(
                        licenses[license].resources[resource].activation_time / 1000
                    ),
                )
                licenses_info[license].resources[res_name] = {
                    "resource_type": licenses_info[license]
                    .resources[resource]
                    .resource_type,
                    "fqdn": licenses_info[license].resources[resource].fqdn,
                    "activation_time": res_start_time,
                    "usage": {
                        "data": licenses[license].resources[resource].usage.data,
                        "unit": licenses[license].resources[resource].usage.unit,
                        "metric": licenses[license]
                        .resources[resource]
                        .usage.metric.name,
                    },
                }
    return licenses_info


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
                "org_name": getattr(subscriptions[subscription], "org_name", None),
                "partner_name": getattr(
                    subscriptions[subscription], "partner_name", None
                ),
                "subscription_term": getattr(
                    subscriptions[subscription], "subscription_term", None
                ),
            }
    return subscriptions_info


def generate_esg_dict(module, pure_1):
    esg_info = {}
    current_date = int(time.time() * 1000)
    appliances = list(pure_1.get_assessment_sustainability_arrays().items)
    for appliance in range(0, len(appliances)):
        name = appliances[appliance].name
        esg_info[name] = {
            "insights": [],
            "location": {},
            "assessment": {},
            "reporting_status": {},
        }
        if getattr(appliances[appliance], "install_address", False):
            esg_info[name]["location"] = {
                "longitude": getattr(
                    appliances[appliance].install_address.geolocation,
                    "longitude",
                    None,
                ),
                "latitude": getattr(
                    appliances[appliance].install_address.geolocation,
                    "latitude",
                    None,
                ),
                "updated": getattr(
                    appliances[appliance].install_address,
                    "updated",
                    None,
                ),
                "address": getattr(
                    appliances[appliance].install_address,
                    "street_address",
                    None,
                ),
            }
            if esg_info[name]["location"]["updated"]:
                esg_info[name]["location"]["updated"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S UTC",
                    time.gmtime(esg_info[name]["location"]["updated"] / 1000),
                )
        if appliances[appliance].reporting_status != "assessment_ready":
            esg_info[name]["reporting_status"] = appliances[appliance].reporting_status
        else:
            esg_info[name]["assessment"] = {
                "array_data_reduction": getattr(
                    appliances[appliance].assessment, "array_data_reduction", None
                ),
                "assessment_level": getattr(
                    appliances[appliance].assessment, "assessment_level", None
                ),
                "blades": getattr(appliances[appliance].assessment, "blades", None),
                "capacity_utilization": getattr(
                    appliances[appliance].assessment, "capacity_utilization", None
                ),
                "chassis": getattr(appliances[appliance].assessment, "chassis", None),
                "power_average": getattr(
                    appliances[appliance].assessment, "power_average", None
                ),
                "power_per_usable_capacity": getattr(
                    appliances[appliance].assessment, "power_per_usable_capacity", None
                ),
                "power_per_used_space": getattr(
                    appliances[appliance].assessment, "power_per_used_space", None
                ),
                "power_typical_spec": getattr(
                    appliances[appliance].assessment, "power_typical_spec", None
                ),
                "power_peak_spec": getattr(
                    appliances[appliance].assessment, "power_peak_spec", None
                ),
                "heat_typical_spec": getattr(
                    appliances[appliance].assessment, "heat_typical_spec", None
                ),
                "heat_peak_spec": getattr(
                    appliances[appliance].assessment, "heat_peak_spec", None
                ),
                "heat_average": getattr(
                    appliances[appliance].assessment, "heat_average", None
                ),
                "rack_units": getattr(
                    appliances[appliance].assessment, "rack_units", None
                ),
                "shelves": getattr(appliances[appliance].assessment, "shelves", None),
                "array_total_load": getattr(
                    appliances[appliance].assessment, "array_total_load", None
                ),
                "start": getattr(
                    appliances[appliance].assessment, "interval_start", None
                ),
                "end": getattr(appliances[appliance].assessment, "interval_end", None),
            }
            if esg_info[name]["assessment"]["start"]:
                esg_info[name]["assessment"]["start"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S UTC",
                    time.gmtime(esg_info[name]["assessment"]["start"] / 1000),
                )
            if esg_info[name]["assessment"]["end"]:
                esg_info[name]["assessment"]["end"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S UTC",
                    time.gmtime(esg_info[name]["assessment"]["end"] / 1000),
                )
    insights = list(pure_1.get_assessment_sustainability_insights_arrays().items)
    for insight in range(0, len(insights)):
        name = getattr(insights[insight].resource, "name", None)
        if name:
            esg_info[name]["insights"].append(
                {
                    "fqdn": insights[insight].resource.fqdn,
                    "type": insights[insight].type,
                    "severity": insights[insight].severity,
                    "insight_data": insights[insight].additional_data,
                }
            )
    return esg_info


def generate_contract_dict(pure_1):
    contract_info = {}
    grace_period = 2592000000  # 30 days in ms
    contract_start_epoch = None
    contract_end_epoch = None
    current_date = int(time.time() * 1000)
    appliances = list(pure_1.get_arrays().items)
    for appliance in range(0, len(appliances)):
        contract_state = "Expired"
        name = appliances[appliance].name
        contract_info[name] = {}
        contract_data = list(
            pure_1.get_arrays_support_contracts(
                filter="resource.name='" + name + "'"
            ).items
        )
        if contract_data:
            contract_start_epoch = getattr(contract_data[0], "start_date", None)
            contract_end_epoch = getattr(contract_data[0], "end_date", None)
            if contract_start_epoch:
                contract_start = datetime.datetime.fromtimestamp(
                    int(contract_start_epoch / 1000)
                ).strftime("%Y-%m-%d")
            if contract_end_epoch:
                contract_end = datetime.datetime.fromtimestamp(
                    int(contract_end_epoch / 1000)
                ).strftime("%Y-%m-%d")
            contract_info[name]["contract_start"] = contract_start
            contract_info[name]["contract_end"] = contract_end
            if contract_end_epoch:
                if current_date <= contract_end_epoch:
                    contract_state = "Active"
                elif contract_end_epoch + grace_period >= current_date:
                    contract_state = "Grace Period"
        contract_info[name]["contract_state"] = contract_state
    return contract_info


def generate_invoices_dict(module, pure_1):
    invoices_info = {}
    res = pure_1.get_invoices()
    if res.status_code == 200:
        invoices = list(res.items)
        for invoice in len(0, len(invoices)):
            name = invoices[invoice].id
            invoice_date = getattr(invoices[invoice], "date", None)
            invoice_due_date = getattr(invoices[invoice], "due_date", None)
            invoice_ship_date = getattr(invoices[invoice], "ship_date", None)
            if invoice_date:
                inv_date = datetime.datetime.fromtimestamp(
                    int(invoice_date / 1000)
                ).strftime("%Y-%m-%d")
            else:
                inv_date = None
            if invoice_due_date:
                inv_due_date = datetime.datetime.fromtimestamp(
                    int(invoice_due_date / 1000)
                ).strftime("%Y-%m-%d")
            else:
                inv_due_date = None
            if invoice_ship_date:
                inv_ship_date = datetime.datetime.fromtimestamp(
                    int(invoice_ship_date / 1000)
                ).strftime("%Y-%m-%d")
            else:
                inv_date = None

            invoices_info[name] = {
                "lines": {},
                "status": getattr(invoices[invoice], "status", None),
                "amount": getattr(invoices[invoice], "amount", 0),
                "date": inv_date,
                "due_date": inv_due_date,
                "ship_date": inv_ship_date,
                "payment_terms": getattr(invoices[invoice], "payment_terms", None),
                "sales_rep": getattr(invoices[invoice], "sales_representative", None),
                "partner_po": getattr(
                    invoices[invoice], "partner_purchase_order", None
                ),
                "end_user_po": getattr(
                    invoices[invoice], "end_user_purchase_order", None
                ),
                "end_user_name": getattr(
                    invoices[invoice], "end_user_purchase_name", None
                ),
                "subscription_id": getattr(invoices[invoice].subscription, "id", None),
                "subscription_name": getattr(
                    invoices[invoice].subscription, "name", None
                ),
            }
            for line in range(0, len(invoices[invoice].lines)):
                line_start_date = (
                    getattr(invoices[invoice].lines[line], "start_date", None),
                )
                line_end_date = (
                    getattr(invoices[invoice].lines[line], "end_date", None),
                )
                if line_start_date:
                    start_date = datetime.datetime.fromtimestamp(
                        int(line_start_date / 1000)
                    ).strftime("%Y-%m-%d")
                else:
                    start_date = None
                if line_end_date:
                    end_date = datetime.datetime.fromtimestamp(
                        int(line_end_date / 1000)
                    ).strftime("%Y-%m-%d")
                else:
                    end_date = None
                invoices_info[invoice]["lines"].append(
                    {
                        "item": getattr(invoices[invoice].lines[line], "item", None),
                        "quantity": getattr(
                            invoices[invoice].lines[line], "quantity", 0
                        ),
                        "description": getattr(
                            invoices[invoice].lines[line], "description", None
                        ),
                        "start_date": start_date,
                        "end_date": end_date,
                        "components": invoices[invoice].lines[line]["components"],
                        "unit_price": getattr(
                            invoices[invoice].lines[line], "unit_price", 0
                        ),
                        "amount": getattr(invoices[invoice].lines[line], "amount", 0),
                        "tax_percentage": getattr(
                            invoices[invoice].lines[line].tax, "percentage", 0
                        ),
                        "tax_amount": getattr(
                            invoices[invoice].lines[line].tax, "amount", 0
                        ),
                        "tax_exemption_statement": getattr(
                            invoices[invoice].lines[line].tax,
                            "exemption_statement",
                            None,
                        ),
                    }
                )
    return invoices_info


def generate_appliances_dict(module, pure_1):
    names_info = {"FlashArray": {}, "FlashBlade": {}, "ObjectEngine": {}}
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
            try:
                names_info["FlashArray"][name]["bandwidth (read) [MB/s]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_read_bandwidth"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 104857600,
                    3,
                )
            except IndexError:
                pass
            try:
                names_info["FlashArray"][name]["bandwidth (write) [MB/s]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_write_bandwidth"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 104857600,
                    3,
                )
            except IndexError:
                pass
            try:
                names_info["FlashArray"][name]["latency (read) [ms]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_read_latency_us"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 1000,
                    2,
                )
            except IndexError:
                pass
            try:
                names_info["FlashArray"][name]["latency (write) [ms]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_write_latency_us"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 1000,
                    2,
                )
            except IndexError:
                pass
            try:
                names_info["FlashArray"][name]["iops (read)"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_read_iops"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                )
            except IndexError:
                pass
            try:
                names_info["FlashArray"][name]["iops (write)"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_write_iops"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                )
            except IndexError:
                pass
            try:
                names_info["FlashArray"][name]["load [%]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_total_load"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    * 100,
                    3,
                )
            except IndexError:
                pass
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
            try:
                names_info["FlashBlade"][name]["bandwidth (read) [MB/s]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_read_bandwidth"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 104857600,
                    3,
                )
            except IndexError:
                pass
            try:
                names_info["FlashBlade"][name]["bandwidth (write) [MB/s]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_write_bandwidth"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 104857600,
                    3,
                )
            except IndexError:
                pass
            try:
                names_info["FlashBlade"][name]["iops (read)"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_read_iops"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                )
            except IndexError:
                pass
            try:
                names_info["FlashBlade"][name]["iops (write)"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_write_iops"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                )
            except IndexError:
                pass
            try:
                names_info["FlashBlade"][name]["latency (read) [ms]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_read_latency_us"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 1000,
                    2,
                )
            except IndexError:
                pass
            try:
                names_info["FlashBlade"][name]["latency (write) [ms]"] = round(
                    list(
                        pure_1.get_metrics_history(
                            names=["array_write_latency_us"],
                            resource_names=[name],
                            aggregation="max",
                            resolution=180000,
                            end_time=int(time.time()) * 1000,
                            start_time=(int(time.time()) * 1000) - 18000000,
                        ).items
                    )[0].data[-1][1]
                    / 1000,
                    2,
                )
            except IndexError:
                pass
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

    module = AnsibleModule(argument_spec, supports_check_mode=True)
    pure_1 = get_pure1(module)

    subset = [test.lower() for test in module.params["gather_subset"]]
    valid_subsets = (
        "all",
        "minimum",
        "appliances",
        "subscriptions",
        "contracts",
        "environmental",
        "invoices",
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
        info["subscription_licenses"] = generate_subscription_licenses_dict(pure_1)
        # info["subscription_assets"] = generate_subscription_assets_dict(pure_1)
    if "contracts" in subset or "all" in subset:
        info["contracts"] = generate_contract_dict(pure_1)
    if "environmental" in subset or "all" in subset:
        info["environmental"] = generate_esg_dict(module, pure_1)
    if "invoices" in subset or "all" in subset:
        info["invoices"] = generate_invoices_dict(module, pure_1)

    module.exit_json(changed=False, pure1_info=info)


if __name__ == "__main__":
    main()
