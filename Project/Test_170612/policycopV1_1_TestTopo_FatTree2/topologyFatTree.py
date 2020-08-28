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
Fat_Tree_Level=2
class CustomTopo(Topo):

    def __init__(self,**opts):
        Topo.__init__(self, **opts)
        global Fat_Tree_Level

        self.s=[]
        for i in range(0, 2+4*Fat_Tree_Level) :
            self.s.append(self.addSwitch('s'+str(i),protocols='OpenFlow13'))

        self.server=[]
        for i in range(0, 2*Fat_Tree_Level) :
            self.server.append(self.addHost('server'+str(i)))

        self.client=[]
        for i in range(0, 4*Fat_Tree_Level):
            self.client.append(self.addHost('client'+str(i)))

        for i in range(0, Fat_Tree_Level) :

            self.addLink(self.s[0],self.s[2+4*i+0],bw=10,delay='3ms')
            self.addLink(self.s[1],self.s[2+4*i+1],bw=10,delay='3ms')

            self.addLink(self.s[2+4*i],self.s[2+4*i+2],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i],self.s[2+4*i+3],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i+1],self.s[2+4*i+2],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i+1],self.s[2+4*i+3],bw=10,delay='3ms')

            self.addLink(self.s[2+4*i+2],self.client[4*i+0],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i+2],self.client[4*i+1],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i+3],self.client[4*i+2],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i+3],self.client[4*i+3],bw=10,delay='3ms')

            self.addLink(self.s[2+4*i+0],self.server[2*i+0],bw=10,delay='3ms')
            self.addLink(self.s[2+4*i+1],self.server[2*i+1],bw=10,delay='3ms')

topos = {'mytopo': (lambda: CustomTopo())}

def createTopo():
    global Fat_Tree_Level

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

    time.sleep(3)
    #net.pingAll()
    for i in net.hosts :
        net.ping([net.hosts[0],i])
        net.ping([net.hosts[1],i])

    time.sleep(3)

    #print net.hosts[1].cmd('tcpdump -w server1Log.dmp &')
    #print net.hosts[2].cmd('tcpdump -w server2Log.dmp &')
    #print net.hosts[3].cmd('tcpdump -w server3Log.dmp &')

    #time.sleep(1)

    for i in range(0,2*Fat_Tree_Level) :
        print net.hosts[(-1)*(i+1)].cmd('iperf -s -u -i 1 -p 5001 -w 2048K &')

    time.sleep(3)
    random.seed(a=5)
    global client_per_node

    a=random.sample(range(4*Fat_Tree_Level), 4*Fat_Tree_Level)
    print 'random sequence is : '+str(a)

    for i in a :
        print net.hosts[i].cmd('iperf -c '+str(net.hosts[(-2)*Fat_Tree_Level].IP())+' -p 5001 -i 1 -t 3000 -u -w 2048K &')
        time.sleep(1)
    
    print 'Main IP is :'
    print net.hosts[(-2)*Fat_Tree_Level].IP()

    print 'Other IPs are :'
    for i in range(0,2*Fat_Tree_Level) :
        print net.hosts[(-1)*(i+1)].IP()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if os.getuid() != 0:
        logger.debug("You are NOT root")
    elif os.getuid() == 0:
	os.system("sudo mn -c")
        createTopo()
