from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


class L2Switch(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
	def __init__(self, *args, **kwargs):
		super(L2Switch, self).__init__(*args, **kwargs)
		self.mac_to_port = {}

	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		self.logger.info("****** Add Defualt Flow *******")
		dp = ev.msg.datapath
		ofp = dp.ofproto
		parser = dp.ofproto_parser
	#	self.logger.info("dp.id = %d",dp.id) 
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER,ofp.OFPCML_NO_BUFFER)]
		inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,actions)]
		mod = parser.OFPFlowMod(datapath=dp, priority=0,match=match, instructions=inst)
		dp.send_msg(mod)
	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def packet_in_handler(self, ev):
		self.logger.info("****** Packet In *******")
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		parser = dp.ofproto_parser

		# packet data
		in_port = msg.match['in_port']
		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocols(ethernet.ethernet)[0]

		if eth.ethertype == ether_types.ETH_TYPE_LLDP:
			#ignore lldp packet
			return
		dst = eth.dst
		src = eth.src

		dpid = dp.id
		self.mac_to_port.setdefault(dpid, {})
		#self.logger.info("packet in dpid:%s src:%s dst:%s in_port:%s",dpid, src, dst, in_port)
		# learn amac address to avoid FLOOD next time.
		self.mac_to_port[dpid][src] = in_port
		self.logger.debug("%s", self.mac_to_port[dpid])
		'''if dst in self.mac_to_port[dpid]:
			self.logger.debug("*********** Add Flow ************")
			out_port = self.mac_to_port[dpid][dst]
			match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
			actions = [parser.OFPActionOutput(out_port)]
			inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
			mod = parser.OFPFlowMod(datapath=dp, priority=4096, match=match, instructions=inst)
			dp.send_msg(mod)'''

		self.logger.debug("*********** FLOOD ************")
		actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
		data = None
		if msg.buffer_id == ofp.OFP_NO_BUFFER:
			data = msg.data
		out = parser.OFPPacketOut( datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
		dp.send_msg(out)
