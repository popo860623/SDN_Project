import json
import requests
import time

while True :
	url = 'http://127.0.0.1:8080/stats/flow/1'
	response = requests.get(url)
	json_data = json.loads(response.text)
	#print json_data
	print len(json_data[u'1'])
	time.sleep(1)
