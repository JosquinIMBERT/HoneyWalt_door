# External
from python_wireguard import ClientConnection, Key, Server, wireguard
from string import Template
import sys, os, time

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.utils.rpc import *

global WG_DOOR_PORT, WG_DOOR_IP, WG_PEER_IP, WG_PEER_MASK, CONF_PATH
WG_DOOR_PORT = 51820
WG_DOOR_IP	 = "192.168.0.254"
WG_PEER_IP	 = "192.168."
WG_PEER_MASK = "16"
CONF_PATH	 = "/etc/wireguard/"

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
			self.privkey = keys["privkey"]
			self.pubkey = keys["pubkey"]

		return True

	def generate_ip(self, dev_id):
		return WG_PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)

	# Set up wireguard interface
	def up(self, client):
		# Checking current state
		if self.is_up():
			log(WARNING, "the interface is already up. Trying to restart it")
			if not self.down(client):
				log(WARNING, "failed to stop the wireguard server")
				return False

		# Removing old configuration files
		for old_conf_file in os.listdir(CONF_PATH):
			os.remove(os.path.join(CONF_PATH, old_conf_file))

		# Loading Server Wireguard Keys
		if not self.load_keys(client): return False

		# Loading configuration templates
		with open(to_root_path("var/template/wg_srv.txt"), "r") as temp_file:
			template_conf = Template(temp_file.read())
		with open(to_root_path("var/template/wg_peer.txt"), "r") as temp_file:
			template_peer = Template(temp_file.read())

		conf_filename = os.path.join(CONF_PATH, self.name+".conf")

		# Creating configuration
		config = template_conf.substitute({
			"name": self.name,
			"server_privkey": self.privkey,
			"address": WG_DOOR_IP,
			"mask": WG_PEER_MASK,
			"server_port": WG_DOOR_PORT
		})

		for peer in self.peers:
			peer_config = template_peer.substitute({
				"pubkey": peer["key"],
				"address": peer["ip"],
				"mask": WG_PEER_MASK
			})
			config += "\n" + peer_config

		# Writing the configuration file
		with open(conf_filename, "w") as conf_file:
			conf_file.write(config)

		# Run 'wg-quick up'
		cmd = "wg-quick up "+conf_filename
		run(cmd)

		return True

	# Set down wireguard interface
	def down(self, client):
		if not self.is_up():
			client.log(INFO, "the wireguard interface is already down")
			return None
		else:
			conf_filename = os.path.join(CONF_PATH, self.name+".conf")

			# Run 'wg-quick down'
			cmd = "wg-quick down "+conf_filename
			run(cmd)

			return True

	# Generate wireguard keys
	def keygen(self, client):
		res = {}

		self.privkey, self.pubkey = Key.key_pair()
		self.privkey = str(self.privkey)
		self.pubkey = str(self.pubkey)

		res["privkey"] = self.privkey
		res["pubkey"]  = self.pubkey

		with open(self.keyfile, "w") as wgkeyfile:
			wgkeyfile.write(json.dumps({"privkey":self.privkey, "pubkey":self.pubkey}))

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