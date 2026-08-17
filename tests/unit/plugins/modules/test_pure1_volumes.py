# Copyright: (c) 2026, Everpure Ansible Team <pure-ansible-team@everpuredata.com>
# GNU General Public License v3.0+ (see COPYING.GPLv3 or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the pure1_volumes module."""

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

from plugins.modules.pure1_volumes import generate_volumes_dict


def _make_volume(**overrides):
    """Build a minimal Pure1 volume object as returned by the SDK."""
    volume = types.SimpleNamespace(
        id="abcd-1234",
        serial="ABC123",
        name="vol1",
        created=1609459200000,  # 2021-01-01 00:00:00 UTC, in milliseconds
        eradicated=False,
        destroyed=False,
        provisioned=1073741824,
        arrays=[
            types.SimpleNamespace(name="array1", fqdn="array1.example.com"),
        ],
    )
    for key, value in overrides.items():
        setattr(volume, key, value)
    return volume


def _client_returning(volumes):
    """A mocked Pure1 client whose get_volumes() yields the given volumes."""
    client = Mock()
    client.get_volumes.return_value = Mock(items=volumes)
    return client


class TestGenerateVolumesDict:
    """Tests for generate_volumes_dict."""

    def test_basic_volume_mapping(self):
        """A volume is keyed by serial with its core fields mapped."""
        module = Mock()
        module.params = {"array": None}
        client = _client_returning([_make_volume()])

        result = generate_volumes_dict(module, client)

        client.get_volumes.assert_called_once_with()
        assert "ABC123" in result
        entry = result["ABC123"]
        assert entry["id"] == "abcd-1234"
        assert entry["name"] == "vol1"
        assert entry["created"] == "2021-01-01 00:00:00 UTC"
        assert entry["provisioned"] == 1073741824
        assert entry["array"] == {
            "name": "array1",
            "fqdn": "array1.example.com",
        }
        assert entry["arrays"] == [
            {"name": "array1", "fqdn": "array1.example.com"},
        ]

    def test_volume_spanning_multiple_arrays(self):
        """A volume on more than one array lists them all under arrays."""
        module = Mock()
        module.params = {"array": None}
        volume = _make_volume(
            arrays=[
                types.SimpleNamespace(name="array1", fqdn="array1.example.com"),
                types.SimpleNamespace(name="array2", fqdn="array2.example.com"),
            ],
        )
        client = _client_returning([volume])

        result = generate_volumes_dict(module, client)

        entry = result["ABC123"]
        # array (singular) stays the first array for backwards compatibility
        assert entry["array"] == {"name": "array1", "fqdn": "array1.example.com"}
        assert entry["arrays"] == [
            {"name": "array1", "fqdn": "array1.example.com"},
            {"name": "array2", "fqdn": "array2.example.com"},
        ]

    def test_no_source_or_pod_defaults_to_empty_list(self):
        """Without a source/pod the fields stay as empty lists."""
        module = Mock()
        module.params = {"array": None}
        client = _client_returning([_make_volume()])

        result = generate_volumes_dict(module, client)

        assert result["ABC123"]["source"] == []
        assert result["ABC123"]["pod"] == []

    def test_source_and_pod_are_unwrapped_to_names(self):
        """A present source/pod is reduced to its name."""
        module = Mock()
        module.params = {"array": None}
        volume = _make_volume(
            source=types.SimpleNamespace(name="parentvol"),
            pod=types.SimpleNamespace(name="pod1"),
        )
        client = _client_returning([volume])

        result = generate_volumes_dict(module, client)

        assert result["ABC123"]["source"] == "parentvol"
        assert result["ABC123"]["pod"] == "pod1"

    def test_array_filter_is_applied(self):
        """The array param builds a Pure1 filter on arrays.name."""
        module = Mock()
        module.params = {"array": "myarray"}
        client = _client_returning([_make_volume()])

        generate_volumes_dict(module, client)

        client.get_volumes.assert_called_once_with(filter="arrays.name='myarray'")

    def test_multiple_volumes(self):
        """Every returned volume gets its own entry keyed by serial."""
        module = Mock()
        module.params = {"array": None}
        volumes = [
            _make_volume(serial="SERIAL1", name="vol-a"),
            _make_volume(serial="SERIAL2", name="vol-b"),
        ]
        client = _client_returning(volumes)

        result = generate_volumes_dict(module, client)

        assert set(result.keys()) == {"SERIAL1", "SERIAL2"}
        assert result["SERIAL1"]["name"] == "vol-a"
        assert result["SERIAL2"]["name"] == "vol-b"
