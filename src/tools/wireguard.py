# External
from python_wireguard import ClientConnection, Key, Server, wireguard
import sys, os, time

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

global WG_DOOR_PORT, WG_DOOR_IP, WG_PEER_IP, WG_PEER_MASK
WG_DOOR_PORT = 51820
WG_DOOR_IP = "192.168.0.254/16"
WG_PEER_IP = "192.168."

class Wireguard:
	"""Wireguard: manager for wireguard"""
	def __init__(self):
		# We need to have keys in any case (even if they are not the expected ones)
		self.privkey = Key("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=")
		self.pubkey = Key("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=")
		self.server = None
		self.peers = []
		self.name = "wg-srv"

	def generate_ip(self, dev_id):
		return WG_PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)

	# Executed before up
	def pre_up(self, res): return res

	# Set up wireguard interface
	def up(self, client):
		res = {"success": True, ERROR:[], WARNING:[], INFO:[]}
		
		if self.is_up():
			log(WARNING, "Wireguard.up: the interface is already up. Trying to restart it")
			down_res = self.down()
			if FATAL in down_res: return down_res

		res = self.pre_up(res)
		if FATAL in res: return res

		log(DEBUG, "Wireguard.up: building wireguard interface")
		self.server = Server(self.name, self.privkey, WG_DOOR_IP, WG_DOOR_PORT)

		log(DEBUG, "Wireguard.up: enabling wireguard server")
		try:
			self.server.enable()
		except Exception as err:
			log(ERROR, "Wireguard.up:", err)
			res[ERROR] += ["failed to enable wireguard server"]
			return res

		# Add peers
		for peer in self.peers:
			log(DEBUG, "Wireguard.up: adding peer (key: "+peer["key"]+" IP: "+peer["ip"]+")")
			self.server.add_client(ClientConnection(Key(peer["key"]), peer["ip"]))

		res = self.post_up(res)
		if FATAL in res: return res

		return res

	# Exeuted after up
	def post_up(self, res):
		if not run("iptables -A POSTROUTING -t nat -s 192.168.0.0/24 -j MASQUERADE"):
			log(ERROR, "Wireguard.post_up: failed to start wireguard packets masquerade")
			res[ERROR] += ["failed to start wireguard packets masquerade"]
			res["success"] = False
			return res
		else:
			return res

	# Executed before down
	def pre_down(self, res):
		if not run("iptables -D POSTROUTING -t nat -s 192.168.0.0/24 -j MASQUERADE"):
			log(ERROR, "Wireguard.pre_down: failed to stop wireguard packets masquerade")
			res[ERROR] += ["failed to stop wireguard packets masquerade"]
			res["success"] = False
			return res
		else:
			return res

	# Set down wireguard interface
	def down(self, client):
		res = {"success": True, ERROR:[], WARNING:[], INFO:[]}

		if not self.is_up():
			res[INFO] += ["the wireguard interface is already down"]
			return res
		else:
			res = self.pre_down(res)
			if FATAL in res: return res

			if self.server is None:
				self.server = Server(self.name, self.privkey, WG_DOOR_IP, WG_DOOR_PORT)
			self.server.delete_interface()

			res = self.post_down(res)
			if FATAL in res: return res

			return res

	# Executed after down
	def post_down(self, res): return res

	# Generate wireguard keys
	def keygen(self, client):
		res = {}

		self.privkey, self.pubkey = Key.key_pair()

		res["privkey"] = str(self.privkey)
		res["pubkey"]  = str(self.pubkey)

		return res

	def reset_peers(self, client):
		self.peers = []

	# Add a wireguard peer
	def add_peer(self, client, key, dev_id):
		self.peers += [{
			"key":key,
			"ip": self.generate_ip(dev_id)
		}]
		return {"success": True}

	def is_up(self):
		# The wireguard library does not allow to check which devices are up
		# (Note: there is a wireguard.list_devices function but it prints the result to stdout instead of returning it)
		res = run("wg show interfaces", output=True)
		return self.name in res.split()