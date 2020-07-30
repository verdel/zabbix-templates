#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import datetime
import logging
import socket
import ssl
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger('SSLVerify')


def ssl_expiry_datetime(hostname: str, port: int = 443) -> datetime.datetime:
    socket.setdefaulttimeout(3.0)
    logger.debug('Connect to {}'.format(hostname))
    seednode_certificate = ssl.get_server_certificate(addr=(hostname, port))
    certificate = x509.load_pem_x509_certificate(seednode_certificate.encode(), backend=default_backend())
    return certificate.not_valid_after


def ssl_valid_time_remaining(hostname: str, port: int = 443) -> datetime.timedelta:
    """Get timedelta left in a cert's lifetime."""
    expires = ssl_expiry_datetime(hostname, port)
    logger.debug(
        'SSL cert for {} expires at {}'.format(
            hostname, expires.isoformat()
        )
    )
    return expires - datetime.datetime.utcnow()


def get_cert_status(hostname: str, port: int = 443) -> int:
    """Return certificate expiration status."""
    try:
        will_expire_in = ssl_valid_time_remaining(hostname, port)
    except ssl.CertificateError as e:
        return f'{hostname} cert error {e}'
    except ssl.SSLError as e:
        return f'{hostname} cert error {e}'
    except socket.timeout:
        return f'{hostname} could not connect'
    else:
        if will_expire_in < datetime.timedelta(days=0):
            return 0
        else:
            return 1


def get_cert_day_before_expire(hostname: str, port: int = 443) -> int:
    """Return day before certificate expiration."""
    try:
        will_expire_in = ssl_valid_time_remaining(hostname, port)
    except ssl.CertificateError as e:
        return f'{hostname} cert error {e}'
    except ssl.SSLError as e:
        return f'{hostname} cert error {e}'
    except socket.timeout:
        return f'{hostname} could not connect'
    else:
        return will_expire_in.days


def cli():
    parser = argparse.ArgumentParser(description='Tool for check the status or expiration date of ssl certificate')
    parser.add_argument('--host', required=True,
                        help='server hostname'
                        )
    parser.add_argument('--port', default=443,
                        help='server port'
                        )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--status', action='store_true',
                       help='get certificate status')
    group.add_argument('--day-before-expire', action='store_true',
                       help='get number of days before certificate expiration')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug level logging')
    return parser.parse_args()


if __name__ == '__main__':
    args = cli()
    if args.debug:
        loglevel = 'DEBUG'
    else:
        loglevel = os.environ.get('LOGLEVEL', 'INFO')
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

    logger.debug('Testing host {}'.format(args.host))
    if args.status:
        message = get_cert_status(args.host, args.port)
    elif args.day_before_expire:
        message = get_cert_day_before_expire(args.host, args.port)
    print(message)
