from f5xctools.helpers import CreateError
import json

def create(xcsession, name: str, api_groups: list = None, description: str = "", namespace: str = 'system'):
    try:
        payload = {
            "api_groups": api_groups,
            "metadata": {
                "name": name,
                "namespace": namespace
            }
        }
        resp = xcsession.post(
            '/api/web/custom/namespaces/{0}/roles'.format(namespace),
            json=payload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise CreateError(e)

def list(xcsession):
    try:
        resp = xcsession.get(
            '/api/web/custom/namespaces/system/roles'
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise CreateError(e)