# External
from python_wireguard import ClientConnection, Key, Server
import sys, os, time
sys.path[0] = os.path.join(os.environ["HONEYWALT_DOOR_HOME"],"src/")

# Internal
from utils.files import *
from utils.logs import *
from utils.system import *

global WG_DOOR_PORT, WG_DOOR_IP
WG_DOOR_PORT = 51820
WG_DOOR_IP = "192.168.0.254/24"
WG_PEER_IP = "192.168.0."

class Wireguard:
	"""Wireguard: manager for wireguard"""
	def __init__(self):
		self.privkey = None
		self.pubkey = None
		self.server = None
		self.peers = []

	# Executed before up
	def pre_up(self):
		return {"success": True}

	# Set up wireguard interface
	def up(self):
		res = {"success": True}

		pre_res = self.pre_up()
		if not pre_res["success"]:
			return pre_res

		self.server = Server("wg-srv", self.privkey, WG_DOOR_IP, WG_DOOR_PORT)
		self.server.enable()

		# Add peers
		for peer in self.peers:
			self.server.add_client(ClientConnection(Key(peer["key"]), peer["ip"]))

		post_res = self.post_up()
		if not post_res["success"]:
			return post_res

		return res

	# Exeuted after up
	def post_up(self):
		run("iptables -A POSTROUTING -t nat -s 192.168.0.0/24 -j MASQUERADE")
		return {"success": True}

	# Executed before down
	def pre_down(self):
		run("iptables -D POSTROUTING -t nat -s 192.168.0.0/24 -j MASQUERADE")
		return {"success": True}

	# Set down wireguard interface
	def down(self):
		res = {"success": True}

		pre_res = self.pre_down()
		if not pre_res["success"]:
			return pre_res

		if self.server is None:
			self.server = Server("wg-srv", self.privkey, WG_DOOR_IP, WG_DOOR_PORT)
		self.server.delete_interface()

		post_res = self.post_down()
		if not post_res["success"]:
			return post_res

		return res

	# Executed after down
	def post_down(self):
		return {"success": True}

	# Generate wireguard keys
	def keygen(self):
		res = {"success": True, "answer": {}}

		self.privkey, self.pubkey = Key.key_pair()

		res["answer"]["privkey"] = str(self.privkey)
		res["answer"]["pubkey"]  = str(self.pubkey)

		return res

	# Add a wireguard peer
	def add_peer(self, key, dev_id):
		self.peers += [{"key":key, "ip": WG_PEER_IP+str(dev_id)}]
		return {"success": True}