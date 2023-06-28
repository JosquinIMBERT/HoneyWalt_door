# External
from python_wireguard import ClientConnection, Key, Server, wireguard
from string import Template
import json, sys, os, time

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

class Wireguard:
	"""Wireguard: manager for wireguard"""

	DOOR_PORT = 51820
	DOOR_IP	 = "192.168.0.254"
	PEER_IP	 = "192.168."
	PEER_MASK = "24"
	CONF_PATH	 = "/etc/wireguard/"

	def __init__(self, server):
		self.server = server
		
		self.privkey = None
		self.pubkey = None
		self.peer = None
		self.name = "wg-srv"

	def load_keys(self):
		self.privkey = self.server.config["honeypot"]["door"]["privkey"]
		self.pubkey = self.server.config["honeypot"]["door"]["pubkey"]

	def generate_ip(self, dev_id):
		if Wireguard.PEER_MASK == "16":
			return Wireguard.PEER_IP+str(dev_id//255)+"."+str((dev_id%255)+1)
		elif Wireguard.PEER_MASK=="24":
			return Wireguard.PEER_IP+"0."+str((dev_id%255)+1)
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
		self.load_keys()

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
			"address": Wireguard.DOOR_IP,
			"mask": Wireguard.PEER_MASK,
			"server_port": Wireguard.DOOR_PORT
		})

		peer_config = template_peer.substitute({
			"pubkey": self.peer["key"],
			"address": self.peer["ip"],
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

		self.server.config["honeypot"]["door"]["privkey"] = self.privkey
		self.server.config["honeypot"]["door"]["pubkey"] = self.pubkey

		return res

	def reset_peer(self):
		self.peer = None

	# Add a wireguard peer
	def set_peer(self, key):
		self.peer = {
			"key":key,
			"ip": self.generate_ip(self.server.config["honeypot"]["id"])
		}
		self.server.config["honeypot"]["device"]["pubkey"] = key
		return True

	def is_up(self):
		# The wireguard library does not allow to check which devices are up
		# (Note: there is a wireguard.list_devices function but it prints the result to stdout instead of returning it)
		res = run("wg show interfaces", output=True)
		return self.name in res.split()