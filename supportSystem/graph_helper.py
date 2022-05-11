import requests

graph_url = 'https://graph.microsoft.com/v1.0'

def get_user(token):
    user = requests.get('{0}/me'.format(graph_url),
    headers={'Authorization': 'Bearer {0}'.format(token)},
    params={})
    return user.json()

def get_group(token):
    groups = requests.get('{0}/me/memberOf'.format(graph_url),
                        headers={
                            'Authorization': 'Bearer {0}'.format(token),
                            'ConsistencyLevel':'eventual'
                        },
                        params={
                            })
    return groups.json()