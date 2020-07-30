#!/usr/bin/env python3

import urllib.request
import urllib.error
import re
import argparse
import sys


DESCRIPTION = """Parses Squid manager authenticator of external_acl
                 output and exposes status of processes running too long
                 as Zabbix metrics."""
VERSION = '0.0.1'


def main(args):
    zabbix_metric = 0
    url = 'http://{}:{}/squid-internal-mgr/{}'.format(args.squid_host,
                                                      args.squid_port,
                                                      args.type)
    try:
        f = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print('HTTPError: {}'.format(e.code))
    except urllib.error.URLError as e:
        print('URLError: {}'.format(e.reason))
    else:
        data = f.read().decode('utf-8')
        pattern = re.compile(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)([\s|BCRSP]+)\s+([\d|\.]+)\s+(\d+)\s+(.*)$',
                             re.MULTILINE)
        result = re.findall(pattern, data)
        if len(result):
            for match in result:
                match_flag = re.sub(r'\s+', '', match[5])
                if match_flag == 'B' and float(match[6]) > args.time_limit:
                    zabbix_metric = 1
        print(zabbix_metric)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--squid-host',
                        default='localhost',
                        help='Squid manager host address')
    parser.add_argument('--squid-port',
                        default='3128',
                        help='Squid manager port')
    parser.add_argument('--type',
                        choices=['negotiateauthenticator',
                                 'ntlmauthenticator',
                                 'basicauthenticator',
                                 'external_acl'],
                        required=True,
                        help='Type of authenticator or external_acl')
    parser.add_argument('--time-limit',
                        default=1,
                        help='Set time limit for request execution in seconds')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(VERSION))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    main(args)
