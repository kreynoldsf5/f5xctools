import asyncio
import aiohttp

async def post(ns, session):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}
    try:
        async with session.get(
            "/api/web/namespaces/{0}/cascade_delete".format(ns), 
            headers=headers, 
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

async def run(NSs):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for ns in NSs:
            task = asyncio.ensure_future(post(ns, session))
            tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses
    return responses

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
task = asyncio.ensure_future(run(url_list))
loop.run_until_complete(task)
result = task.result().result()