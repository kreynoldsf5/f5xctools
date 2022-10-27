from requests import Session
from urllib.parse import urljoin

class session(Session):
    def __init__(self, token, prefix_url=None, *args, **kwargs):
        super(session, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.headers.update({'Authorization': "APIToken {0}".format(token)})

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(session, self).request(method, url, *args, **kwargs)