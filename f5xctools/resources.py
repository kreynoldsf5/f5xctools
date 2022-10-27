import datetime
from requests import Session
from urllib.parse import urljoin
from dateutil.parser import *

def findExpiry(staleDays: int):
    expiry = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=staleDays)
    return expiry

class Error(Exception):
    """Base class for other exceptions"""
    pass

class FindError(Error):
    """Raised when IAM operations fail"""
    pass

class DelError(Error):
    """Raised when IAM operations fail"""
    pass

class RenewError(Error):
    """Raised when IAM operations fail"""
    pass

class iam():
    def __init__(self, xc_session):
        self.xcsession = xc_session

    def exists(self, email: str) -> bool:
        try:
            resp = self.xcsession.get('/api/web/custom/namespaces/system/user_roles?namespace=system')
            resp.raise_for_status()
            if next((x for x in resp.json()['items'] if x['email'] == email), None):
                return True
            else:
                return False
        except Exception as e:
            raise FindError(e)

    def find_stale(self, staleDays):
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
            raise FindError(e)

    def delete(self, email, namespace='system'):
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
            raise DelError(e)

class cloud_cred():
    def __init__(self, xc_session):
        self.xcsession = xc_session

    def find_stale(self, staleDays):
        specSitesDict = [
            {'url': '/api/config/namespaces/system/aws_vpc_sites?report_fields', 'cred': 'aws_cred'},
            {'url': '/api/config/namespaces/system/aws_tgw_sites?report_fields', 'cred': 'aws_cred'},
            {'url': '/api/config/namespaces/system/azure_vnet_sites?report_fields', 'cred': 'azure_cred'},
            {'url': '/api/config/namespaces/system/gcp_vpc_sites?report_fields', 'cred': 'cloud_credentials'},
        ]
        try:
            usedCreds = []
            for kind in specSitesDict:
                resp = self.get(kind['url'])
                resp.raise_for_status()
                for item in resp.json()['items']:
                    if kind['cred'] in item['get_spec']:
                        usedCreds.append(item['get_spec'][kind['cred']])
            usedCreds = [i for n, i in enumerate(usedCreds) if i not in usedCreds[n + 1:]]
            #Find all cloud creds
            creds = []
            resp = self.get('/api/config/namespaces/system/cloud_credentialss?report_fields')
            resp.raise_for_status()
            for item in resp.json()['items']:
                this = {
                    'tenant': item['tenant'],
                    'namespace': item['namespace'],
                    'name': item['name'],
                    'creation_timestamp': item['system_metadata']['creation_timestamp']
                }
                creds.append(this)
            #Eleminate used creds from all creds
            for cred in creds.copy():
                for used in usedCreds:
                    if cred.get('name') == used['name']:
                        creds.remove(cred)
            #Find the unused creds that are 'stale'
            staleCreds = []
            expiry = findExpiry(staleDays)
            for cred in creds:
                if parse(cred['creation_timestamp']) < expiry:
                    staleCreds.append(cred) 
            if len(staleCreds):
                return staleCreds
            else:
                return None
        except Exception as e:
            raise FindError(e)

    def delete(self, cred):
        #Docs are wrong: https://docs.cloud.f5.com/docs/api/cloud-credentials#operation/ves.io.schema.cloud_credentials.API.Delete
        #userPayload = {
        #    'name': cred['name'],
        #    'namespace': cred['namespace'],
        #    'fail_if_referred': True
        #}
        try:
            resp = self.delete(
                '/api/config/namespaces/{0}/cloud_credentialss/{1}'.format(cred['namespace'], cred['name']),
            )
            resp.raise_for_status()
            return
        except Exception as e:
            raise DelError(e)

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

class site():
    def __init__(self, xc_session):
        self.xcsession = xc_session

    def findStale(self, staleDays):
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
            raise FindError(e)

    def delete(self, site):
        kindDict = {
            'aws_vpc_site': '/api/config/namespaces/{}/aws_vpc_sites/'.format(site['namespace']),
            'aws_tgw_site': '/api/config/namespaces/{}/aws_tgw_sites/'.format(site['namespace']),
            'azure_vnet_site': '/api/config/namespaces/{}/azure_vnet_sites/'.format(site['namespace']),
            'gcp_vpc_site': '/api/config/namespaces/{}/gcp_vpc_sites/'.format(site['namespace']),
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
            raise DelError(e)

class ns():
    def __init__(self, xc_session):
        self.xcsession = xc_session

    def delete(self, nsName):
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
            raise DelError(e)