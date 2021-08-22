import json
  
# Opening JSON file
f = open('data.json',)
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
print (data['deviceId'])
#for i in data['info']:
    #print(i)
  
# Closing file
f.close()
