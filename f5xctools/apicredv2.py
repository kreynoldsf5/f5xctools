from .helpers import findExpiry, DelError, RenewError
from dateutil.parser import parse
from requests import Session
from urllib.parse import urljoin

class apicredv2(Session):
    def __init__(self, token, prefix_url=None, *args, **kwargs):
        super(apicredv2, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.headers.update({'Authorization': "APIToken {0}".format(token)})

    def req(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(apicredv2, self).request(method, url, *args, **kwargs)

    def renew(self, tokenName: str, expiryDays: int=7):
        tokenPayload = {
            "name": tokenName,
            "expiration_days": expiryDays,
        }
        try:
            resp = self.req.post('/api/web/namespaces/system/renew/api_credentials', json=tokenPayload)
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
            resp = self.req.post('/api/web/namespaces/system/renew/api_credentials', json=tokenPayload)
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
            resp = self.req.post(
                '/api/web/namespaces/system/revoke/api_credentials',
                json=userPayload
            )
            resp.raise_for_status()
            return
        except Exception as e:
            raise DelError(e)