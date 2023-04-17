#!/usr/bin/env python3
import argparse, json, sys
from helper import F5xcSession, getLogger, writeCSV

def main():
    ap = argparse.ArgumentParser(
        prog='f5xc_stale_ns',
        usage='%(prog)s [options]',
        description='find and, optionally, remove stale f5xc namespaces from a tenant'
    )
    ap.add_argument(
        '--tenant',
        help='tenant url (ex. "https://foo.console.ves.volterra.io")',
        default='https://f5-channel.console.ves.volterra.io',
        required=False
    )
    ap.add_argument(
        '--token',
        help='auth token for tenant',
        type=str,
        required=True
    )
    ap.add_argument(
        '--stale_days',
        help='days since created/used',
        type=int,
        required=False,
        default=5
    )
    ap.add_argument(
        '--ephemeral',
        help='namespace is ephemeral',
        type=bool,
        required=False,
        default=True
    )
    ap.add_argument(
        '--csv',
        help='output results to csv file named "results.csv".',
        default=False,
        action='store_true',
        required=False
    )
    ap.add_argument(
        '--remove',
        help='remove stale namespaces',
        default=False,
        action='store_true',
        required=False
    )
    ap.add_argument(
        '--log',
        help='add "debug" logging',
        default=False,
        action='store_true',
        required=False
    )
    args = ap.parse_args()
    if args.log:
        level = 'DEBUG'
    else:
        level = 'INFO'
    logger = getLogger('stale_namespaces', level)
    try:
        xcSession = F5xcSession(args.token, args.tenant)
        logger.debug('created XC session')
        stale = xcSession.staleNSs(args.stale_days, True)
        if stale:
            logger.info('found {} stale Namespaces'.format(len(stale)))
        else:
            logger.info('no stale Namespaces found. Exiting.')
            sys.exit(0)
    except Exception as e:
        logger.debug(e)
        logger.info('Error creation XC session and retrieving namespaces. Exiting.')
        sys.exit(1)
    try:
        if args.csv:
            writeCSV(stale)
            logger.info('CSV written.')
        else:
            print(json.dumps(stale, sort_keys=False, indent=4, ensure_ascii=False))
    except Exception as e:
        logger.debug(e)
        logger.info('Error writing results. Exiting.')
        sys.exit(1)
    try:
        if args.remove:
            for ns in stale:
                try:
                    xcSession.deleteNS(ns['name'])
                    logger.info('Namespace {} removed.'.format(ns['name']))
                except Exception as e:
                    logger.info('Error removing stale namespace {0}: {1}'.format(ns['name'], e))
                    continue
    except Exception as e:
        logger.debug(e)
        logger.info('Error removing stale namespaces. Exiting.')
        sys.exit(1)
    logger.info('Done. Exiting.')
    sys.exit(0)

if __name__ == '__main__':
    main()