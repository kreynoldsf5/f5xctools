from f5xctools.helpers import CreateError, findExpiry, FindError, DelError
from dateutil.parser import parse

def create(xcsession, firstName: str, lastName: str, email: str, nsRoles: str = None):
    try:
        pass
        payload = {
            'email': email,
            'first_name': firstName,
            'last_name': lastName,
            'domain_owner': False,
            'namespace_roles': nsRoles
        }
        resp = xcsession.post(
            '/api/web/custom/namespaces/system/users',
            json=payload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise CreateError(e)

def exists(xcsession, email: str) -> bool:
    try:
        resp = xcsession.get('/api/web/custom/namespaces/system/user_roles?namespace=system')
        resp.raise_for_status()
        if next((x for x in resp.json()['items'] if x['email'] == email), None):
            return True
        else:
            return False
    except Exception as e:
        raise FindError(e)

def find_stale(xcsession, staleDays):
    try:
        resp = xcsession.get('/api/web/custom/namespaces/system/user_roles')
        resp.raise_for_status()
        staleIAMs = []
        for item in resp.json()['items']:
            expiry = findExpiry(staleDays)
            this = {
                    'email': item['email'],
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                    'domain_owner': item['domain_owner'],
                    'creation_timestamp': item['creation_timestamp'],
                    'last_login_timestamp': item['last_login_timestamp']
                }
            if this['last_login_timestamp']:
                if parse(this['last_login_timestamp']) < expiry:
                    staleIAMs.append(this)
            else:
                if parse(this['creation_timestamp']) < expiry:
                    staleIAMs.append(this)
        if len(staleIAMs):
            return staleIAMs
        else:
            return None
    except Exception as e:
        raise FindError(e)

def delete(xcsession, iam, namespace='system'):
    userPayload = {
        "email": iam['email'],
        "namespace": namespace
    }
    try:
        resp = xcsession.post(
            '/api/web/custom/namespaces/system/users/cascade_delete',
            json=userPayload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise DelError(e)

"""
TBD
Handle domain owners
add bulk create and bulk delete methods
"""