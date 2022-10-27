from f5xctools.helpers import findExpiry, FindError, DelError
from dateutil.parser import parse

def findStale(xcsession, staleDays):
    try:
        resp = xcsession.get('/api/config/namespaces/system/sites?report_fields')
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

def delete(xcsession, site):
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
                resp = xcsession.delete(kindDict[site['kind']]+site['name'])
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