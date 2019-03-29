#!/usr/bin/env python

import json
import subprocess
import argparse
import sys


DESCRIPTION = """Parses StorCLI's JSON output and exposes MegaRAID health as
                 Zabbix metrics."""
VERSION = '0.0.1'


def get_storcli_json(storcli_path):
    storcli_cmd = [storcli_path, '/call', 'show', 'all', 'J']
    proc = subprocess.Popen(storcli_cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()[0]


def discover_controller(data):
    zabbix_discovery = []

    for ctrl_raw in data["Controllers"]:
        ctrl_data = ctrl_raw["Response Data"]

        controller = {
            "id": ctrl_data["Basics"]["Controller"],
            "model": ctrl_data["Basics"]["Model"],
            "serial": ctrl_data["Basics"]["Serial Number"],
        }

        zabbix_discovery.append({
            "{#CTRL}": controller["id"],
            "{#MODEL}": controller["model"],
            "{#SERIAL}": controller["serial"]
        })
        return json.dumps({"data": zabbix_discovery}, indent=4, sort_keys=True)


def discover_pd(data):
    zabbix_discovery = []

    for ctrl_raw in data["Controllers"]:
        ctrl_data = ctrl_raw["Response Data"]

        for pd_data in ctrl_data["PD LIST"]:
            pd = {
                "id": "{}/{}".format(ctrl_data["Basics"]["Controller"], pd_data["EID:Slt"]),
                "type": pd_data["Med"],
                "model": pd_data["Model"],
                "size": pd_data["Size"],
            }

            zabbix_discovery.append({
                "{#PD}": pd["id"],
                "{#NAME}": "{} {} [{}]".format(pd["size"], pd["type"], pd["model"])
            })
        return json.dumps({"data": zabbix_discovery}, indent=4, sort_keys=True)


def discover_vd(data):
    zabbix_discovery = []

    for ctrl_raw in data["Controllers"]:
        ctrl_data = ctrl_raw["Response Data"]
        for vd_data in ctrl_data["VD LIST"]:
            vd = {
                "id": "{}/{}".format(ctrl_data["Basics"]["Controller"], vd_data["DG/VD"]),
                "name": vd_data["Name"],
                "type": vd_data["TYPE"],
                "size": vd_data["Size"]
            }

            zabbix_discovery.append({
                "{#VD}": vd["id"],
                "{#NAME}": "{} {} [{}]".format(vd["size"], vd["type"], vd["name"])
            })
    return json.dumps({"data": zabbix_discovery}, indent=4, sort_keys=True)


def get_info(data):
    zabbix_info = {
        "ctrl": {},
        "vd": {},
        "pd": {}
    }

    for ctrl_raw in data["Controllers"]:
        ctrl_data = ctrl_raw["Response Data"]
        zabbix_info["ctrl"].update({
            ctrl_data["Basics"]["Controller"]: {
                "firmware": ctrl_data["Version"]["Firmware Version"],
                "status": ctrl_data["Status"]["Controller Status"],
                "temperature": ctrl_data["HwCfg"]["ROC temperature(Degree Celsius)"]
            }
        })

        for pd_data in ctrl_data["PD LIST"]:
            zabbix_info["pd"].update({
                "{}/{}".format(ctrl_data["Basics"]["Controller"], pd_data["EID:Slt"]): {
                    "state": pd_data["State"],
                }
            })

        for vd_data in ctrl_data["VD LIST"]:
            zabbix_info["vd"].update({
                "{}/{}".format(ctrl_data["Basics"]["Controller"], vd_data["DG/VD"]): {
                    "state": vd_data["State"],
                }
            })
    return json.dumps(zabbix_info, indent=4, sort_keys=True)


def main(args):
    data = json.loads(get_storcli_json(args.storcli_path))

    if args.discover_controller:
        print(discover_controller(data))

    elif args.discover_pd:
        print(discover_pd(data))

    elif args.discover_vd:
        print(discover_vd(data))

    elif args.get_info:
        print(get_info(data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--storcli_path',
                        default='/opt/MegaRAID/storcli/storcli64',
                        help='Path to StorCLi binary')

    g = parser.add_mutually_exclusive_group()
    g.add_argument('--discover-controller', action='store_true',
                   help='Discover controllers')
    g.add_argument('--discover-pd', action='store_true',
                   help='Discover physical disks')
    g.add_argument('--discover-vd', action='store_true',
                   help='Discover virtual disks')
    g.add_argument('--get-info', action='store_true',
                   help='Get health info')

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(VERSION))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    main(args)
