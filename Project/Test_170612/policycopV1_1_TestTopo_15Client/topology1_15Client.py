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
client_per_node=15
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

        self.addLink(self.s[0],self.s[1],bw=10,delay='3ms')
        self.addLink(self.s[1],self.s[2],bw=10,delay='3ms')
        self.addLink(self.s[2],self.s[3],bw=10,delay='3ms')
        self.addLink(self.s[3],self.s[4],bw=10,delay='3ms')
        self.addLink(self.s[4],self.s[5],bw=10,delay='3ms')

        self.addLink(self.s[0],self.s[5],bw=10,delay='3ms')
        self.addLink(self.s[0],self.s[2],bw=10,delay='3ms')
        self.addLink(self.s[3],self.s[5],bw=10,delay='3ms')
        self.addLink(self.s[2],self.s[5],bw=10,delay='3ms')

        self.server=[]
        self.server.append(self.addHost('server1'))
        self.server.append(self.addHost('server2'))
        self.server.append(self.addHost('server3'))

        self.client=[]

        global client_per_node

        for i in range(client_per_node*3):
            self.client.append(self.addHost('client%s' % (i)))

        for i in range(client_per_node):
            self.addLink(self.s[0],self.client[i])
            self.addLink(self.s[1],self.client[i+client_per_node])
            self.addLink(self.s[2],self.client[i+2*client_per_node])

        self.addLink(self.s[3],self.server[0])
        self.addLink(self.s[4],self.server[1])	
        self.addLink(self.s[5],self.server[2])

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

    print net.hosts[0].cmd('iperf -s -u -i 1 -p 5001 -w 2048K &')
    print net.hosts[1].cmd('iperf -s -u -i 1 -p 5001 -w 2048K &')
    print net.hosts[2].cmd('iperf -s -u -i 1 -p 5001 -w 2048K &')

    time.sleep(3)
    random.seed(a=5)
    global client_per_node

    a=random.sample(range(3*client_per_node), 3*client_per_node)
    print a
    #print net.hosts[0].cmd('iperf -c '+str(net.hosts[-3].IP())+' -p 5001 -i 1 -t 3000 -u -w 2048K &')
    for i in a :
        print net.hosts[i].cmd('iperf -c '+str(net.hosts[-3].IP())+' -p 5001 -i 1 -t 3000 -u -w 2048K &')
        time.sleep(1)

    print 'Main IP is :'
    print net.hosts[-3].IP()

    print 'Other IPs are :'
    for i in range(0,3) :
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
