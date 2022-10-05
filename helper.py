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

class SITESerror(Error):
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
                #Let's keep our objects smaller w/ only crucial props
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

    def staleSites(self, staleDays):
        try:
            resp = self.get('/api/config/namespaces/system/sites?report_fields')
            resp.raise_for_status()
            staleSites = []
            for item in resp.json()['items']:
                if item['get_spec']['site_type'] != 'CUSTOMER_EDGE':
                    continue
                if item['get_spec']['site_state'] == 'ONLINE':
                    continue
                expiry = findExpiry(staleDays)
                this = {
                    'name': item['name'],
                    'namespace': item['namespace'],
                    'site_type': item['get_spec']['site_type'],
                    'site_state': item['get_spec']['site_state'],
                    'creation_timestamp': item['system_metadata']['creation_timestamp'],
                    'modification_timestamp': item['system_metadata']['modification_timestamp'],
                    'provider': item['labels'].get('ves.io/provider', 'UNKNOWN')
                }
                if item['owner_view']:
                    this['kind']=item['owner_view']['kind']
                if this['modification_timestamp']:
                    if parse(this['modification_timestamp']) < expiry:
                        staleSites.append(this)
                else:
                    if parse(this['creation_timestamp']) < expiry:
                        staleSites.append(this)
            if len(staleSites):
                return staleSites
            else:
                return None
        except Exception as e:
            raise SITESerror(e)

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

    def deleteSite(self, site):
        kindDict = {
            'aws_vpc_site': '/api/config/namespaces/{}/aws_vpc_sites/'.format(site['namespace']),
            'aws_tgw_site': '/api/config/namespaces/{}/aws_tgw_sites/'.format(site['namespace']),
            'azure_vnet_site': '/api/config/namespaces/{}/azure_vnet_sites/'.format(site['namespace']),
            'voltstack_site': '/api/config/namespaces/{}/voltstack_sites/'.format(site['namespace'])
        }
        try:
            if 'kind' in site:
                if site['kind'] in kindDict.keys():
                    resp = self.delete(kindDict[site['kind']]+site['name'])
                    resp.raise_for_status()
                    return
                else:
                    print('Skipping removal for {0} -- {1} kind not yet implemented'.format(site['name'], site['kind']))
                    return
            else:          
                userPayload = {
                    "name": site['name'],
                    'namespace': site['namespace'],
                    'state': 7
                }
                url='/api/register/namespaces/system/site/{}/state'.format(site['name'])
                resp = self.post(
                    url,
                    json=userPayload
                )
                resp.raise_for_status()
                return
        except Exception as e:
            raise APICREDerror(e)

