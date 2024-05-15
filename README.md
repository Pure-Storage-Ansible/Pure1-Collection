<a href="https://github.com/Pure-Storage-Ansible/Pure1-Collection/releases/latest"><img src="https://img.shields.io/github/v/tag/Pure-Storage-Ansible/Pure1-Collection?label=release">
<a href="COPYING.GPLv3"><img src="https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg"></a>
<img src="https://cla-assistant.io/readme/badge/Pure-Storage-Ansible/Pure1-Collection">
<img src="https://github.com/Pure-Storage-Ansible/Pure1-Collection/workflows/Pure%20Storage%20Ansible%20CI/badge.svg">
<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

# Pure Storage Pure1 Collection

## Description

The Pure Storage Pure1 collection consists of the latest versions of the Pure1 modules.

## Requirements

- Ansible 2.15.0 or later
- Authorized API Application ID for Pure Storage Pure1 and associated Private Key
  Refer to Pure Storage documentation on how to create these.
- python >= 3.9 
- py-pure-client
- datetime

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```
ansible-galaxy collection install purestorage.pure1
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```
collections:
  - name: purestorage.pure1
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the Ansible package. 

To upgrade the collection to the latest available version, run the following command:

```
ansible-galaxy collection install purestorage.pure1 --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version 1.0.0:

```
ansible-galaxy collection install purestorage.pure1:==1.0.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

### Example Playbook
```yaml
- hosts: localhost
  tasks:
  - name: Collect information for Pure Storage fleet in Pure1
    purestorage.pure1.pure1_info:
      gather_subset: all
      app_id: <Pure1 API Application ID>
      key_file: <private key file name>
      password: <private key password>
```

## Contributing

There are many ways in which you can participate in the project, for example:

* Submit bugs and feature requests, and help us verify as they are checked in
* Review source code changes
* Review the documentation and make pull requests for anything from typos to new content
* If you are interested in fixing issues and contributing directly to the code base, please see the details below:
    1. Fork this project into your account if you are a first-time contributor.
    2. Create a branch based on the latest `master` branch, commit your changes on this branch.
    3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.
 
## Support

Only the latest release of this collection is supported.

For support please raise a GitHub Issue on this repository.

If you are a Pure Storage customer, you may log a support call with the Pure Storage Support team ([support\@purestorage.com](mailto:support@purestorage.com?subject=Pure1-Ansible-Collection))

If you have a Red Hat Ansible support contract, as this is a Certified collection, you may log a support call with Red Hat directly.
  
## Release Notes

Release notes for this collection can be found [here](https://github.com/Pure-Storage-Ansible/Pure1-Collection/releases)

## Related Information
### Available Modules

- pure1_alerts - Get alerts from Pure1
- pure1_array_tags - Manage array tags for managed devices in Pure1
- pure1_info - Get information on fleet configuration
- pure1_nics - Get network interface information from Pure1
- pure1_pods - Get FlashArray pod information from Pure1
- pure1_ports - Get port information from Pure1
- pure1_volumes - Get FlashArray volume information from Pure1

## License

[BSD-2-Clause](https://directory.fsf.org/wiki?title=License:FreeBSD)

[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Author

This collection was created in 2020 by [Simon Dodsley](@sdodsley) for, and on behalf of, the [Pure Storage Ansible Team](pure-ansible-team@purestorage.com)
