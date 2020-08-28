from inform import *
from EventHandler import *
def PolicyChecker(IP,ServiceID):
	# Add Clients List
	if IP not in Get_DB()[ServiceID]['srcIP']:
		if Get_distance() == {}:
			return
		Get_DB()[ServiceID]['srcIP'].append(IP)
		print Get_DB()
		NewUserEvent(ServiceID)

