===============================
Purestorage.Pure1 Release Notes
===============================

.. contents:: Topics


v1.3.0
======

Minor Changes
-------------

- Fixed issue with use of environmental variables for key, key file and password
- password parameter is now optional, to allow for unprotected key files
- pure1_info.py - Added more subscrition detail

New Modules
-----------

- purestorage.pure1.pure1_nics - Collect network interface information from Pure1
- purestorage.pure1.pure1_pods - Collect FlashArray pod information from Pure1
- purestorage.pure1.pure1_ports - Collect FlashArray port information from Pure1
- purestorage.pure1.pure1_volumes - Collect volumes information from Pure1

v1.2.0
======

Minor Changes
-------------

- pure1_info - Add environmental subset for ESG data and platform insights

v1.1.0
======

Minor Changes
-------------

- All - Update documentation to use FQCNs
- pure1_info - Add array performance data and load (FA only). Add support contract status.

New Modules
-----------

- purestorage.pure1.pure1_alerts - Collect array alerts from Pure1 based on severity
- purestorage.pure1.pure1_network_interfaces - Collect array netowrk interface details from Pure1

v1.0.0
======

Major Changes
-------------

- pure1_array_tags - New module to manage Pure1 array tags
- pure1_info - New module for gathering Pure1 information
