# External
import signal, threading

# Internal
from common.door.proto import *
from common.utils.controller import Controller
from common.utils.logs import *
from common.utils.sockets import ServerSocket
import glob

class DoorController(Controller):
	def __init__(self):
		self.socket = ServerSocket(DOOR_PORT)
		self.socket.set_name("Socket(Door-Controller)")
		self.keep_running = False

	def __del__(self):
		del self.socket

	def connect(self):
		self.socket.bind()

	def stop(self):
		self.keep_running = False

	def handler(self, signum, frame):
		log(DEBUG, "DoorController.handler: "+threading.current_thread().name)
		self.keep_running = False
		raise KeyboardInterrupt

	def run(self):
		self.keep_running = True
		while self.keep_running:
			signal.signal(signal.SIGINT, self.handler)
			accepted = self.socket.accept()
			signal.signal(signal.SIGINT, signal.SIG_IGN)
			if accepted:
				disconnected = False
				while self.keep_running and not disconnected:
					cmd = self.socket.recv_cmd()
					if not cmd:
						disconnected = True
					else:
						self.execute(cmd)
				if disconnected:
					log(INFO, "DoorController.run: Client disconnected")

	def execute(self, cmd):
		if cmd == CMD_DOOR_FIREWALL_UP:
			log(INFO, "DoorController.execute: setting firewall up")
			self.exec(glob.SERVER.FIREWALL.up, self.socket.remaddr[0])
		elif cmd == CMD_DOOR_FIREWALL_DOWN:
			log(INFO, "DoorController.execute: setting firewall down")
			self.exec(glob.SERVER.FIREWALL.down)
		elif cmd == CMD_DOOR_WG_KEYGEN:
			log(INFO, "DoorController.execute: generating wireguard keys")
			self.exec(glob.SERVER.WIREGUARD.keygen)
		elif cmd == CMD_DOOR_WG_UP:
			log(INFO, "DoorController.execute: setting wireguard up")
			self.exec(glob.SERVER.WIREGUARD.up)
		elif cmd == CMD_DOOR_WG_DOWN:
			log(INFO, "DoorController.execute: setting wireguard down")
			self.exec(glob.SERVER.WIREGUARD.down)
		elif cmd == CMD_DOOR_WG_ADD_PEER:
			log(INFO, "DoorController.execute: adding wireguard peer")
			args = self.socket.recv_obj()
			self.exec(glob.SERVER.WIREGUARD.add_peer, args["pubkey"], args["id"])
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_UP:
			log(INFO, "DoorController.execute: setting traffic shaper up")
			self.exec(glob.SERVER.TRAFFIC_SHAPER.up)
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_DOWN:
			log(INFO, "DoorController.execute: setting traffic shaper down")
			self.exec(glob.SERVER.TRAFFIC_SHAPER.down)
		elif cmd == CMD_DOOR_LIVE:
			log(INFO, "DoorController.execute: answering LIVE query")
			self.socket.send_obj({"success": True})
		else:
			log(WARNING, "DoorController.execute: received invalid command")
			res = {"success": False, ERROR: ["unknown command"]}
			self.socket.send_obj(res)