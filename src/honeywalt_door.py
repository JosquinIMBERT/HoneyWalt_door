import signal

from door.controller import DoorController
import glob
from utils.files import *
from utils.firewall import Firewall
from utils.traffic_shaper import TrafficShaper
from utils.wireguard import Wireguard

def handle(signum, frame):
	glob.SERVER.stop()

class DoorServer:
	"""DoorServer"""
	def __init__(self):
		# Getting controller IP
		with to_root_path("var/controller.ip") as ip_file:
			controller_ip = ip_file.read()
		glob.init(controller_ip, self)
		self.FIREWALL = Firewall()
		self.DOOR_CONTROLLER = DoorController()
		self.TRAFFIC_SHAPER = TrafficShaper()
		self.WIREGUARD = Wireguard()
		signal.signal(signal.SIGINT, handle) # handle ctrl-C
	
	def stop(self):
		self.WIREGUARD.down()
		self.TRAFFIC_SHAPER.stop()
		self.DOOR_CONTROLLER.stop()
		self.FIREWALL.down()

	def start(self):
		self.DOOR_CONTROLLER.start()

if __name__ == '__main__':
	door_server = DoorServer()
	door_server.start()