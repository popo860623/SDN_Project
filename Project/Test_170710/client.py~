import socket
import time
import datetime
import sys

print 'Argument List:', str(sys.argv)

UDP_IP = sys.argv[2]
UDP_PORT = int(sys.argv[3])

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
sock.settimeout(2)

with open(sys.argv[1], "w") as record:
            record.write('')


while True:
    TimeNow=datetime.datetime.now()
    sock.sendto(str(datetime.datetime.now()), (UDP_IP, UDP_PORT))
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        #print "received message:", data
        Time = datetime.datetime.strptime(data,"%H:%M:%S.%f")
        DalayObj=datetime.timedelta(hours=Time.hour, minutes=Time.minute, seconds=Time.second, microseconds=Time.microsecond)
        #print 'Delay is :'+str(DalayObj.seconds)+' second + '+str(DalayObj.microseconds)+' microseconds'
        with open(sys.argv[1], "a") as record:
            record.write(str(TimeNow.hour)+','
                +str(TimeNow.minute)+','
                +str(TimeNow.second)+','
                +'{:06d}'.format(TimeNow.microsecond)+',\t'
                +str(DalayObj.seconds)+','
                +str(DalayObj.microseconds)+'\n')
    except socket.timeout:
        print 'lost connection'
        with open(sys.argv[1], "a") as record:
            record.write(str(TimeNow.hour)+','
                +str(TimeNow.minute)+','
                +str(TimeNow.second)+','
                +str(TimeNow.microsecond)+',\t'
                +'9999'+','
                +'999999'+'\n')
    time.sleep(0.5)
    
