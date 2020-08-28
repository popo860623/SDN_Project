from operator import attrgetter

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
import requests
import urllib2

import json

class SimpleMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    
    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
	self.f = open('workfile', 'w')
	#self.app.run(port=5050)

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
        response = requests.get('http://127.0.0.1:5000/controller')
	print response.content+'.....................'
	if response.content == 'drop':
	    return
	msg= ev.msg
	dp= msg.datapath
	ofp= dp.ofproto
	parser = dp.ofproto_parser

	self.logger.debug("************ Debug ************")
	# output port
	actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
	out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,in_port=msg.match['in_port'],actions=actions)
	dp.send_msg(out)
   
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

    def _monitor(self):
	while True:
		for dp in self.datapaths.values():
			self._request_stats(dp)
		hub.sleep(10)
    def _request_stats(self, datapath):
	self.logger.debug('send stats request: %016x', datapath.id)
	ofproto = datapath.ofproto
	parser = datapath.ofproto_parser

	req = parser.OFPFlowStatsRequest(datapath)
	datapath.send_msg(req)

	req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
	datapath.send_msg(req)
	
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
	body = ev.msg.body
	#It will show the message per 10 second.
	self.logger.info('datapath         in-port  eth-dst           out-port packets  bytes')
	self.logger.info('---------------- -------- ----------------- -------- -------- --------')
	for stat in sorted([flow for flow in body if flow.priority == 1],key=lambda flow: (flow.match['in_port'],flow.match['eth_dst'])):
		#self.logger.info('%016x %8x %17s %8x %8d %8d',ev.msg.datapath.id,stat.match['in_port'], stat.match['eth_dst'],stat.instructions[0].actions[0].port,stat.packet_count, stat.byte_count)
		self.logger.info('%s', json.dumps(ev.msg.to_jsondict(), ensure_ascii=True,
                                  indent=3, sort_keys=True))
		self.f.write(str(ev.msg.datapath.id)+' '+str(stat.match['in_port'])+' '+str(stat.match['eth_dst'])+' '+str(stat.instructions[0].actions[0].port)+' '+str(stat.packet_count)+' '+str()+' '+str(stat.byte_count)+'\n')
