from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf, TCLink
from mininet.topo import Topo
import logging
import os
import time
import random
import sys
client_per_node=2
class CustomTopo(Topo):

    def __init__(self,**opts):
        Topo.__init__(self, **opts)
        self.s=[]
        self.s.append(self.addSwitch('s0',protocols='OpenFlow13'))
        self.s.append(self.addSwitch('s1',protocols='OpenFlow13'))
        self.s.append(self.addSwitch('s2',protocols='OpenFlow13'))
        self.s.append(self.addSwitch('s3',protocols='OpenFlow13'))
        self.s.append(self.addSwitch('s4',protocols='OpenFlow13'))
        self.s.append(self.addSwitch('s5',protocols='OpenFlow13'))

        self.addLink(self.s[0],self.s[1],bw=10,delay='100ms')
        self.addLink(self.s[1],self.s[2],bw=10,delay='100ms')
        self.addLink(self.s[2],self.s[3],bw=10,delay='100ms')
        self.addLink(self.s[3],self.s[4],bw=10,delay='100ms')
        self.addLink(self.s[4],self.s[5],bw=10,delay='100ms')

        self.addLink(self.s[0],self.s[5],bw=10,delay='100ms')
        self.addLink(self.s[0],self.s[2],bw=10,delay='100ms')
        self.addLink(self.s[3],self.s[5],bw=10,delay='100ms')
        self.addLink(self.s[2],self.s[5],bw=10,delay='100ms')

        self.server=[]
        self.server.append(self.addHost('server1'))
        self.server.append(self.addHost('server2'))
        self.server.append(self.addHost('server3'))

        self.client=[]

        global client_per_node

        for i in range(client_per_node*3):
            self.client.append(self.addHost('client%s' % (i)))

        for i in range(client_per_node):
            self.addLink(self.s[0],self.client[i],bw=10,delay='100ms')
            self.addLink(self.s[1],self.client[i+client_per_node],bw=10,delay='100ms')
            self.addLink(self.s[2],self.client[i+2*client_per_node],bw=10,delay='100ms')

        self.addLink(self.s[3],self.server[0],bw=10,delay='100ms')
        self.addLink(self.s[4],self.server[1],bw=10,delay='100ms')	
        self.addLink(self.s[5],self.server[2],bw=10,delay='100ms')

topos = {'mytopo': (lambda: CustomTopo())}

def createTopo():
    logging.debug("Create Topo")
    topo = CustomTopo()

    logging.debug("Start Mininet")
    CONTROLLER_IP = "127.0.0.1"
    CONTROLLER_PORT = 6633
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.addController(
        'controller', controller=RemoteController,
        ip=CONTROLLER_IP, port=CONTROLLER_PORT)

    net.start()
    time.sleep(1)
    for i in net.hosts :
        net.ping([net.hosts[0],i])
        net.ping([net.hosts[1],i])

    time.sleep(3)
    if not os.path.exists(sys.argv[1]):
        os.makedirs(sys.argv[1], mode=7777)
    print net.hosts[-3].cmd('python ../UDPserver.py 5001 '+sys.argv[1]+'/Server'+str(1)+'.log &')
    print net.hosts[-2].cmd('python ../UDPserver.py 5001 '+sys.argv[1]+'/Server'+str(2)+'.log &')
    print net.hosts[-1].cmd('python ../UDPserver.py 5001 '+sys.argv[1]+'/Server'+str(3)+'.log &')
    
    time.sleep(1)
    random.seed(a=5)
    global client_per_node

    a=random.sample(range(3*client_per_node), 3*client_per_node)
    print a
    
    for i in a :
        print net.hosts[i].cmd('python ../UDPclient.py '+sys.argv[1]+'/client'+str(i)+'.csv '+str(net.hosts[-3].IP())+' 5001 &')
        time.sleep(3)
    

    print net.hosts[-3].IP()
    #CLI(net)
    print 'time.sleep(60)'
    time.sleep(60)
    net.stop()
    os.system('sudo chmod 7777 '+sys.argv[1]+' '+sys.argv[1]+'/*')

if __name__ == '__main__':
    setLogLevel('info')
    if os.getuid() != 0:
        logger.debug("You are NOT root")
    elif os.getuid() == 0:
	os.system("sudo mn -c")
        createTopo()
