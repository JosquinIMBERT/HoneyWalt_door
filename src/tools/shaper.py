# External
import os, select, socket, sys, threading

# Internal
from common.utils.logs import *
from common.utils.rpc import *
from common.utils.shaper import Shaper
import glob

class DoorShaper(Shaper):
	def __init__(self, udp_host="127.0.0.1", udp_port=51820, timeout=60):
		super().__init__(name="DOOR", timeout=timeout)

		# Where we will connect to with UDP
		self.udp_host = udp_host
		self.udp_port = udp_port
