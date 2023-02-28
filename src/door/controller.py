# Internal
from door.proto import *
from door.sock import *
import glob
from utils.controller import Controller

class DoorController(Controller):
	def __init__(self):
		self.socket = DoorSocket()
		self.keep_running = False

	def __del__(self):
		del self.socket

	def connect(self):
		self.socket.connect()

	def run(self):
		self.keep_running = True
		while self.keep_running:
			if self.socket.accept():
				while self.keep_running:
					cmd = self.socket.recv_cmd()
					self.execute(cmd)

	def execute(self, cmd):
		if cmd == CMD_DOOR_FIREWALL_UP:
			ip = str(self.socket.recv_obj())
			self.exec(glob.SERVER.FIREWALL.up, ip)
		elif cmd == CMD_DOOR_FIREWALL_DOWN:
			self.exec(glob.SERVER.FIREWALL.down)
		elif cmd == CMD_DOOR_WG_KEYGEN:
			self.exec(glob.SERVER.WIREGUARD.keygen)
		elif cmd == CMD_DOOR_WG_UP:
			self.exec(glob.SERVER.WIREGUARD.up)
		elif cmd == CMD_DOOR_WG_DOWN:
			self.exec(glob.SERVER.WIREGUARD.down)
		elif cmd == CMD_DOOR_WG_ADD_PEER:
			args = self.socket.recv_obj()
			self.exec(glob.SERVER.WIREGUARD.add_peer, args["pubkey"], args["id"])
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_UP:
			self.exec(glob.SERVER.TRAFFIC_SHAPER.up)
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_DOWN:
			self.exec(glob.SERVER.TRAFFIC_SHAPER.down)
		elif cmd == CMD_DOOR_LIVE:
			self.socket.send_obj({"success": True})
		else:
			res = {"success": False, "error": ["unknown command"]}
			self.socket.send_obj(res)