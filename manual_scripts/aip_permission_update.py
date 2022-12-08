#!/usr/bin/env python3
import argparse, sys, time
from f5xctools import xcsession, iam

def findUserNS(email: str) -> str:
    userNS = ""
    if "#EXT#@" in email:
        userNS = email.split(
            '#EXT#@')[0].replace('.', '-').replace('_', '-').lower()
    else:
        userNS = email.split('@')[0].replace('.', '-').lower()
    return userNS

def updateNSroles(iam: dict) -> dict:
    ns_roles = []
    userNS = findUserNS(iam['email'])
    for role in iam['namespace_roles']:
        if role['namespace'] == userNS:
            role['role'] ='ves-io-power-developer-role'
        ns_roles.append(role)
    iam['namespace_roles'].append({
        'namespace': userNS,
        'role': 'f5xc-aip-write'
    })
    return iam

def updateIam(iam: dict):
    try:
        iam.update(iam)
        time.sleep(.2)
        print("updated user {}".format(iam['email']))
    except Exception as e:
        print(e)
    return

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
    args = ap.parse_args()
    try:
        session = xcsession(args.token, args.tenant)
        users = iam.find_all(session)
        print('found {} non-owner users.'.format(len(users)))
        update_users = []
        for user in users:
            if {'namespace': 'system', 'role': 'ves-io-monitor-role'} in user['namespace_roles']:
                continue
            else:
                if {'namespace': findUserNS(user['email']), 'role': 'ves-io-admin-role'} in user['namespace_roles']:
                    update_users.append(user)
        print('found {} users to update.'.format(len(update_users)))
        for iam in update_users:
            try:
                print(iam)
                newIam = updateNSroles(iam)
                print(newIam)
                #updateIam(newIam)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()