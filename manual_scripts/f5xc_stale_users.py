#!/usr/bin/env python3
import argparse, json, sys
from manual_scripts.helper import F5xcSession, getLogger, writeCSV

def main():
    ap = argparse.ArgumentParser(
        prog='f5xc_stale_users',
        usage='%(prog)s [options]',
        description='find and, optionally, remove stale f5xc users from a tenant'
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
        help='days since login',
        type=int,
        required=True
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
        help='remove stale users',
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
        stale = xcSession.staleIAMs(args.stale_days)
        if stale:
            logger.info('found {} stale IAMs'.format(len(stale)))
        else:
            logger.info('no stale IAMs found. Exiting.')
            sys.exit(0)
    except Exception as e:
        logger.debug(e)
        logger.info('Error creation XC session and retrieving users. Exiting.')
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
            for user in stale:
                if user['domain_owner']:
                    logger.info('User {} is tenant owner. Skipping.'.format(user['email']))
                    continue
                else:
                    try:
                        xcSession.deleteIAM(user['email'])
                        logger.info('User {} removed.'.format(user['email']))
                    except Exception as e:
                        logger.info('Error removing stale user {0}: {1}'.format(user['email'], e))
                        continue
    except Exception as e:
        logger.debug(e)
        logger.info('Error removing stale users. Exiting.')
        sys.exit(1)
    logger.info('Done. Exiting.')
    sys.exit(0)

if __name__ == '__main__':
    main()