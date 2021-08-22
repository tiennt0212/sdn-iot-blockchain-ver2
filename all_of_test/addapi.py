from os import device_encoding
import requests
from requests.auth import HTTPBasicAuth
import json
import sys

# with open(sys.argv[2]) as data_file:    
# 	json_rule = json.dumps(json.load(data_file))

def add_rule():
	json_rule = '''
	{
    		"flows": [
		{
        		"priority": 7,
        		"isPermanent": true,
        		"treatment": {},
			"deviceId": "of:0000000000000001",
        		"selector": 
			{
            			"criteria": [
					{
                			"type": "IPV4_SRC",
               				"ip":"10.0.0.251/32"
            				},
					{
                			"type": "IPV4_DST",
               				"ip":"10.0.0.252/32"
            				},
            				{
            				"type": "ICMPV4_TYPE",
            				"icmpType": "8"
            				},
            				{
           				"type": "ICMPV4_CODE",
            				"icmpCode": 0
            				}
				]
        			}
        	}]
	}	
	'''

	#POST rules via API "flow", appId=org.onosproject.fwd
	url = 'http://172.17.0.2:8181/onos/v1/flows?appId=org.onosproject.fwd'
	print("Post rule with url: ", url)

	headers = {'Content-Type':'application/json' , 'Accept':'application/json'}

	response = requests.post(url, data=json_rule, auth=('onos', 'rocks'), headers=headers)
	print(response.status_code) #Get Reponse to terminal
	print(response.json())



##main()
add_rule()
