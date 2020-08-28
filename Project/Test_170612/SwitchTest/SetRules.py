import json
import requests
import time

def mac(getvar):
	macs=getvar.split('.')
	ma=[]
	for i in range(0, 6):
		maca=macs[i] 
		if int(maca) < 16 :
			a = '0'+hex(int(maca)).upper()[2:]
		else:
			a = hex(int(maca)).upper()[2:]
		ma.append(a)
	return ma[0]  + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]
a=5
for tableid in range(0,50) :
	p=3
	for i in range(0,100) :
		foobar=str((a>>40)&255)+'.'+str((a>>32)&255)+'.'+str((a>>24)&255)+'.'+str((a>>16)&255)+'.'+str((a>>8)&255)+'.'+str(a&255)
		a=(a+1)&((1<<48)-1)
		url = 'http://127.0.0.1:8080/stats/flowentry/add'
		rule={}
		rule['dpid']=1
		rule['cookie']=1
		rule['cookie_mask']=1
		rule['table_id']=tableid
		rule['idle_timeout']=0
		rule['hard_timeout']=0
		#rule['priority']=3
		rule['priority']=p
		p+=1
		rule['flags']=1
		rule['match']={}
		rule['match']['in_port']=1
		rule['match']['dl_dst']=mac(foobar)
		rule['actions']=[]
		rule['actions'].append({})
		rule['actions'][0]['type']='OUTPUT'
		rule['actions'][0]['port']=0xfffffffd
		response = requests.post(url,data=json.dumps(rule))
		print response
#print 'p = '+str(p)
