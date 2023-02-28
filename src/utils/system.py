# External
import subprocess

# Internal
from utils.logs import *

def run(cmd, check=False, output=False, timeout=False):
	log(COMMAND, cmd)
	res = subprocess.run(
		cmd,
		shell=True,
		check=check,
		text=True,
		capture_output=output,
		timeout=timeout
	)
	if output:
		return str(res.stdout)
	else:
		return res.returncode == 0