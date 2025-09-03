#!/usr/bin/env python3
import json
import sys
import subprocess
import re

def safe_group(name):
    """Make sure group names are safe for Ansible"""
    return re.sub(r'[^A-Za-z0-9_]', '_', name)

def load_inventory():
    try:
        output = subprocess.check_output(
            ["tofu", "output", "-json"],
            cwd="/root/tofu-proxmox-lxc"
        )
        raw = json.loads(output)
        return raw.get("ansible_inventory", {}).get("value", {})
    except Exception as e:
        print(f"Failed to load inventory: {e}", file=sys.stderr)
        return {}

def build_inventory(data):
    inventory = {"_meta": {"hostvars": {}}, "all": {"hosts": [], "vars": {}}}

    for host, attrs in data.items():
        # Strip out any null values
        clean_attrs = {k: v for k, v in attrs.items() if v is not None}
        inventory["_meta"]["hostvars"][host] = clean_attrs
        inventory["all"]["hosts"].append(host)

        # Group by tags
        for tag in clean_attrs.get("host_tags", []):
            group = f"tag_{safe_group(tag)}"
            inventory.setdefault(group, {"hosts": []})["hosts"].append(host)

        # Group by roles
        for role in clean_attrs.get("host_roles", []):
            group = f"role_{safe_group(role)}"
            inventory.setdefault(group, {"hosts": []})["hosts"].append(host)

    return inventory

def main():
    if "--list" in sys.argv:
        data = load_inventory()
        print(json.dumps(build_inventory(data), indent=2))
    else:
        print(json.dumps({}))

if __name__ == "__main__":
    main()