#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import argparse
from librouteros import connect
from librouteros.login import login_plain, login_token


def stats(api, mac):
    ap_clients = api(cmd='/caps-man/registration-table/print', stats=True)
    dhcp_leases = api(cmd='/ip/dhcp-server/lease/print')
    for ap_client in ap_clients:
        if mac == ap_client['mac-address']:
            for lease in dhcp_leases:
                if lease['mac-address'] == mac:
                    print(json.dumps({"tx-bytes": ap_client['bytes'].split(",")[0],
                                      "rx-bytes": ap_client['bytes'].split(",")[1],
                                      "tx-packets": ap_client['packets'].split(",")[0],
                                      "rx-packets": ap_client['packets'].split(",")[1],
                                      "rx-signal": ap_client['rx-signal'],
                                      "cap": ap_client['interface'],
                                      "ip-address": lease['active-address']}))
                    sys.exit()


def ssid(api, ssid):
    result = 0
    ap_clients = api(cmd='/caps-man/registration-table/print', stats=True)
    for client in ap_clients:
        if client['ssid'] == ssid:
            result += 1
    print(result)
    sys.exit()


def summary(api):
    ap_clients = api(cmd='/caps-man/registration-table/print', stats=True)
    print(len(ap_clients))
    sys.exit()


def discovery(api):
    ap_discovery = []
    ap_clients = api(cmd='/caps-man/registration-table/print', stats=True)
    dhcp_leases = api(cmd='/ip/dhcp-server/lease/print')

    for ap_client in ap_clients:
        mac = ap_client['mac-address']
        for lease in dhcp_leases:
            if lease['mac-address'] == mac:
                hostname = lease.get('comment', '')
                if not hostname:
                    hostname = lease.get('host-name', ap_client['mac-address'])
                ap_discovery.append({'{#WIFIMAC}': ap_client['mac-address'], '{#WIFINAME}': hostname})

    print(json.dumps({"data": ap_discovery}))
    sys.exit()


def auth(host, username, password):
    method = (login_plain, )
    try:
        api = connect(username=username, password=password, host=host, login_methods=method)
    except:
        return False
    return api


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    subparsers = parser.add_subparsers(title="commands", metavar="COMMAND", dest='command')
    parser_discovery = subparsers.add_parser("discovery", help="discovery connected wifi clients")
    parser_discovery = subparsers.add_parser("summary", help="summary information about connected wifi clients")
    parser_stat = subparsers.add_parser("stats", help="statistic for connected wifi clients")
    parser_stat.add_argument("--mac", required=True)
    parser_stat = subparsers.add_parser("ssid", help="statistic for ssid connected wifi clients")
    parser_stat.add_argument("--name", required=True)

    args = parser.parse_args()
    api = auth(host=args.host, username=args.username, password=args.password)
    if not api:
        print("Wrong username or password")
        sys.exit(1)

    if args.command == 'discovery':
        discovery(api)
    elif args.command == 'stats':
        stats(api, args.mac)
    elif args.command == 'summary':
        summary(api)
    elif args.command == 'ssid':
        ssid(api, args.name)
