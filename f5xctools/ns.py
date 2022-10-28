from f5xctools.helpers import DelError
from dateutil.parser import parse

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

"""
Delete NSs async to save time
"""