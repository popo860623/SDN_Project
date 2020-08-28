from inform import *
from ResourceProvisioning import *

def BalancePolicy(ServiceID,IP):

	serverlength=len(Get_DB()[ServiceID]['IPs'])
	dstSrcNumber=hash(IP)%serverlength
	ClientServerPair={}
	ClientServerPair[IP]=Get_DB()[ServiceID]['IPs'][dstSrcNumber]
	ResourceProvisioning(ClientServerPair=ClientServerPair,ServiceID=ServiceID)
	
