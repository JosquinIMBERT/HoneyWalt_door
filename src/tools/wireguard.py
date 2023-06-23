# External
from python_wireguard import ClientConnection, Key, Server, wireguard
from string import Template
import sys, os, time

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.utils.rpc import *

class Wireguard:
	"""Wireguard: manager for wireguard"""

	WG_DOOR_PORT = 51820
	WG_DOOR_IP	 = "192.168.0.254"
	WG_PEER_IP	 = "192.168."
	WG_PEER_MASK = "24"
	CONF_PATH	 = "/etc/wireguard/"

	def __init__(self, server):
		self.server = server
		
		self.privkey = None
		self.pubkey = None
		self.server = None
		self.peers = []
		self.name = "wg-srv"
		self.keyfile = to_root_path("var/key/wireguard.json")
		self.load_keys(FakeClient(ignore_logs=True))

	def load_keys(self):
		if not os.path.isfile(self.keyfile):
			log(ERROR, "Wireguard.load_keys: failed")
			return False

		with open(self.keyfile, "r") as wgkeyfile:
			keys = json.loads(wgkeyfile.read())
			self.privkey = keys["privkey"]
			self.pubkey = keys["pubkey"]

		return True

	def generate_ip(self, dev_id):
		if Wireguard.WG_PEER_MASK == "16":
			return Wireguard.WG_PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)
		elif Wireguard.WG_PEER_MASK=="24":
			return Wireguard.WG_PEER_IP+"0."+str((dev_id%255)+1)
		else:
			return None

	# Set up wireguard interface
	def up(self):
		# Checking current state
		if self.is_up():
			log(WARNING, "Wireguard.up: already up - trying to stop it first")
			if not self.down():
				log(WARNING, "Wireguard.up: failed to stop the wireguard server")
				return False

		# Removing old configuration files
		for old_conf_file in os.listdir(Wireguard.CONF_PATH):
			os.remove(os.path.join(Wireguard.CONF_PATH, old_conf_file))

		# Loading Server Wireguard Keys
		if not self.load_keys(): return False

		# Loading configuration templates
		with open(to_root_path("var/template/wg_srv.txt"), "r") as temp_file:
			template_conf = Template(temp_file.read())
		with open(to_root_path("var/template/wg_peer.txt"), "r") as temp_file:
			template_peer = Template(temp_file.read())

		conf_filename = os.path.join(Wireguard.CONF_PATH, self.name+".conf")

		# Creating configuration
		config = template_conf.substitute({
			"name": self.name,
			"server_privkey": self.privkey,
			"address": Wireguard.WG_DOOR_IP,
			"mask": Wireguard.WG_PEER_MASK,
			"server_port": Wireguard.WG_DOOR_PORT
		})

		for peer in self.peers:
			peer_config = template_peer.substitute({
				"pubkey": peer["key"],
				"address": peer["ip"],
				"mask": "32"
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
	def down(self):
		if not self.is_up():
			log(INFO, "Wireguard.down: already down")
			return None
		else:
			conf_filename = os.path.join(Wireguard.CONF_PATH, self.name+".conf")

			# Run 'wg-quick down'
			cmd = "wg-quick down "+conf_filename
			run(cmd)

			return True

	# Generate wireguard keys
	def keygen(self):
		res = {}

		self.privkey, self.pubkey = Key.key_pair()
		self.privkey = str(self.privkey)
		self.pubkey = str(self.pubkey)

		res["privkey"] = self.privkey
		res["pubkey"]  = self.pubkey

		with open(self.keyfile, "w") as wgkeyfile:
			wgkeyfile.write(json.dumps({"privkey":self.privkey, "pubkey":self.pubkey}))

		return res

	def reset_peers(self):
		self.peers = []

	# Add a wireguard peer
	def add_peer(self, key, dev_id):
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