# External
import select, socket, sys, threading

if __name__ == "__main__":
	sys.path[0] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Internal
from common.utils.logs import *
import glob

def encode_len(bytes_obj):
	return len(bytes_obj).to_bytes(2, "big")

def decode_len(length):
	return int.from_bytes(length, "big")

def traffic_shaper_listen(traffic_shaper):
	traffic_shaper.listen()

class TrafficShaper:
	"""TrafficShaper: shape UDP traffic into TCP traffic"""
	def __init__(self, udp_host="127.0.0.1", udp_port=51820, tcp_host="0.0.0.0", tcp_port=51819):
		self.udp_host=udp_host
		self.udp_port=udp_port
		self.tcp_host=tcp_host
		self.tcp_port=tcp_port
		self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_sock.bind((self.tcp_host, self.tcp_port))
		self.tcp_sock = None
		self.udp_sock = None
		self.listen_thread = None

	def __del__(self):
		if self.tcp_sock is not None:
			self.tcp_sock.close()
		if self.udp_sock is not None:
			self.udp_sock.close()
		self.listen_sock.close()

	def up(self, client):
		self.keep_running = True
		self.listen_sock.settimeout(5)
		self.listen_thread = threading.Thread(target=traffic_shaper_listen, args=(self,), daemon=True)
		self.listen_thread.start()

	def down(self, client):
		self.keep_running = False
		if self.listen_thread is not None:
			self.listen_thread.join()

	def wait(self):
		self.listen_thread.join()
		
	def listen(self):
		self.listen_sock.listen(1)
		while self.keep_running:
			try:
				self.tcp_sock, addr = self.listen_sock.accept()
				self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				self.run()
			except socket.timeout:
				pass
			except Exception as err:
				log(INFO, "TrafficShaper.listen: an unknown error occured when waiting for the controller to connect")
				log(ERROR, err)
			else:
				log(INFO, "TrafficShaper.listen: door socket listening thread was interrupted")

	def run(self):
		sel_list = [self.udp_sock, self.tcp_sock]
		try:
			connected = True
			while self.keep_running and connected:
				rready, _, _ = select.select(sel_list, [], [])
				for ready in rready:
					if ready is self.udp_sock:
						if not self.recv_udp():
							connected = False
							break
					elif ready is self.tcp_sock:
						if not self.recv_tcp():
							connected = False
							break
					else:
						log(ERROR, "TrafficShaper.run: Select returned while no socket is ready")
						connected = False
						break
		except ConnectionResetError:
			log(WARNING, "TrafficShaper.run: traffic shaper connection reset")

	def recv_udp(self):
		msg, addr = self.udp_sock.recvfrom(1024)
		if not msg:
			return False

		msg = encode_len(msg) + msg
		self.tcp_sock.sendall(msg)
		
		return True

	def recv_tcp(self):
		msg = self.tcp_sock.recv(1024)
		if not msg:
			return False
		
		while msg:
			blen, msg = msg[0:2], msg[2:]
			length = decode_len(blen)
			if length>len(msg):
				return False
			to_send, msg = msg[:length], msg[length:]
			self.udp_sock.sendto(to_send, (self.udp_host, self.udp_port))
		
		return True

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Run the door's TrafficShaper")
	parser.add_argument("-uh", "--udp-host", nargs=1, help="UDP Host to connect to", default=["127.0.0.1"])
	parser.add_argument("-up", "--udp-port", nargs=1, help="UDP Port to connect to", default=[51820])
	parser.add_argument("-th", "--tcp-host", nargs=1, help="TCP Host to listen on",  default=["0.0.0.0"])
	parser.add_argument("-tp", "--tcp-port", nargs=1, help="TCP Port to listen on",  default=[51819])

	options = parser.parse_args()
	udp_host = options.udp_host[0]
	udp_port = options.udp_port[0]
	tcp_host = options.tcp_host[0]
	tcp_port = options.tcp_port[0]

	print("Running TrafficShaper with:")
	print("  - udp_host=", udp_host)
	print("  - udp_port=", udp_port)
	print("  - tcp_host=", tcp_host)
	print("  - tcp_port=", tcp_port)

	ts = TrafficShaper(udp_host=udp_host, udp_port=udp_port, tcp_host=tcp_host, tcp_port=tcp_port)
	ts.up(sys)
	ts.wait()
	del ts