from f5xctools.helpers import findExpiry, RenewError, DelError
from dateutil.parser import parse

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

def revoke(xcsession, name, namespace='system'):
    userPayload = {
        "name": name,
        "namespace": namespace
    }
    try:
        resp = xcsession.post(
            '/api/web/namespaces/system/revoke/api_credentials',
            json=userPayload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise DelError(e)