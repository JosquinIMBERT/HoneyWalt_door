# Internal
from common.utils.shaper import Shaper

class DoorShaper(Shaper):
	def __init__(self, server, udp_host="127.0.0.1", udp_port=51820, timeout=60):
		super().__init__(name="DOOR", timeout=timeout)

		self.server = server

		# Where we will connect to with UDP
		self.udp_host = udp_host
		self.udp_port = udp_port
