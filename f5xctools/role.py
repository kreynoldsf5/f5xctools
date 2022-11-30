from f5xctools.helpers import CreateError

def create(xcsession, name: str, api_groups: list = None, namespace: str = 'system'):
    try:
        payload = {
            'metadata': {
                'name': name,
                'namespaces': namespace,
                'spec': {},
                'api_groups': api_groups
            }
        }
        resp = xcsession.post(
            '/api/web/custom/namespaces/{}/roles'.format(namespace),
            json=payload
        )
        resp.raise_for_status()
        return
    except Exception as e:
        raise CreateError(e)