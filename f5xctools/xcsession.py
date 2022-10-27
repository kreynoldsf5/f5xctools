from requests import Session
from urllib.parse import urljoin
from f5xctools.helpers import SessionError

class xcsession(Session):
    def __init__(self, token, prefix_url=None, *args, **kwargs):
        super(xcsession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.headers.update({'Authorization': "APIToken {0}".format(token)})
        self.valid()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(xcsession, self).request(method, url, *args, **kwargs)

    def valid(self) -> bool:
        try:
            resp = self.request.get('/api/web/custom/namespaces/system/whoaminamespace=system')
            resp.raise_for_status()
            return
        except Exception as e:
            raise SessionError(e)
