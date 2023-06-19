# External
import argparse, signal, sys, threading

# Internal
from door.controller import DoorController
import glob
from tools.firewall import Firewall
from tools.traffic_shaper import DoorShaper
from tools.wireguard import Wireguard
from common.utils.files import *
from common.utils.logs import *
from common.utils.rpc import *

def terminate(signume, frame):
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
		self.TRAFFIC_SHAPER = DoorShaper()
		log(INFO, "DoorServer.__init__: building the wireguard manager")
		self.WIREGUARD = Wireguard()
		signal.signal(signal.SIGINT, terminate)
		signal.signal(signal.SIGTERM, terminate)
	
	def stop(self):
		fake_client = FakeClient()
		try:
			log(INFO, "DoorServer.stop: stopping wireguard")
			self.WIREGUARD.down(fake_client)
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
			self.FIREWALL.down(fake_client)
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		sys.exit(0)


	def start(self):
		log(INFO, "DoorServer.start: starting the controller")
		self.DOOR_CONTROLLER.start()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HoneyWalt Door Daemon')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	#threading.current_thread().name = "MainThread"

	door_server = DoorServer()
	door_server.start()