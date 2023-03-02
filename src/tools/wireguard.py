# External
from python_wireguard import ClientConnection, Key, Server, wireguard
import sys, os, time

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

global WG_DOOR_PORT, WG_DOOR_IP
WG_DOOR_PORT = 51820
WG_DOOR_IP = "192.168.0.254/24"
WG_PEER_IP = "192.168.0."

class Wireguard:
	"""Wireguard: manager for wireguard"""
	def __init__(self):
		# We need to have keys in any case (even if they are not the expected ones)
		self.privkey = Key("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=")
		self.pubkey = Key("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=")
		self.server = None
		self.peers = []
		self.name = "wg-srv"

	# Executed before up
	def pre_up(self):
		return {"success": True}

	# Set up wireguard interface
	def up(self):
		pre_res = self.pre_up()
		if not pre_res["success"]:
			return pre_res

		log(DEBUG, "Wireguard.up: building wireguard interface")
		self.server = Server(self.name, self.privkey, WG_DOOR_IP, WG_DOOR_PORT)

		log(DEBUG, "Wireguard.up: enabling wireguard server")
		self.server.enable()

		# Add peers
		for peer in self.peers:
			log(DEBUG, "Wireguard.up: adding peer (key: "+peer["key"]+" IP: "+peer["ip"]+")")
			self.server.add_client(ClientConnection(Key(peer["key"]), peer["ip"]))

		post_res = self.post_up()
		if not post_res["success"]:
			return post_res

		return {"success": True}

	# Exeuted after up
	def post_up(self):
		run(
			"iptables -A POSTROUTING -t nat -s 192.168.0.0/24 -j MASQUERADE",
			"Failed to start wireguard packets masquerade"
		)
		return {"success": True}

	# Executed before down
	def pre_down(self):
		run(
			"iptables -D POSTROUTING -t nat -s 192.168.0.0/24 -j MASQUERADE",
			"Failed to stop wireguard packets masquerade"
		)
		return {"success": True}

	# Set down wireguard interface
	def down(self):
		if not self.is_up():
			return {"success": False}
		else:
			pre_res = self.pre_down()
			if not pre_res["success"]:
				return pre_res

			if self.server is None:
				self.server = Server(self.name, self.privkey, WG_DOOR_IP, WG_DOOR_PORT)
			self.server.delete_interface()

			post_res = self.post_down()
			if not post_res["success"]:
				return post_res

			return {"success": True}

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

	def is_up(self):
		# The wireguard library does not allow to check which devices are up
		# (Note: there is a wireguard.list_devices function but it prints the result to stdout instead of returning it)
		res = run(
			"wg-quick show interfaces",
			"Failed to list wireguard interfaces"
			output=True
		)
		return self.name in res.split(" ")