from f5xctools.helpers import DelError
from dateutil.parser import parse
import asyncio
import aiohttp
import json

def delete(xcsession, nsName):
    nsPayload = {
        "name": nsName
    }
    try:
        resp = xcsession.post(
            "/api/web/namespaces/{0}/cascade_delete".format(nsName),
            json=nsPayload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise DelError(e)

async def _post(ns, session):
    try:
        async with session.post(
            "/api/web/namespaces/{0}/cascade_delete".format(ns),
            data = json.dumps({'name': ns}),
            ssl = True, 
            timeout = aiohttp.ClientTimeout(
                total=None, 
                sock_connect = 10, 
                sock_read = 10
            )
        ) as response:
            content = await response.read()
            return (ns, 'OK', content)
    except Exception as e:
        print(e)
        return (ns, 'ERROR', str(e))

async def _run(xcsession, NSs):
    tasks = []
    async with aiohttp.ClientSession(base_url=xcsession.prefix_url, headers=xcsession.headers) as session:
        for ns in NSs:
            task = asyncio.ensure_future(_post(ns, session))
            tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses
    return responses

def bulk_delete(xcsession, NSs):
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    task = asyncio.ensure_future(_run(xcsession, NSs))
    loop.run_until_complete(task)
    return(task.result().result())

"""
Delete NSs async to save time
"""