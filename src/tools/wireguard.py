from utils import *

class Wireguard:
	"""Wireguard: manager for wireguard"""
	def __init__(self):
		self.findkeys()
		self.state = "Down"

	def up(self):
		if self.state=="Up":
			self.down()
		if path.exists("/etc/wireguard/wg.conf"):
			cmd.run("wg-quick up wg")
			self.state = "Up"
		else:
			log.warn("failed to start wg, no configuration found")

	def down(self):
		if path.exists("/etc/wireguard/wg.conf"):
			cmd.run("wg-quick down wg")
			self.state = "Down"
		else:
			log.warn("failed to stop wg, no configuration found")

	def genconf(self):
		wg_temp_path = path.to_root("var/template/wg-server.txt")
		with open(wg_temp_path, "r") as wg_temp_file:
			wg_temp = wg_temp_file.read()
			conf = wg_temp.substitute({
				"privkey": str(self.privkey),
				"port": glob.WG_PORT,
				"vm_pubkey": self.vm_pubkey
			})

		conf_path = path.to_root("/etc/wireguard/wg.conf")
		with open(conf_path, "w") as conf_file:
			conf_file.write(conf)

	def findkeys(self):
		privkey_path = path.to_root("var/wg/privkey")
		pubkey_path = path.to_root("var/wg/pubkey")
		vmpubkey_path = path.to_root("var/wg/vmpubkey")
		
		if path.exists(privkey_path):
			with open(privkey_path, "r") as privkey_file:
				self.privkey = privkey_file.read()
		if path.exists(pubkey_path):
			with open(pubkey_path, "r") as pubkey_file:
				self.pubkey = pubkey_file.read()
		if path.exists(vmpubkey_path):
			with open(vmpubkey_path, "r") as vmpubkey_file:
				self.vm_pubkey = vmpubkey_file.read()

		if self.privkey is None
			or self.pubkey is None 
			or self.privkey==""
			or self.pubkey=="":
			self.genkeys()

	def genkeys(self):
		command = path.to_root("src/script/wg-genkeys.sh")+" "+path.to_root("var/wg/")
		keys = cmd.run(command, output=True)
		self.privkey = keys.split(" ", 1)[0]
		self.pubkey = keys.split(" ", 1)[1]

	def get_pubkey(self):
		return str(self.pubkey)

	def set_vm_pubkey(self, key):
		if self.vm_pubkey is None or key != self.vm_pubkey:
			self.vm_pubkey = key
			with open(path.to_root("var/wg/vmpubkey"), "w") as vmpubkey_file:
				vmpubkey_file.write(str(self.vm_pubkey))
			self.genconf()
			self.up()

	def client_add(self, client):
		pass

	def client_rm(self, client):
		pass