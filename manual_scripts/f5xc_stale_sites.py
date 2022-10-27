#!/usr/bin/env python3
import argparse, json, sys
from manual_scripts.helper import F5xcSession, getLogger, writeCSV

def main():
    ap = argparse.ArgumentParser(
        prog='f5xc_stale_sites',
        usage='%(prog)s [options]',
        description='find and, optionally, remove stale f5xc sites from a tenant'
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
        help='days since site was last seen',
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
        help='remove stale sites',
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
    logger = getLogger('stale_sites', level)
    try:
        xcSession = F5xcSession(args.token, args.tenant)
        logger.debug('created XC session')
        stale = xcSession.staleSites(args.stale_days)
        if stale:
            logger.info('found {} stale sites'.format(len(stale)))
        else:
            logger.info('no stale sites found. Exiting.')
            sys.exit(0)
    except Exception as e:
        logger.debug(e)
        logger.info('Error creation XC session and retrieving sites. Exiting.')
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
        for site in stale:
            try:
                xcSession.deleteSite(site)
                logger.info('site {} removed.'.format(site['name']))
            except Exception as e:
                logger.info('Error removing stale site {0}: {1}. skipping.'.format(site['name'], e))
                continue 
    logger.info('Done. Exiting.')
    sys.exit(0)

if __name__ == '__main__':
    main()