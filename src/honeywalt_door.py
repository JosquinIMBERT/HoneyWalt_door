# External
import argparse, signal, sys, threading

# Internal
from door.controller import DoorController
import glob
from tools.firewall import Firewall
from tools.traffic_shaper import TrafficShaper
from tools.wireguard import Wireguard
from utils.files import *
from utils.logs import *

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
		signal.signal(signal.SIGINT, signal.SIG_IGN) # ignore interrupts
	
	def stop(self):
		try:
			log(INFO, "DoorServer.stop: stopping wireguard")
			self.WIREGUARD.down()
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		try:
			log(INFO, "DoorServer.stop: stopping the traffic shaper")
			self.TRAFFIC_SHAPER.stop()
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		try:
			log(INFO, "DoorServer.stop: stopping the door controller")
			self.DOOR_CONTROLLER.stop()
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		try:
			log(INFO, "DoorServer.stop: stopping the firewall")
			self.FIREWALL.down()
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		sys.exit(0)


	def start(self):
		log(INFO, "DoorServer.start: binding the controller socket")
		self.DOOR_CONTROLLER.connect()
		log(INFO, "DoorServer.start: running the controller")
		self.DOOR_CONTROLLER.run()
		log(INFO, "DoorServer.start: left main control loop. stopping the server")
		self.stop()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HoneyWalt Door Client: test the door protocol from a command line interface')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	threading.current_thread().name = "MainThread"

	door_server = DoorServer()
	door_server.start()