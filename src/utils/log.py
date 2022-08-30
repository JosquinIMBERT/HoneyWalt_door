def command(msg):
	log(glob.CMD, msg)

def debug(msg):
	log(glob.DEB, msg)

def info(msg):
	log(glob.INFO, msg)

def warn(msg):
	log(glob.WARN, msg)

def error(msg):
	log(glob.ERROR, msg)

def fatal(msg):
	log(glob.FATAL, msg)


def log(level, msg):
	pass