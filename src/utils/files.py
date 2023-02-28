import os
from os.path import abspath, dirname, exists, join

# Get the path to the root of the application
def get_root_path():
	#path = abspath(dirname(__file__))
	#return "/".join(path.split("/")[:-1])
	return os.environ["HONEYWALT_DOOR_HOME"]

def to_root_path(path):
	root_path = get_root_path()
	return join(root_path, path)

def delete(directory, suffix=""):
	for name in os.listdir(directory):
		file = os.path.join(directory,name)
		if file.endswith(suffix):
			os.remove(file)

def exists(path):
	return exists(path)