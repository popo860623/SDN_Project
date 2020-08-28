from flask import Flask, url_for
from flask import request
from flask import Response
from flask import jsonify
from flask import json
from inform import *
from TrafficMonitor import *
from TopologyMonitor import *
import thread
import time


app = Flask(__name__)

def flaskThread():
	app.run(port=5010)
flood=False
@app.route('/')
def api_root():
	return 'Welcome\n'

@app.route('/service', methods=['POST'])
def api_service():
	data = request.get_data()
	jsondata = json.loads(data)
	ServiceID = jsondata['ServiceID']
	MainIP = jsondata['MainIP']
	IPs = jsondata['IPs']
	Port = jsondata['Port']
	print MainIP
	print IPs
	print Port
	Get_DB()[ServiceID]={}
	Get_DB()[ServiceID]['MainIP']=MainIP
	Get_DB()[ServiceID]['IPs']=IPs
	Get_DB()[ServiceID]['Port']=Port
	Get_DB()[ServiceID]['srcIP']=[]
	return 'success'
@app.route('/DB', methods=['GET'])
def api_DB():
	data=json.dumps(Get_DB())
	return data

if __name__ == '__main__':
	thread.start_new_thread(flaskThread,())
	while True:
		#print '1'
		TrafficMonitor()
		TopologyMonitor()
		time.sleep(2)

