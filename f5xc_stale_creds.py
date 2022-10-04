#!/usr/bin/env python3
import argparse, json, sys
from helper import F5xcSession, getLogger, writeCSV

def main():
    ap = argparse.ArgumentParser(
        prog='f5xc_stale_creds',
        usage='%(prog)s [options]',
        description='find and, optionally, remove stale f5xc credentials from a tenant'
    )
    ap.add_argument(
        '--tenant',
        help='tenant url (ex. "https://foo.console.ves.volterra.io")',
        default='https://f5-gsa.console.ves.volterra.io',
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
        help='days since API cred expired',
        type=int,
        default=30,
        required=False
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
        help='remove stale credentials',
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
    logger = getLogger('stale_users', level)
    try:
        xcSession = F5xcSession(args.token, args.tenant)
        logger.debug('created XC session')
        stale = xcSession.staleApiCreds(args.stale_days)
        if stale:
            logger.info('found {} stale API credentials'.format(len(stale)))
        else:
            logger.info('no stale API credentials found. Exiting.')
            sys.exit(0)
    except Exception as e:
        logger.debug(e)
        logger.info('Error creation XC session and retrieving API credentials. Exiting.')
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
    if args.remove:
        for cred in stale:
            if cred['type'] == 'SITE_GLOBAL_KUBE_CONFIG':
                logger.info('API credential {0} is a global kubeconfig. skipping.'.format(cred['name']))
                continue
            else:   
                try:
                    xcSession.deleteApiCred(cred['name'], cred['namespace'])
                    logger.info('cred {} removed.'.format(cred['name']))
                except Exception as e:
                    logger.info('Error removing stale API credential {0}: {1}. skipping.'.format(cred['name'], e))
                    continue 
    logger.info('Done. Exiting.')
    sys.exit(0)

if __name__ == '__main__':
    main()