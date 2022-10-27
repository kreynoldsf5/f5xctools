from helpers import findExpiry, FindError, DelError, RenewError
from dateutil.parser import parse

class api_cred():
    def __init__(self, xc_session):
        self.xcsession = xc_session

    def renew(self, tokenName: str, expiryDays: int=7):
        tokenPayload = {
            "name": tokenName,
            "expiration_days": expiryDays,
        }
        try:
            resp = self.post('/api/web/namespaces/system/renew/api_credentials', json=tokenPayload)
            resp.raise_for_status()
            return
        except Exception as e:
            raise RenewError(e)

    def expire(self, tokenName: str):
        tokenPayload = {
            "name": tokenName,
            "expiration_days": 0,
        }
        try:
            resp = self.post('/api/web/namespaces/system/renew/api_credentials', json=tokenPayload)
            resp.raise_for_status()
            return
        except Exception as e:
            raise RenewError(e)

    def revoke(self, name, namespace='system'):
        userPayload = {
            "name": name,
            "namespace": namespace
        }
        try:
            resp = self.post(
                '/api/web/namespaces/system/revoke/api_credentials',
                json=userPayload
            )
            resp.raise_for_status()
            return
        except Exception as e:
            raise DelError(e)