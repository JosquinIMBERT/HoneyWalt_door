def init(controller_ip, door_server):
	global CONTROLLER_IP, CONTROL_PORT, TRAFFIC_PORT, WG_PORT

	global FW, DOORSOCK, TSHAPER, WG, SERVER

	CONTROLLER_IP = controller_ip
	CONTROL_PORT = 5555
	TRAFFIC_PORT = 51819
	WG_PORT = 51820
	FW = None
	DOORSOCK = None
	TSHAPER = None
	WG = None
	SERVER = door_server