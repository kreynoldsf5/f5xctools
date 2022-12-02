from f5xctools.helpers import CreateError, FindError, DelError, ReplaceError, findExpiry
from dateutil.parser import parse
import asyncio
import aiohttp
import json

def create(xcsession, firstName: str, lastName: str, email: str, nsRoles: str = None):
    try:
        pass
        payload = {
            'email': email,
            'first_name': firstName,
            'last_name': lastName,
            'domain_owner': False,
            'namespace_roles': nsRoles
        }
        resp = xcsession.post(
            '/api/web/custom/namespaces/system/users',
            json=payload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise CreateError(e)

def exists(xcsession, email: str) -> bool:
    try:
        resp = xcsession.get('/api/web/custom/namespaces/system/user_roles?namespace=system')
        resp.raise_for_status()
        if next((x for x in resp.json()['items'] if x['email'] == email), None):
            return True
        else:
            return False
    except Exception as e:
        raise FindError(e)

def find_stale(xcsession, staleDays):
    try:
        resp = xcsession.get('/api/web/custom/namespaces/system/user_roles')
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

def find_all(xcsession, excludeDomainOwners: bool = True):
    try:
        resp = xcsession.get('/api/web/custom/namespaces/system/user_roles')
        resp.raise_for_status()
        IAMs = []
        for item in resp.json()['items']:
            this = {
                    'email': item['email'],
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                    'domain_owner': item['domain_owner'],
                    'namespace_roles': item['namespace_roles']
                }
            if excludeDomainOwners:
                if item['domain_owner']: 
                    continue
                IAMs.append(this)
            else:
                IAMs.append(this)
        if len(IAMs):
            return IAMs
        else:
            return None
    except Exception as e:
        raise FindError(e)

def delete(xcsession, iam, namespace='system'):
    userPayload = {
        "email": iam['email'],
        "namespace": namespace
    }
    try:
        resp = xcsession.post(
            '/api/web/custom/namespaces/system/users/cascade_delete',
            json=userPayload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise DelError(e)



"""
TBD
Handle domain owners
add bulk create and bulk delete methods
"""

"""
Below for bulk user deletion
"""
async def _post(session, email: str, namespace='system'):
    try:
        async with session.post(
            '/api/web/custom/namespaces/system/users/cascade_delete',
            data = json.dumps({'email': email, 'namespace': namespace}),
            ssl = True, 
            timeout = aiohttp.ClientTimeout(
                total=None, 
                sock_connect = 10, 
                sock_read = 45
            )
        ) as response:
            async with response:
                assert (response.status == 200),"status: {}".format(response.status)
            return({'user': email, 'result': 'OK', 'message': response.status})
    except Exception as e:
        return({'user': email, 'result': 'ERROR', 'message': str(e)})

#Can we pass in a function here? That was we can reuse this with any bulk action.
async def _run(xcsession, users):
    tasks = []
    async with aiohttp.ClientSession(base_url=xcsession.prefix_url, headers=xcsession.headers) as session:
        for user in users:
            task = asyncio.ensure_future(_post(session, user))
            tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses
    return responses

def bulk_delete(xcsession, users):
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    task = asyncio.ensure_future(_run(xcsession, users))
    loop.run_until_complete(task)
    return(task.result().result())