# External
import socket, time

# Internal
from utils.logs import *
from utils.sockets import *
from door.proto import *

class DoorSocket(ProtoSocket):
	def __init__(self):
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket = None
		self.addr = None

	def __del__(self):
		if self.socket is not None:
			self.socket.close()
		if self.listen_socket is not None:
			self.listen_socket.close()

	def connect(self):
		try:
			self.listen_socket.bind(("", DOOR_PORT))
		except:
			log(ERROR, self.name()+".connect: failed to bind socket")
			return False
		self.listen_socket.listen(1)
		return True

	def accept(self):
		try:
			self.socket, self.addr = self.listen_socket.accept()
		except Exception as err:
			log(ERROR, self.name()+".accept: an error occured when waiting for controller connection")
			log(ERROR, self.name()+".accept:", err)
			return False
		else:
			return True