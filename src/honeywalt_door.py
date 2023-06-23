# External
import argparse, signal

# Internal
from door.controller import DoorController
from tools.cowrie import Cowrie
from tools.firewall import Firewall
from tools.shaper import DoorShaper
from tools.wireguard import Wireguard

from common.utils.logs import *
from common.utils.rpc import *

server = None

def terminate(signume, frame):
	global server
	if server is not None:
		server.stop()

class DoorServer:
	"""DoorServer"""
	def __init__(self):
		log(INFO, "DoorServer: building the cowrie manager")
		self.cowrie = Cowrie(self)
		
		log(INFO, "DoorServer: building the firewall manager")
		self.firewall = Firewall(self)
		
		log(INFO, "DoorServer: building the door controller")
		self.door = DoorController(self)
		
		log(INFO, "DoorServer: building the traffic shaper")
		self.shaper = DoorShaper(self)
		
		log(INFO, "DoorServer: building the wireguard manager")
		self.wireguard = Wireguard(self)
		
		signal.signal(signal.SIGINT, terminate)
		signal.signal(signal.SIGTERM, terminate)
	
	def stop(self):
		fake_client = FakeClient()
		try:
			log(INFO, "DoorServer.stop: stopping wireguard")
			self.wireguard.down(fake_client)
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		try:
			log(INFO, "DoorServer.stop: stopping the traffic shaper")
			self.shaper.stop()
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		try:
			log(INFO, "DoorServer.stop: stopping the door controller")
			self.door.stop()
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

		try:
			log(INFO, "DoorServer.stop: stopping the firewall")
			self.firewall.down(fake_client)
		except Exception as err:
			log(ERROR, "DoorServer.stop:", err)

	def start(self):
		log(INFO, "DoorServer.start: starting the controller")
		self.door.start()

def main():
	global server

	parser = argparse.ArgumentParser(description='HoneyWalt Door Daemon')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	server = DoorServer()
	server.start()

if __name__ == '__main__':
	main()