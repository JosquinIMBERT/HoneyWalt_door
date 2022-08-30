import signal

import glob
from tools import *
from utils import *

def handle(signum, frame):
	glob.SERVER.stop()

class DoorServer:
	"""DoorServer"""
	def __init__(self):
		# Getting controller IP
		with path.to_root("var/controller.ip") as ip_file:
			controller_ip = ip_file.read()
		glob.init(controller_ip, self)
		glob.FW = firewall.Firewall()
		glob.DOORSOCK = door_socket.DoorSocket()
		glob.TSHAPER = traffic_shaper.TrafficShaper()
		glob.WG = wireguard.Wireguard()
		signal.signal(signal.SIGINT, handle) # handle ctrl-C
	
	def stop(self):
		glob.WG.down()
		glob.TSHAPER.stop()
		glob.DOORSOCK.stop()
		glob.FW.down()

	def start(self):
		glob.FW.up()
		glob.DOORSOCK.start()
		glob.TSHAPER.start()
		glob.WG.up()

if __name__ == '__main__':
	door_server = DoorServer()
	door_server.start()