def run(cmd, check=False, output=False, timeout=False):
	log.command(cmd)
	res = subprocess.run(
		command,
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