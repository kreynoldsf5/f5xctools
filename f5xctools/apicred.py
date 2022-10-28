from f5xctools.helpers import findExpiry, RenewError, DelError, FindError
from dateutil.parser import parse

def find_stale(xcsession, staleDays):
    try:
        resp = xcsession.get('/api/web/namespaces/system/api_credentials?report_fields')
        resp.raise_for_status()
        staleCreds = []
        for item in resp.json()['items']:
            expiry = findExpiry(staleDays)
            if parse(item['expiry_timestamp']) < expiry:
                staleCreds.append(item)
        if len(staleCreds):
            return staleCreds
        else:
            return None
    except Exception as e:
        raise FindError(e)

def renew(xcsession, tokenName: str, expiryDays: int=7):
    tokenPayload = {
        "name": tokenName,
        "expiration_days": expiryDays,
    }
    try:
        resp = xcsession.post('/api/web/namespaces/system/renew/api_credentials', json=tokenPayload)
        resp.raise_for_status()
        return
    except Exception as e:
        raise RenewError(e)

def expire(xcsession, tokenName: str):
    tokenPayload = {
        "name": tokenName,
        "expiration_days": 0,
    }
    try:
        resp = xcsession.post('/api/web/namespaces/system/renew/api_credentials', json=tokenPayload)
        resp.raise_for_status()
        return
    except Exception as e:
        raise RenewError(e)

def revoke(xcsession, cred):
    if cred['type'] == 'SITE_GLOBAL_KUBE_CONFIG':
        userPayload = {
            "name": cred['name']
        }
        url = '/api/web/namespaces/system/revoke/global-kubeconfigs'
    else:  
        userPayload = {
            "name": cred['name'],
            "namespace": cred['namespace']
        }
        url = '/api/web/namespaces/system/revoke/api_credentials'
    try:
        resp = xcsession.post(url, json=userPayload)
        resp.raise_for_status()
        return
    except Exception as e:
        raise DelError(e)