import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint

data = {
    'command': 'uploader',
    'parameters': {
        'name': 'uploader_add',
        'description': 'Home Server',
        'provider': 'home',
        'format': 'RFA',
        'hostname': '###',
        'port': 44202,
        'url': '/data',
        'uploadSize': 0,
        'uploadPeriod': 0,
        'protocol': 'http',
        'x-header1': '',
        'x-header2': '',
        'x-header3': '',
    },
}


result = requests.post('https://api.rainforestcloud.com/rest/device/####/command',
              json=data,
              headers={'authorization': 'Bearer #####'})

pprint(result.request.headers)
print(result.headers)
print(result.status_code)
print(result.text)
