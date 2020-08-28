from inform import *
from munkres import Munkres, print_matrix
from ResourceProvisioning import *

def BalancePolicy(ServiceID):
	print 'ServiceID = '+ServiceID

	clientlength=len(Get_DB()[ServiceID]['srcIP'])
	serverlength=len(Get_DB()[ServiceID]['IPs'])
	print 'clientlength = '+str(clientlength)
	print 'serverlength = '+str(serverlength)
	#revised column size
	w=((clientlength//serverlength)+int(bool(clientlength%serverlength)))*serverlength
	matrix=[]
	for i in range(0,clientlength):
		matrix.append([0]*w)
	for i in range(0,len(matrix)):
		for j in range(0,len(matrix[i])):
			matrix[i][j]=Get_distance()[Get_DB()[ServiceID]['srcIP'][i]][Get_DB()[ServiceID]['IPs'][j%serverlength]]
	print 'matrix = '+str(matrix)
	# Hungarian Algorithm
	m = Munkres()
	indexes = m.compute(matrix)
	ClientServerPair={}
	for clientindex, serverindex in indexes:
		ClientServerPair[Get_DB()[ServiceID]['srcIP'][clientindex]]=Get_DB()[ServiceID]['IPs'][serverindex%serverlength]
	print ClientServerPair
	ResourceProvisioning(ClientServerPair=ClientServerPair,ServiceID=ServiceID)
	
