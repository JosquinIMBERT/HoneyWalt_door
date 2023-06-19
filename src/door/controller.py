# External
import ssl
from rpyc.utils.server import ThreadedServer
from rpyc.utils.authenticators import SSLAuthenticator

# Internal
import glob
from common.door.proto import *
from common.utils.files import *
from common.utils.logs import *
from common.utils.rpc import AbstractService

class DoorController():
	def __init__(self):
		log(INFO, "Creating the DoorController")

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
		self.service_thread = ThreadedServer(DoorService, port=DOOR_PORT, authenticator=authenticator)
		self.service_thread.start()

	def stop(self):
		self.service_thread.close()



class DoorService(AbstractService):
	def __init__(self):
		AbstractService.__init__(self)

	def exposed_firewall_up(self):
		return self.call(glob.SERVER.FIREWALL.up, self.remote_ip)

	def exposed_firewall_down(self):
		return self.call(glob.SERVER.FIREWALL.down)

	def exposed_wg_keygen(self):
		return self.call(glob.SERVER.WIREGUARD.keygen)

	def exposed_wg_up(self):
		return self.call(glob.SERVER.WIREGUARD.up)

	def exposed_wg_down(self):
		return self.call(glob.SERVER.WIREGUARD.down)

	def exposed_wg_reset(self):
		return self.call(glob.SERVER.WIREGUARD.reset_peers)

	def exposed_wg_add_peer(self, pubkey, ident):
		return self.call(glob.SERVER.WIREGUARD.add_peer, pubkey, ident)

	def exposed_traffic_shaper_up(self):
		glob.SERVER.TRAFFIC_SHAPER.set_peer(self.conn.root)
		return self.call(glob.SERVER.TRAFFIC_SHAPER.start)

	def exposed_traffic_shaper_down(self):
		return self.call(glob.SERVER.TRAFFIC_SHAPER.stop)

	def exposed_forward_wg_packet(self, packet):
		return self.call(glob.SERVER.TRAFFIC_SHAPER.forward, packet)