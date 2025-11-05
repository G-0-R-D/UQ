
from os import (
	stat as os_stat,
	)

def snap_path_changed(SRCPATH, DESTPATH):
	# just compare times, not sizes
	try:
		src_stat = os_stat(SRCPATH)
		dest_stat = os_stat(DESTPATH)
		# use int() in case device isn't decimal accurate
		return (int(src_stat.st_mtime) != int(dest_stat.st_mtime)) or (int(src_stat.st_size) != int(dest_stat.st_size))
	except OSError:
		return True

def build(ENV):
	ENV.snap_path_changed = snap_path_changed

def main(ENV):
	ENV.snap_test_out(snap_path_changed(__file__, __file__) == False)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

