
def gdbinit_files():

	def gen1():
		# this goes in build directory (build/.gdbinit)

		yield '\n'
		yield '# https://www.cse.unsw.edu.au/~learn/debugging/modules/gdb_init_file/\n'
		yield '# https://stackoverflow.com/questions/4845617/how-to-make-gdb-send-an-external-notification-on-receiving-a-signal\n\n'

		yield '# in home directory create .gdbinit file with "set auto-load safe-path /" at the top\n\n'

		yield '# then make sure this is in the directory gdb is being called from (same as run.sh)\n\n'

		yield 'set $_exitcode = -999\n'
		yield '#handle SIGTERM nostop print pass\n'
		yield '#handle SIGPIPE nostop\n'
		yield 'define hook-stop\n'
		yield '\t#if $_exitcode != -999\n'
		yield '\tquit\n'
		yield '\t#end\n'
		yield 'end\n'
		yield 'run\n'

	def gen2():
		# this one goes in project directory (next to executable) as .gdbinit:
		##gdb -ex=run ./build/libsnap
		#gdb -silent ./build/libsnap)

		yield '\n'
		yield 'set $_exitcode = -999\n'
		yield 'handle SIGTERM nostop print pass\n'
		yield 'handle SIGPIPE nostop\n'
		yield 'define hook-stop\n'
		yield '\tif $_exitcode == -999\n'
		yield '\t\tset filename-display basename\n'
		yield '\t\tprint (void) SnapNode_PRINT_DEBUG_INFO()\n'
		yield '\t\tbt 6\n'
		yield '\tend\n'
		yield '\tquit\n'
		yield 'end\n'
		yield 'echo .gdbinit: running app\n'
		yield 'run\n'

	return [
		dict(filepath='build/.gdbinit', file_contents=''.join(gen1()),
		dict(filepath='.gdbinit', file_contents=''.join(gen2()),
	]


