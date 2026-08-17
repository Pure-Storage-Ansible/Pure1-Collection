# Copyright: (c) 2026, Everpure Ansible Team <pure-ansible-team@everpuredata.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the pure1_volume_metrics module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import types
from unittest.mock import Mock, MagicMock

# Mock external dependencies before importing the module
sys.modules["ansible"] = MagicMock()
sys.modules["ansible.module_utils"] = MagicMock()
sys.modules["ansible.module_utils.basic"] = MagicMock()
sys.modules["pypureclient"] = MagicMock()
sys.modules["pypureclient.pure1"] = MagicMock()
sys.modules["ansible_collections"] = MagicMock()
sys.modules["ansible_collections.everpure"] = MagicMock()
sys.modules["ansible_collections.everpure.pure1"] = MagicMock()
sys.modules["ansible_collections.everpure.pure1.plugins"] = MagicMock()
sys.modules["ansible_collections.everpure.pure1.plugins.module_utils"] = MagicMock()
sys.modules["ansible_collections.everpure.pure1.plugins.module_utils.pure1"] = (
    MagicMock()
)

from plugins.modules.pure1_volume_metrics import (
    generate_metrics_dict,
    list_volume_metrics,
    MAX_TIME_SERIES,
)


def _make_volume(serial="ABC123", name="vol1", vid="id-1"):
    return types.SimpleNamespace(serial=serial, name=name, id=vid)


def _make_series(vid, vname, metric, data, unit="B"):
    return types.SimpleNamespace(
        name=metric,
        unit=unit,
        resources=[types.SimpleNamespace(id=vid, name=vname)],
        data=data,
    )


def _module(**params):
    defaults = {
        "array": None,
        "volumes": None,
        "metrics": ["volume_total_used"],
        "aggregation": "avg",
        "resolution": 86400000,
        "window": 86400,
        "list_available": False,
    }
    defaults.update(params)
    module = Mock()
    module.params = defaults
    return module


class TestListVolumeMetrics:
    def test_catalog_is_mapped(self):
        client = Mock()
        client.get_metrics.return_value = Mock(
            items=[
                types.SimpleNamespace(
                    name="volume_total_used",
                    unit="B",
                    description="Used space",
                    resource_types=["volumes"],
                ),
            ]
        )

        result = list_volume_metrics(client)

        client.get_metrics.assert_called_once_with(resource_types=["volumes"])
        assert result == [
            {
                "name": "volume_total_used",
                "unit": "B",
                "description": "Used space",
                "resource_types": ["volumes"],
            }
        ]


class TestGenerateMetricsDict:
    def test_latest_data_point_is_used(self):
        module = _module()
        client = Mock()
        client.get_volumes.return_value = Mock(items=[_make_volume()])
        client.get_metrics_history.return_value = Mock(
            status_code=200,
            items=[
                _make_series(
                    "id-1",
                    "vol1",
                    "volume_total_used",
                    [[1000, 10], [2000, 25]],
                ),
            ],
        )

        result = generate_metrics_dict(module, client)

        entry = result["ABC123"]
        assert entry["id"] == "id-1"
        assert entry["name"] == "vol1"
        assert entry["metrics"]["volume_total_used"] == {
            "unit": "B",
            "timestamp": 2000,
            "value": 25,
        }

    def test_volume_without_data_is_still_present(self):
        module = _module()
        client = Mock()
        client.get_volumes.return_value = Mock(items=[_make_volume()])
        client.get_metrics_history.return_value = Mock(status_code=200, items=[])

        result = generate_metrics_dict(module, client)

        assert result["ABC123"]["metrics"] == {}

    def test_array_filter_is_applied(self):
        module = _module(array="myarray")
        client = Mock()
        client.get_volumes.return_value = Mock(items=[_make_volume()])
        client.get_metrics_history.return_value = Mock(status_code=200, items=[])

        generate_metrics_dict(module, client)

        client.get_volumes.assert_called_once_with(filter="arrays.name='myarray'")

    def test_volumes_name_filter_is_applied(self):
        module = _module(volumes=["vol1", "vol2"])
        client = Mock()
        client.get_volumes.return_value = Mock(items=[_make_volume()])
        client.get_metrics_history.return_value = Mock(status_code=200, items=[])

        generate_metrics_dict(module, client)

        client.get_volumes.assert_called_once_with(names=["vol1", "vol2"])

    def test_batches_respect_time_series_limit(self):
        # Two metrics => at most 16 volumes per call (32 / 2).
        module = _module(metrics=["m1", "m2"])
        volumes = [_make_volume(serial="S%d" % i, vid="id-%d" % i) for i in range(40)]
        client = Mock()
        client.get_volumes.return_value = Mock(items=volumes)
        client.get_metrics_history.return_value = Mock(status_code=200, items=[])

        generate_metrics_dict(module, client)

        per_call = MAX_TIME_SERIES // 2
        for call in client.get_metrics_history.call_args_list:
            assert len(call.kwargs["resource_ids"]) <= per_call
        # 40 volumes / 16 per call => 3 calls
        assert client.get_metrics_history.call_count == 3

    def test_failed_batch_is_skipped(self):
        module = _module()
        client = Mock()
        client.get_volumes.return_value = Mock(items=[_make_volume()])
        client.get_metrics_history.return_value = Mock(
            status_code=400, errors="boom", items=[]
        )

        result = generate_metrics_dict(module, client)

        module.warn.assert_called()
        assert result["ABC123"]["metrics"] == {}
