from helpers import DelError

from dateutil.parser import parse
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