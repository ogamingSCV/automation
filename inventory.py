#!/usr/bin/env python3
import json
import sys
import subprocess

def load_inventory():
    try:
        output = subprocess.check_output(["tofu", "output", "-json"], cwd="/root/tofu-proxmox-lxc")
        raw = json.loads(output)

        # Adjust if wrapped inside an "ansible_inventory" output
        if "ansible_inventory" in raw:
            return raw["ansible_inventory"]["value"]
        elif "value" in raw:
            return raw["value"]
        else:
            return {}

    except Exception as e:
        print(f"Failed to load inventory: {e}", file=sys.stderr)
        return {}

def build_inventory(data):
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": list(data.keys()),
            "vars": {}
        }
    }

    for host, attrs in data.items():
        inventory["_meta"]["hostvars"][host] = attrs
        for tag in attrs.get("tags", []):
            if tag not in inventory:
                inventory[tag] = {"hosts": []}
            inventory[tag]["hosts"].append(host)

    return inventory

def main():
    if "--list" in sys.argv:
        data = load_inventory()
        print(json.dumps(build_inventory(data), indent=2))
    else:
        print(json.dumps({}))

if __name__ == "__main__":
    main()