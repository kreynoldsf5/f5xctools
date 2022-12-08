#!/usr/bin/env python3
import argparse, sys
from f5xctools import user_group, xcsession, iam

def main():
    ap = argparse.ArgumentParser(
        prog='f5xc_user_group',
        usage='%(prog)s [options]',
        description='add a user_group to existing users'
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
        '--user_group',
        help='days since API cred expired',
        type=str,
        default='sales-tenant-default-group',
        required=False
    )
    args = ap.parse_args()
    try:
        session = xcsession(args.token, args.tenant)
        users = iam.find_all(session)
        reg_users = []
        for user in users:
            if {'namespace': 'system', 'role': 'ves-io-monitor-role'} in user['namespace_roles']:
                continue
            else:
                reg_users.append(user)
        #Add users to our group
        user_names = []
        for reg in reg_users:
            user_names.append(reg['email'])
        print(len(user_names))
        user_group.updateUsers(session, args.user_group, user_names, 300)
        #print(user_names)
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()