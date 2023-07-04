# External
import argparse, json, os, signal

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
	def __init__(self, ip_white_list=[]):
		log(INFO, "DoorServer: building the cowrie manager")
		self.cowrie = Cowrie(self)

		log(INFO, "DoorServer: building the firewall manager")
		self.firewall = Firewall(self, ip_white_list=ip_white_list)

		log(INFO, "DoorServer: building the door controller")
		self.door = DoorController(self)

		log(INFO, "DoorServer: building the traffic shaper")
		self.shaper = DoorShaper(self)

		log(INFO, "DoorServer: building the wireguard manager")
		self.wireguard = Wireguard(self)

		self.user_conf_file = to_root_path("etc/honeywalt_door.cfg")
		self.dist_conf_file = to_root_path("etc/honeywalt_door.cfg.dist")
		self.config = {}
		self.load_config()

		signal.signal(signal.SIGINT, terminate)
		signal.signal(signal.SIGTERM, terminate)

	def load_config(self):
		configuration_filename = self.user_conf_file if isfile(self.user_conf_file) else self.dist_conf_file
		with open(configuration_filename, "r") as configuration_file:
			self.config = json.loads(configuration_file.read())

	def store_config(self):
		with open(self.user_conf_file, "w") as configuration_file:
			configuration_file.write(json.dumps(self.config, indent=4))

	def set_config(self, config):
		self.config = json.loads(config)

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
	parser.add_argument("-p", "--pid-file", nargs=1, help="Select a PID file")
	parser.add_argument("-w", "--ip-white-list", nargs=1, help="Select IPs to accept SSH connections from")

	options = parser.parse_args()

	# Log Level
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	# PID file
	if options.pid_file is not None:
		pid_file_path = options.pid_file[0]
		from pathlib import Path
		path = Path(pid_file_path)
		if path.parent.exists():
			with open(pid_file_path, "w") as pid_file:
				pid_file.write(str(os.getpid()))

	# IP White List (from arguments)
	args_ips = []
	if options.ip_white_list is not None:
		args_ips = options.ip_white_list[0].split(",")

	# IP White List (from file)
	file_ips = []
	white_list_filepath = to_root_path("etc/whitelist.txt")
	if isfile(white_list_filepath):
		with open(white_list_filepath, "r") as white_list_file:
			file_ips = white_list_file.read().strip().split(",")

	# IP White List (final)
	ip_white_list = args_ips + file_ips

	server = DoorServer(ip_white_list=ip_white_list)
	server.start()

if __name__ == '__main__':
	main()