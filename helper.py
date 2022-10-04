import datetime, logging, sys, csv
from requests import Session
from urllib.parse import urljoin
from dateutil.parser import *

def findExpiry(staleDays: int):
    expiry = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=staleDays)
    return expiry

def writeCSV(data: list, filename: str = 'results.csv'):
    header = ['email', 'first_name', 'last_name', 'domain_owner', 'creation_timestamp', 'last_login_timestamp']
    file = open(filename, 'w', newline ='') 
    with file:   
        writer = csv.DictWriter(file, fieldnames = header) 
        writer.writeheader()
        for row in data:
            writer.writerow(row) 

def getLogger(name: str, level: str):
    log = logging.getLogger(name)
    log.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    FORMAT_STRING = '%(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(FORMAT_STRING)
    handler.setFormatter(formatter)
    log.propagate = False
    log.addHandler(handler)
    return log

class Error(Exception):
    """Base class for other exceptions"""
    pass

class NSerror(Error):
    """Raised when NS operations fail"""
    pass

class IAMerror(Error):
    """Raised when IAM operations fail"""
    pass

class APICREDerror(Error):
    """Raised when IAM operations fail"""
    pass

class F5xcSession(Session):
    def __init__(self, token, prefix_url=None, *args, **kwargs):
        super(F5xcSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.headers.update({'Authorization': "APIToken {0}".format(token)})

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(F5xcSession, self).request(method, url, *args, **kwargs)

    def existIAM(self, email: str) -> bool:
        try:
            resp = self.get('/api/web/custom/namespaces/system/user_roles?namespace=system')
            resp.raise_for_status()
            if next((x for x in resp.json()['items'] if x['email'] == email), None):
                return True
            else:
                return False
        except Exception as e:
            raise IAMerror(e)

    def staleIAMs(self, staleDays):
        try:
            resp = self.get('/api/web/custom/namespaces/system/user_roles')
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

    def staleApiCreds(self, staleDays):
        try:
            resp = self.get('/api/web/namespaces/system/api_credentials')
            resp.raise_for_status()
            staleApiCreds = []
            for item in resp.json()['items']:
                expiry = findExpiry(staleDays)
                if parse(item['expiry_timestamp']) < expiry:
                    staleApiCreds.append(item)
            if len(staleApiCreds):
                return staleApiCreds
            else:
                return None
        except Exception as e:
            raise APICREDerror(e)

    def deleteNS(self, nsName):
        nsPayload = {
            "name": nsName
        }
        try:
            resp = self.post(
                "/api/web/namespaces/{0}/cascade_delete".format(nsName),
                json=nsPayload
            )
            resp.raise_for_status()
            return
        except Exception as e:
            raise NSerror(e)

    def deleteIAM(self, email):
        userPayload = {
            "email": email.lower(),
            "namespace": "system"
        }
        try:
            resp = self.post(
                '/api/web/custom/namespaces/system/users/cascade_delete',
                json=userPayload
            )
            resp.raise_for_status()
            return
        except Exception as e:
            raise IAMerror(e)

    def deleteApiCred(self, name, namespace):
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
            raise APICREDerror(e)

