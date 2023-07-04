from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

class Firewall:
	"""Firewall: class for the door's firewall"""
	def __init__(self, server, ip_white_list=[]):
		self.server = server
		self.ip_white_list = ip_white_list

	def up(self, ip):
		white_list = ",".join(self.ip_white_list)
		if not run(to_root_path("src/script/firewall-up.sh")+" "+str(ip)+" "+str(white_list)):
			log(WARNING, "Firewall.up: failed to start firewall")
			return False
		else:
			return True

	def down(self):
		if not run(to_root_path("src/script/firewall-down.sh")):
			log(WARNING, "Firewall.down: failed to stop firewall")
			return False
		else:
			return True