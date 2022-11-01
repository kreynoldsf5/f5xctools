import requests
from urllib.parse import urljoin
from f5xctools.helpers import SessionError

class xcsession(requests.Session):
    def __init__(self, token, prefix_url=None, *args, **kwargs):
        super(xcsession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.headers.update({'Authorization': "APIToken {0}".format(token)})
        self.valid(token, prefix_url)

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(xcsession, self).request(method, url, *args, **kwargs)

    def valid(self, token, prefix_url) -> bool:
        try:
            headers = {'Authorization': "APIToken {0}".format(token)}
            resp = requests.get('{}/api/web/custom/namespaces/system/whoami?namespace=system'.format(prefix_url), headers=headers)
            resp.raise_for_status()
            return
        except Exception as e:
            raise SessionError(e)

"""
use aiohttp.ClientSession for all requests, even if in a synchronous way?
"""
