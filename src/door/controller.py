# External
import ssl, threading
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
		log(INFO, "Deleting the DoorController")

	def start(self):
		authenticator = SSLAuthenticator(
			to_root_path("var/key/pki/private/server.key"),
			to_root_path("var/key/pki/server.crt"),
			ca_certs=to_root_path("var/key/pki/ca.crt"),
			cert_reqs=ssl.CERT_REQUIRED,
			ssl_version=ssl.PROTOCOL_TLS
		)
		self.threaded_server = ThreadedServer(DoorService, port=DOOR_PORT, authenticator=authenticator)
		self.service_thread = threading.Thread(target=self.run)
		self.service_thread.start()

	def run(self):
		self.threaded_server.start()

	def stop(self):
		if self.threaded_server is not None: self.threaded_server.close()
		if self.service_thread is not None: self.service_thread.join()



class DoorService(AbstractService):
	def __init__(self):
		AbstractService.__init__(self)

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
		return self.call(self.server.wireguard.reset_peers)

	def exposed_wg_add_peer(self, pubkey, ident):
		return self.call(self.server.wireguard.add_peer, pubkey, ident)

	def exposed_traffic_shaper_up(self):
		self.server.shaper.set_peer(self.conn.root)
		return self.call(self.server.shaper.start, ignore_client=True)

	def exposed_traffic_shaper_down(self):
		return self.call(self.server.shaper.stop, ignore_client=True)

	def exposed_forward(self, packet):
		return self.call(self.server.shaper.forward, packet, ignore_client=True)

	def exposed_cowrie_configure(self):
		return self.call(self.server.cowrie.configure) #TODO: add parameters

	def exposed_cowrie_start(self):
		return self.call(self.server.cowrie.start)

	def exposed_cowrie_stop(self):
		return self.call(self.server.cowrie.stop)

	def exposed_cowrie_is_running(self):
		return self.call(self.server.cowrie.is_running)