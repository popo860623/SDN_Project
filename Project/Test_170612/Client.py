import socket
import time
import datetime
import sys

print 'Argument List:', str(sys.argv)

UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
sock.settimeout(2)



while True:
    TimeNow=datetime.datetime.now()
    sock.sendto(str(datetime.datetime.now()), (UDP_IP, UDP_PORT))
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        #print "received message:", data
        Time = datetime.datetime.strptime(data,"%H:%M:%S.%f")
        DalayObj=datetime.timedelta(hours=Time.hour, minutes=Time.minute, seconds=Time.second, microseconds=Time.microsecond)
        print 'Delay is :'+str(DalayObj.seconds)+' second + '+str(DalayObj.microseconds)+' microseconds'

    except socket.timeout:
        print 'lost connection'

    time.sleep(0.5)
    
