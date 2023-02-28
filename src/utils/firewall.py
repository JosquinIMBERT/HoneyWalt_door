import glob
from utils.files import *
from utils.logs import *
from utils.system import *

class Firewall:
	"""Firewall: class for the door's firewall"""
	def __init__(self):
		pass

	def up(self, ip):
		run(to_root_path("src/script/firewall-up.sh")+" "+ip)
		return {"success": True}

	def down(self):
		run(to_root_path("src/script/firewall-down.sh"))
		return {"success": True}