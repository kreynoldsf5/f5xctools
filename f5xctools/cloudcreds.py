from .helpers import findExpiry, FindError, DelError
from dateutil.parser import parse

class cloudcred():
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