from os.path import abspath, dirname, exists, join

# Get the path to the root of the application
def get_root():
	path = abspath(dirname(__file__))
	return "/".join(path.split("/")[:-1])

def to_root(path):
	root_path = get_root()
	return join(root_path, path)

def exists(path):
	return exists(path)