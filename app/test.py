import json

import requests


def get_requiered_token():
    headers = requests.head(url=f"{registryBase}/v2/{image}/manifests/{digest}").headers
    auth_info = headers['Www-Authenticate']
    auth_info = '{"' + auth_info.replace(" ", "") + '}'
    auth_info = auth_info.replace('="', '":"')
    auth_info = auth_info.replace(',', ',"')
    auth_info = json.loads(auth_info)
    r = requests.get(url=auth_info['Bearerrealm'],
                     params={
                         "service": auth_info['service'],
                         "scope": auth_info['scope']
                     })
    return r.json()['token']


#registryBase = 'https://registry-1.docker.io'
#authBase = 'https://auth.docker.io'
#authService = 'registry.docker.io'
#image = 'library/hello-world'
#digest = 'latest'
registryBase = 'https://registry-1.docker.io'
authBase = 'https://auth.docker.io'
authService = 'registry.docker.io'
image = 'library/hello-world'
digest = 'latest'

token = get_requiered_token()

header = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.docker.distribution.manifest.v2+json"
}
url = f"{registryBase}/v2/{image}/manifests/{digest}"
r = requests.get(url=url, headers=header)
manifest = r.json()
