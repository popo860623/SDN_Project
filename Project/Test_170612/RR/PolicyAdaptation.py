from inform import *
from ResourceProvisioning import *

def BalancePolicy(ServiceID,IP):

	serverlength=len(Get_DB()[ServiceID]['IPs'])
	counterNext=(Get_DB()[ServiceID]['counter']+1)%serverlength
	ClientServerPair={}
	ClientServerPair[IP]=Get_DB()[ServiceID]['IPs'][counterNext]
	ResourceProvisioning(ClientServerPair=ClientServerPair,ServiceID=ServiceID)
	Get_DB()[ServiceID]['counter']=counterNext
	
