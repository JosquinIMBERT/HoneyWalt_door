# External
from python_wireguard import ClientConnection, Key, Server, wireguard
import sys, os, time

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.utils.rpc import *

global WG_DOOR_PORT, WG_DOOR_IP, WG_PEER_IP, WG_PEER_MASK
WG_DOOR_PORT = 51820
WG_DOOR_IP = "192.168.0.254/16"
WG_PEER_IP = "192.168."

class Wireguard:
	"""Wireguard: manager for wireguard"""
	def __init__(self):
		self.privkey = None
		self.pubkey = None
		self.server = None
		self.peers = []
		self.name = "wg-srv"
		self.keyfile = to_root_path("var/key/wireguard.json")
		self.load_keys(FakeClient(ignore_logs=True))

	def load_keys(self, client):
		if not os.path.isfile(self.keyfile):
			log(ERROR, "Failed to load wireguard keys.")
			client.log(ERROR, "Failed to load wireguard keys.")
			return False

		with open(self.keyfile, "r") as wgkeyfile:
			keys = json.loads(wgkeyfile.read())
			self.privkey, self.pubkey = Key(keys["privkey"])

		return True

	def generate_ip(self, dev_id):
		return WG_PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)

	# Set up wireguard interface
	def up(self, client):
		if self.is_up():
			log(WARNING, "Wireguard.up: the interface is already up. Trying to restart it")
			if not self.down(client): return False

		if not self.load_keys(client): return False

		log(DEBUG, "Wireguard.up: building wireguard interface")
		self.server = Server(self.name, self.privkey, WG_DOOR_IP, WG_DOOR_PORT)

		log(DEBUG, "Wireguard.up: enabling wireguard server")
		try:
			self.server.enable()
		except Exception as err:
			log(ERROR, "Wireguard.up:", err)
			client.log(ERROR, "failed to enable wireguard server")
			return None

		# Add peers
		for peer in self.peers:
			log(DEBUG, "Wireguard.up: adding peer (key: "+peer["key"]+" IP: "+peer["ip"]+")")
			self.server.add_client(ClientConnection(Key(peer["key"]), peer["ip"]))

		self.post_up(client)

		return True

	# Exeuted after up
	def post_up(self, client):
		if not run("iptables -A POSTROUTING -t nat -s 192.168.0.0/16 -j MASQUERADE"):
			log(ERROR, "Wireguard.post_up: failed to start wireguard packets masquerade")
			client.log(ERROR, "failed to start wireguard packets masquerade")
			return False
		else:
			return True

	# Executed before down
	def pre_down(self, client):
		if not run("iptables -D POSTROUTING -t nat -s 192.168.0.0/16 -j MASQUERADE"):
			log(ERROR, "Wireguard.pre_down: failed to stop wireguard packets masquerade")
			client.log(ERROR, "failed to stop wireguard packets masquerade")
			return None
		else:
			return True

	# Set down wireguard interface
	def down(self, client):
		if not self.is_up():
			client.log(INFO, "the wireguard interface is already down")
			return None
		else:
			if not self.load_keys(client): return False

			self.pre_down(client)

			if self.server is None:
				self.server = Server(self.name, self.privkey, WG_DOOR_IP, WG_DOOR_PORT)
			self.server.delete_interface()

			return True

	# Generate wireguard keys
	def keygen(self, client):
		res = {}

		self.privkey, self.pubkey = Key.key_pair()

		res["privkey"] = str(self.privkey)
		res["pubkey"]  = str(self.pubkey)

		with open(self.keyfile, "w") as wgkeyfile:
			wgkeyfile.write(json.dumps({"privkey":str(self.privkey), "pubkey":str(self.pubkey)}))

		return res

	def reset_peers(self, client):
		self.peers = []

	# Add a wireguard peer
	def add_peer(self, client, key, dev_id):
		self.peers += [{
			"key":key,
			"ip": self.generate_ip(dev_id)
		}]
		return True

	def is_up(self):
		# The wireguard library does not allow to check which devices are up
		# (Note: there is a wireguard.list_devices function but it prints the result to stdout instead of returning it)
		res = run("wg show interfaces", output=True)
		return self.name in res.split()