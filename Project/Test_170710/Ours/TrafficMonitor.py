from inform import *
from PolicyChecker import *
import requests
import json
## Flow Monitor Module
def TrafficMonitor():
	for ServiceID in Get_DB():
		IP=Get_DB()[ServiceID]['MainIP']
		url = 'http://127.0.0.1:5000/get_flow_state'
		data={}
		data['hostip']=IP
		payload=json.dumps(data)
		#print payload
		response = requests.post(url,data=payload)
		print "****GetFlowState_Response**** = "+str(response)
		json_data = json.loads(response.text)
		if len(json_data.items())==0:
			continue
		## Flow Filter Module
		for flow in json_data[u'OFPFlowStatsReply'][u'body']:
			IPmatch =False
			Portmatch=False
			for matchfield in flow[u'OFPFlowStats'][u'match'][u'OFPMatch'][u'oxm_fields']:
				#print matchfield
				if matchfield[u'OXMTlv'][u'field']==u'ipv4_dst':
					#print 'ipv4_dst = '+ matchfield[u'OXMTlv'][u'value']
					if matchfield[u'OXMTlv'][u'value']==IP:
						IPmatch =True
				if matchfield[u'OXMTlv'][u'field']==u'udp_dst':
					#print 'ipv4_dst = '+ matchfield[u'OXMTlv'][u'value']
					if matchfield[u'OXMTlv'][u'value']==Get_DB()[ServiceID]["Port"]:
						Portmatch =True
			if IPmatch == True and Portmatch ==True:
				for matchfield in flow[u'OFPFlowStats'][u'match'][u'OFPMatch'][u'oxm_fields']:
					if matchfield[u'OXMTlv'][u'field']==u'ipv4_src':
						PolicyChecker(IP=matchfield[u'OXMTlv'][u'value'],ServiceID=ServiceID)
								
								
