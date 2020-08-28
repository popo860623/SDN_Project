import SocketServer
from datetime import datetime
import sys

class MyUDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        datetime_object = datetime.strptime(data, '%Y-%m-%d %H:%M:%S.%f')
        timeDiff=datetime.now()-datetime_object
        print str(datetime.now())+'\t'+str(self.client_address)+'\'delay is :'+str(timeDiff.seconds)+' second + '+str(timeDiff.microseconds)+' microseconds'
        socket.sendto(str(timeDiff), self.client_address)
        with open(sys.argv[2], "a") as record:
            record.write(str(datetime.now().hour)+','
                +str(datetime.now().minute)+','
                +str(datetime.now().second)+','
                +str(datetime.now().microsecond)+',\t'
                +str(self.client_address)+'connecting\n')

if __name__ == "__main__":
    with open(sys.argv[2], "w") as record:
        record.write('')
    HOST, PORT = "0.0.0.0", int(sys.argv[1])
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
