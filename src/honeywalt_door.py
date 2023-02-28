# External
import argparse, signal

# Internal
from door.controller import DoorController
import glob
from utils.files import *
from utils.firewall import Firewall
from utils.logs import *
from utils.traffic_shaper import TrafficShaper
from utils.wireguard import Wireguard

def handle(signum, frame):
	glob.SERVER.stop()

class DoorServer:
	"""DoorServer"""
	def __init__(self):
		# Getting controller IP
		glob.init(self)
		log(INFO, "DoorServer.__init__: building the firewall manager")
		self.FIREWALL = Firewall()
		log(INFO, "DoorServer.__init__: building the door controller")
		self.DOOR_CONTROLLER = DoorController()
		log(INFO, "DoorServer.__init__: building the traffic shaper")
		self.TRAFFIC_SHAPER = TrafficShaper()
		log(INFO, "DoorServer.__init__: building the wireguard manager")
		self.WIREGUARD = Wireguard()
		signal.signal(signal.SIGINT, handle) # handle ctrl-C
	
	def stop(self):
		log(INFO, "DoorServer.stop: stopping wireguard")
		self.WIREGUARD.down()
		log(INFO, "DoorServer.stop: stopping the traffic shaper")
		self.TRAFFIC_SHAPER.stop()
		log(INFO, "DoorServer.stop: stopping the door controller")
		self.DOOR_CONTROLLER.stop()
		log(INFO, "DoorServer.stop: stopping the firewall")
		self.FIREWALL.down()

	def start(self):
		log(INFO, "DoorServer.start: binding the controller socket")
		self.DOOR_CONTROLLER.connect()
		log(INFO, "DoorServer.start: running the controller")
		self.DOOR_CONTROLLER.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HoneyWalt Door Client: test the door protocol from a command line interface')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	door_server = DoorServer()
	door_server.start()