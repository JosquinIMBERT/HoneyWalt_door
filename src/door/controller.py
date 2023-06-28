# External
import json, ssl, threading
from rpyc.utils.server import ThreadedServer
from rpyc.utils.authenticators import SSLAuthenticator

# Internal
from common.door.proto import *
from common.utils.files import *
from common.utils.logs import *
from common.utils.rpc import AbstractService

class DoorController():
	def __init__(self, server):
		self.server = server

	def __del__(self):
		log(DEBUG, "DoorController: deleting")

	def start(self):
		authenticator = SSLAuthenticator(
			to_root_path("var/key/pki/private/server.key"),
			to_root_path("var/key/pki/server.crt"),
			ca_certs=to_root_path("var/key/pki/ca.crt"),
			cert_reqs=ssl.CERT_REQUIRED,
			ssl_version=ssl.PROTOCOL_TLS
		)
		DoorService = CustomizedDoorService(self.server)
		self.threaded_server = ThreadedServer(DoorService, port=DOOR_PORT, authenticator=authenticator)
		self.service_thread = threading.Thread(target=self.run)
		self.service_thread.start()

	def run(self):
		self.threaded_server.start()

	def stop(self):
		if self.threaded_server is not None: self.threaded_server.close()
		if self.service_thread is not None: self.service_thread.join()



# This function customizes the ClientService class so that it takes the server as a parameter parameter
def CustomizedDoorService(server):
	class DoorService(AbstractService):
		def __init__(self):
			AbstractService.__init__(self)

			self.server = server

		def exposed_firewall_up(self):
			return self.call(self.server.firewall.up, self.remote_ip)

		def exposed_firewall_down(self):
			return self.call(self.server.firewall.down)

		def exposed_wg_keygen(self):
			return self.call(self.server.wireguard.keygen)

		def exposed_wg_up(self):
			return self.call(self.server.wireguard.up)

		def exposed_wg_down(self):
			return self.call(self.server.wireguard.down)

		def exposed_wg_reset(self):
			return self.call(self.server.wireguard.reset_peer)

		def exposed_wg_set_peer(self, pubkey):
			return self.call(self.server.wireguard.set_peer, pubkey)

		def exposed_shaper_up(self):
			self.server.shaper.set_peer(self.conn.root)
			return self.call(self.server.shaper.start)

		def exposed_shaper_down(self):
			return self.call(self.server.shaper.stop)

		def exposed_forward(self, packet):
			return self.call(self.server.shaper.forward, packet)

		def exposed_cowrie_configure(self):
			return self.call(self.server.cowrie.configure, self.server.config["honeypot"], self.server.config["hpfeeds"])

		def exposed_cowrie_start(self):
			return self.call(self.server.cowrie.start)

		def exposed_cowrie_stop(self):
			return self.call(self.server.cowrie.stop)

		def exposed_cowrie_is_running(self):
			return self.call(self.server.cowrie.is_running)

		def exposed_set_config(self, config):
			self.server.config = json.loads(config)

		def exposed_commit(self):
			return self.call(self.server.store_config)
	
	return DoorService