

class Firewall:
	"""Firewall: class for the door's firewall"""
	def __init__(self):
		self.state = "Down"

	def up(self):
		# Run src/script/firewall-up.sh
		self.state = "Up"

	def down(self):
		# Run src/script/firewall-down.sh
		self.state = "Down"

	def state(self):
		return self.state