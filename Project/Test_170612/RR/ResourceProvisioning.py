from inform import *
import json
import requests
def ResourceProvisioning(ClientServerPair,ServiceID):
	url = 'http://127.0.0.1:5000/alltuple'
	response = requests.get(url)
	json_data = json.loads(response.text)
	for client in ClientServerPair:
		for rule in json_data:
			if rule[u'clientIP']==client and rule[u'servicePort']==Get_DB()[ServiceID]['Port']:
				if rule[u'NewserverIP']==ClientServerPair[client]:
					print client + ' not change'
				else:
					url = 'http://127.0.0.1:5000/del'
					payloadOld=json.dumps(rule)
					response = requests.post(url,data=payloadOld)
					print 'del '+str(payloadOld)
				break

		server = Get_DB()[ServiceID]['MainIP']
		url = 'http://127.0.0.1:5000/set'
		rule={}
		rule['servicePort']=Get_DB()[ServiceID]['Port']
		rule['MainserverIP']=server
		rule['NewserverIP']=ClientServerPair[client]
		rule['clientIP']=client
		payloadNew=json.dumps(rule)
		response = requests.post(url,data=payloadNew)
		print 'add '+str(payloadNew)
					
