import socket, threading

import glob
from utils import *

def door_socket_listen(door_sock):
	door_sock.listen()

class DoorSocket:
	"""DoorSocket: server socket to communicate with controller"""
	def __init__(self):
		self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_sock.bind((glob.CONTROLLER_IP, glob.CONTROL_PORT))
		self.sock = None

	def __del__(self):
		if self.sock is not None:
			self.sock.close()
		self.listen_sock.close()

	def start(self):
		self.keep_running = True
		self.listen_thread = threading.Thread(target=door_socket_listen, args=(self,), daemon=True)
		self.listen_thread.start()

	def stop(self):
		self.keep_running = False
		self.listen_thread.join()

	def listen(self):
		self.listen_sock.listen(1)
		while self.keep_running:
			try:
				self.sock, addr = self.listen_sock.accept()
				self.run()
			except:
				log.info("door socket lost connection to controller")
		log.info("door socket listening thread was interrupted")
	
	def run(self):
		while self.keep_running:
			instruction = self.recv()
			if instruction is None:
				break
			self.exec(instruction)

	def exec(self, instruction):
		if instruction=="wg_getkey":
			key = glob.WG.get_pubkey()
			self.send(keys)
		elif instruction=="wg_set_vmpubkey":
			vm_pubkey = self.recv()
			glob.WG.set_vm_pubkey(vm_pubkey)
		elif instruction=="wg_client_add":
			client_info = self.recv()
			glob.WG.client_add(client_info)
		elif instruction=="wg_client_rm":
			client_info = self.recv()
			glob.WG.client_rm(client_info)
		elif instruction=="still_alive":
			self.send("1")
		else:
			log.error("door socket received invalid instruction")

	def send(self, string):
		self.sock.sendall(string)

	def recv(self):
		try:
			return self.sock.readline()
		except:
			return None