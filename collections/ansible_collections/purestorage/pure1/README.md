# Pure Storage Pure1 Collection

The Pure Storage Pure1 collection consists of the latest versions of the Pure1 modules.

## Modules

## Requirements

- Ansible 2.9 or later
- Access to Pure Storage Pure1
- py-pure-client Python SDK

## Instructions

Install the Pure Storage Pure1 collection on your Ansible management host.

- Using ansible-galaxy (Ansible 2.9 or later):
```
ansible-galaxy collection install purestorage.pure1 -p ~/.ansible/collections
```

## Example Playbook
```yaml
- hosts: localhost
  gather_facts: true
  collections:
    - puestorage.pure1
  tasks:
```

## License

[BSD-2-Clause](https://directory.fsf.org/wiki?title=License:FreeBSD)
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Author

This collection was created in 2020 by [Simon Dodsley](@sdodsley) for, and on behalf of, the [Pure Storage Ansible Team](pure-ansible-team@purestorage.com)
