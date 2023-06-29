# External
import os
from string import Template

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.utils.misc import *

class Cowrie:

	SSH_LISTEN_PORT  = 2222 # Traffic from 22 is redirected to 2222 (cowrie can not listen on 22 - missing privileges)
	BACKEND_SSH_PORT = 2000
	BACKEND_SSH_HOST = "127.0.0.1"
	SOCKET_PORTS     = 4000

	def __init__(self, server):
		self.server = server

		self.run_dir       = "/opt/cowrie/honeywalt/"
		os.makedirs(self.run_dir, exist_ok=True)

		self.pid_file      = self.run_dir+"/cowrie.pid"
		self.log_file      = self.run_dir+"/cowrie.log"
		self.json_file     = self.run_dir+"/cowrie.json"
		self.conf_file     = self.run_dir+"/cowrie.conf"
		self.download_path = self.run_dir+"/download/"

		self.conf_template  = ""
		self.start_template = ""

		with open(to_root_path("var/template/cowrie_conf.txt"), "r") as temp_file:
			self.conf_template = Template(temp_file.read())
		with open(to_root_path("var/template/start_cowrie.txt"), "r") as temp_file:
			self.start_template = Template(temp_file.read())

	def __del__(self):
		pass

	# Generate Cowrie Configuration
	def configure(self, honeypot, hpfeeds):
		# Deleting former configuration
		delete_file(self.conf_file)

		params = {
			'download_path'      : self.download_path,
			'listen_port'        : Cowrie.SSH_LISTEN_PORT,
			'backend_host'       : Cowrie.BACKEND_SSH_HOST,
			'backend_port'       : Cowrie.BACKEND_SSH_PORT + int(honeypot["id"]),
			'backend_user'       : honeypot["credentials"]["user"],
			'backend_pass'       : honeypot["credentials"]["pass"],
			'hpfeeds_server'     : hpfeeds["server"],
			'hpfeeds_port'       : hpfeeds["port"],
			'hpfeeds_identifier' : hpfeeds["identifier"],
			'hpfeeds_secret'     : hpfeeds["secret"],
			'logfile'            : self.json_file,
			'socket_port'        : Cowrie.SOCKET_PORTS + int(honeypot["id"])
		}

		content = self.conf_template.substitute(params)

		with open(self.conf_file, "w") as configuration_file:
			configuration_file.write(content)

	# Prepare cowrie to run
	def prepare(self):
		# Delete previous pid file
		delete(self.run_dir, suffix=".pid")

		# Create downloads directory
		os.makedirs(self.download_path, exist_ok=True)

		# Allow cowrie user to access cowrie files
		run("chown -R cowrie:cowrie "+self.run_dir)

	def start(self):
		if self.is_running():
			log(INFO, "Cowrie.start: already running - trying to stop first")
			self.stop()

		self.prepare()

		cmd = self.start_template.substitute({
			"conf_path" : self.conf_file,
			"pid_path"  : self.pid_file,
			"log_path"  : self.log_file
		})

		if not run(cmd):
			log(ERROR, "Cowrie.start: failed")

	def stop(self):
		try:
			kill_from_file(self.pid_file)
		except:
			log(WARNING, "Cowrie.stop: failed - the pid file is: "+str(self.pid_file))
			return False
		else:
			return True

	def is_running(self):
		return read_pid_file(self.pid_file) is not None
