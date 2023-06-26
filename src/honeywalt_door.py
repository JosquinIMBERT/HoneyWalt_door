# External
import argparse, json, signal

# Internal
from door.controller import DoorController
from tools.cowrie import Cowrie
from tools.firewall import Firewall
from tools.shaper import DoorShaper
from tools.wireguard import Wireguard

from common.utils.files import *
from common.utils.logs import *

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

		self.user_conf_file = to_root_path("etc/honeywalt_door.cfg")
		self.dist_conf_file = to_root_path("etc/honeywalt_door.cfg.dist")
		self.config = {}

		signal.signal(signal.SIGINT, terminate)
		signal.signal(signal.SIGTERM, terminate)

	def load_config(self):
		if isfile(self.user_conf_file):
			with open(self.user_conf_file, "r") as configuration_file:
				self.config = json.loads(configuration_file.read())
		else:
			with open(self.dist_conf_file, "r") as configuration_file:
				self.config = json.loads(configuration_file.read())

	def store_config(self):
		with open(self.user_conf_file, "w") as configuration_file:
			configuration_file.write(json.dumps(self.config))

	def stop(self):
		try:
			log(INFO, "DoorServer.stop: stopping wireguard")
			self.wireguard.down()
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
			self.firewall.down()
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