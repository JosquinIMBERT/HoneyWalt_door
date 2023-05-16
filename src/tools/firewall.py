import glob
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

class Firewall:
	"""Firewall: class for the door's firewall"""
	def __init__(self):
		pass

	def up(self, client, ip):
		if not run(to_root_path("src/script/firewall-up.sh")+" "+ip):
			log(WARNING, "Firewall.up: failed to start firewall")
			return {"success": False}
		else:
			return {"success": True}

	def down(self, client):
		if not run(to_root_path("src/script/firewall-down.sh")):
			log(WARNING, "Firewall.down: failed to stop firewall")
			return {"success": False}
		else:
			return {"success": True}