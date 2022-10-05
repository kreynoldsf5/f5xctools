import datetime
from dateutil.parser import *

def findExpiry(staleDays: int):
    expiry = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=staleDays)
    return expiry

class Error(Exception):
    """Base class for other exceptions"""
    pass

class IAMerror(Error):
    """Raised when IAM operations fail"""
    pass

class cleanIAM():
    def __init__(self, xc_session):
        self.xcsession = xc_session

    def exist(self, email: str) -> bool:
        try:
            resp = self.xcsession.get('/api/web/custom/namespaces/system/user_roles?namespace=system')
            resp.raise_for_status()
            if next((x for x in resp.json()['items'] if x['email'] == email), None):
                return True
            else:
                return False
        except Exception as e:
            raise IAMerror(e)

    def stale(self, staleDays):
        try:
            resp = self.xcsession.get('/api/web/custom/namespaces/system/user_roles')
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
            raise IAMerror(e)

    def deleteIAM(self, email, namespace='system'):
        userPayload = {
            "email": email.lower(),
            "namespace": namespace
        }
        try:
            resp = self.xcsession.post(
                '/api/web/custom/namespaces/system/users/cascade_delete',
                json=userPayload
            )
            resp.raise_for_status()
            return
        except Exception as e:
            raise IAMerror(e)