from operator import attrgetter

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event, switches
from ryu.topology.api import get_switch,get_all_switch,get_link,get_all_link,get_host,get_all_host
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
import requests
import urllib2
import sys
import copy
import math

import json

def BellmanFord(weight,source):
	distance=[999999999]*len(weight)
	distance[source]=0
	parent=[0]*len(weight)
	parent[source]=source
	
	for i in range(0,len(weight)):
		for a in range(0,len(weight)):
			for b in range(0,len(weight)):
				if distance[a] != 999999999 and weight[a][b] != 999999999:
					if (distance[a] + weight[a][b]) < distance[b]:
						distance[b] = distance[a] + weight[a][b]
						parent[b] = a
	for a in range(0,len(weight)):
		for b in range(0,len(weight)):
			if distance[a] + weight[a][b] < distance[b]:
				sys.exit("Graph contains a negative-weight cycle")
	return ( distance , parent )

def MakeForwardingTable(weight):
	table=[]
	for i in range(0,len(weight)):
		table.append([0]*len(weight))
	distance=[]
	for i in range(0,len(weight)):
		distance.append([0]*len(weight))
	parent=[]
	for i in range(0,len(weight)):
		parent.append([0]*len(weight))
	
	for i in range(0,len(weight)):
		distance[i] , parent[i] = BellmanFord(weight,i)

	for i in range(0,len(weight)):
		for j in range(0,len(weight)):
			parentNode=j
			while parent[i][parentNode] != i:
				parentNode = parent[i][parentNode]
			table[i][j]=parentNode
	
	return table
class SimpleMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
	self.TopoNumberTo = []
	self.forwardingTable = {}
	self.ArpTable={}
	self.topology_thread = hub.spawn(self._topology_thread)
	self.all_switch=[]
	self.all_link=[]
	self.all_host=[]
		

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
	self.logger.info("****** Add DefualtFlow *******")
	dp= ev.msg.datapath
	ofp= dp.ofproto
	parser = dp.ofproto_parser
	match = parser.OFPMatch()
	actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER,ofp.OFPCML_NO_BUFFER)]
	inst= [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,actions)]
	mod = parser.OFPFlowMod(datapath=dp, priority=0,match=match, instructions=inst)
	dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
	
	if len(self.forwardingTable)==0:
		return
	msg = ev.msg
	
	pkt = packet.Packet(data=msg.data)
	pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
	#print dir(pkt_ethernet)
	if pkt_ethernet.ethertype == ether_types.ETH_TYPE_LLDP:
		#ignore lldp packet
		return
	pkt_arp = pkt.get_protocol(arp.arp)
	if pkt_arp:
		self._handle_arp(msg=msg, pkt=pkt)
		return
	else:
		self._handle_packet(msg=msg, pkt=pkt)
		return
	

    def _handle_arp(self,msg, pkt):
	datapath = msg.datapath
	dpid = datapath.id
	in_port = msg.match['in_port']
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
	data = None
	if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        	data = msg.data
	#print self.ArpTable[dpid]
	#print 'in_port = '
	#print in_port
	for ToPort in self.ArpTable[dpid]:
		if ToPort != in_port:
        		actions = [parser.OFPActionOutput(port=ToPort)]
        		out = parser.OFPPacketOut(datapath=datapath,
				buffer_id=msg.buffer_id,
				in_port=in_port,
				actions=actions,
				data=data)
			self.logger.info("****** send *******")
        		datapath.send_msg(out)
    def _handle_packet(self,msg, pkt):
	datapath = msg.datapath
	dpid = datapath.id
	in_port = msg.match['in_port']
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
	data = None
	pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
	if msg.buffer_id == ofproto.OFP_NO_BUFFER:
        	data = msg.data
	dst = pkt_ethernet.dst
	#print '...........................................'
	#print dst
	#print self.forwardingTable[dpid]
	#print 'in_port = '
	#print in_port
	if dst in self.forwardingTable[dpid]:
		self.logger.info("****** set flow *******")
		match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
		out_port = self.forwardingTable[dpid][dst]
		actions = [parser.OFPActionOutput(out_port)]
		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
		mod = parser.OFPFlowMod(datapath=datapath, priority=4096, match=match, instructions=inst)
		datapath.send_msg(mod)
		self.logger.info("****** Packet In *******")
        	actions = [parser.OFPActionOutput(port=out_port)]
        	out = parser.OFPPacketOut(datapath=datapath,
			buffer_id=msg.buffer_id,
			in_port=in_port,
			actions=actions,
			data=data)
		self.logger.info("****** send *******")
        	datapath.send_msg(out)
    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
	datapath = ev.datapath
	if ev.state == MAIN_DISPATCHER:
		if not datapath.id in self.datapaths:
			self.logger.debug('register datapath: %016x', datapath.id)
			self.datapaths[datapath.id] = datapath
	elif ev.state == DEAD_DISPATCHER:
		if datapath.id in self.datapaths:
			self.logger.debug('unregister datapath: %016x', datapath.id)
			del self.datapaths[datapath.id]

    def _topology_thread(self):
	while True:
		self.all_switch=get_all_switch(self)
		self.all_link=get_all_link(self)
		self.all_host=get_all_host(self)
		
		print 'self.all_switch = '
		print len(self.all_switch)
		print 'self.all_link = '
		print len(self.all_link)
		print 'self.all_host = '
		print len(self.all_host)
		for a in self.all_host:
			print a.ipv4
		hub.sleep(3)
		if len(self.all_switch) == 6 and len(self.all_host) == 6:
			c=0
			for i in range(0,len(self.all_switch)) :
				self.TopoNumberTo.append(['switch',self.all_switch[i]])
			for i in range(0,len(self.all_host)) :
				self.TopoNumberTo.append(['host',self.all_host[i]])

			for x in self.TopoNumberTo:
				print (x,':',str(x))
			weight=[]
			for i in range(0,len(self.TopoNumberTo)):
				weight.append([999999999]*len(self.TopoNumberTo))
			for i in range(0,len(weight)):			
				for j in range(0,len(weight[i])):
					if i == j :
						weight[i][j]=0
			for link in self.all_link:
				indexA=0
				indexB=0
				for i in self.TopoNumberTo:
					if i[0] == 'switch' and i[1].dp.id == link.src.dpid :
						indexA = self.TopoNumberTo.index(i)
					if i[0] == 'switch' and i[1].dp.id == link.dst.dpid :
						indexB = self.TopoNumberTo.index(i)
				weight[indexA][indexB]=1
				weight[indexB][indexA]=1
			for host in self.all_host:
				indexA=0
				indexB=0
				for i in self.TopoNumberTo:
					if i[0] == 'host' and i[1] == host :
						indexA = self.TopoNumberTo.index(i)
					if i[0] == 'switch' and i[1].dp.id == host.port.dpid :
						indexB = self.TopoNumberTo.index(i)
				weight[indexA][indexB]=1
				weight[indexB][indexA]=1
			print weight
			#forwarding matrix to forwarding Table
			forwardingMatrix = MakeForwardingTable(weight)
			
			print forwardingMatrix

			for i in range(0,len(self.TopoNumberTo)):
				
				if self.TopoNumberTo[i][0] == 'switch':
					
					switchdp=self.TopoNumberTo[i][1].dp.id
					self.forwardingTable[switchdp]={}
					for j in range(0,len(forwardingMatrix[i])):
						if self.TopoNumberTo[j][0] == 'host' :
							dsthost=self.TopoNumberTo[j][1].mac
							Pport=-1
							if self.TopoNumberTo[forwardingMatrix[i][j]][0] == 'switch':
								for link in self.all_link:
									if link.src.dpid == switchdp and link.dst.dpid == self.TopoNumberTo[forwardingMatrix[i][j]][1].dp.id :
										Pport=link.src.port_no
										
							if self.TopoNumberTo[forwardingMatrix[i][j]][0] == 'host':
								Pport=self.TopoNumberTo[j][1].port.port_no
							
							if Pport==-1:
								print 'host not found'
								return
							else :
								self.forwardingTable[switchdp][dsthost] = Pport





										
			check=[0]*len(self.TopoNumberTo)
			check[0]=1
			arpMatrix=[]
			for i in range(0,len(self.TopoNumberTo)):
				arpMatrix.append([0]*len(self.TopoNumberTo))
			for i in range(0,len(self.TopoNumberTo)):
				for j in range(0,len(self.TopoNumberTo)):
					if weight[i][j]==1 and check[j] == 0:
						arpMatrix[i][j]=1
						arpMatrix[j][i]=1
						check[j]=1
			print arpMatrix
			
			for i in range(0,len(self.TopoNumberTo)):
				if self.TopoNumberTo[i][0] == 'switch':
					
					switchdp=self.TopoNumberTo[i][1].dp.id
					self.ArpTable[switchdp]=[]
					for j in range(0,len(arpMatrix[i])):
						if arpMatrix[i][j] == 1 :
							Pport=-1
							if self.TopoNumberTo[j][0] == 'switch':
								for link in self.all_link:
									if link.src.dpid == switchdp and link.dst.dpid == self.TopoNumberTo[j][1].dp.id :
										Pport=link.src.port_no
										
							if self.TopoNumberTo[j][0] == 'host':
								Pport=self.TopoNumberTo[j][1].port.port_no
							
							if Pport==-1:
								print 'Pport not found'
								return
							else :
								self.ArpTable[switchdp].append(Pport)

			print self.ArpTable
			

			
			break
    		
