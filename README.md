# Pure Storage Pure1 Collection

The Pure Storage Pure1 collection consists of the latest versions of the Pure1 modules.

## Modules

## Requirements

- Ansible 2.9 or later
- Authorized API Application ID for Pure Storage Pure1 and associated Private Key
  Refer to Pure Storage documentation on how to create these. 
- py-pure-client >= 1.14.1
- time
- datetime

## Available Modules

- pure1_array_tags - Manage array tags for managed devices in Pure1
- pure1_info - Get information on fleet configuration

## Instructions

Install the Pure Storage Pure1 collection on your Ansible management host.

- Using ansible-galaxy (Ansible 2.9 or later):
```
ansible-galaxy collection install purestorage.pure1 -p ~/.ansible/collections
```

## Example Playbook
```yaml
- hosts: localhost
  collections:
    - purestorage.pure1
  tasks:
  - name: Collect information for Pure Storage fleet in Pure1
    pure1_info:
      gather_subset: all
      app_id: <Pure1 API Application ID>
      key_file: <private key file name>
      password: <private key password>
```

## License

[BSD-2-Clause](https://directory.fsf.org/wiki?title=License:FreeBSD)
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Author

This collection was created in 2020 by [Simon Dodsley](@sdodsley) for, and on behalf of, the [Pure Storage Ansible Team](pure-ansible-team@purestorage.com)
