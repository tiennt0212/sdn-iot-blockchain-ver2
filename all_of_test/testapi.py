import requests
import json
url='http://172.17.0.2:8181/onos/ui'
res=requests.get(url).headers.json()
print(res)
