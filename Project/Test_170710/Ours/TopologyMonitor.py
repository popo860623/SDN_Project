from inform import *
import requests
import json

def TopologyMonitor():
	url = 'http://127.0.0.1:5000/distance'
	response = requests.get(url)
	#print 'Topology Response:'
	json_data = json.loads(response.text)
	Set_distance(json_data)
	#print Get_distance()

