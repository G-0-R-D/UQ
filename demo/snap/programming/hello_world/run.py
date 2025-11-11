
import os
THISDIR = os.path.realpath(os.path.dirname(__file__))

"""
for ins in dis.get_instructions(data):
	print(ins.opname, ins.arg, ins.argval, ins.offset, ins.positions)

a.py:
RESUME 0 0 0 Positions(lineno=0, end_lineno=1, col_offset=0, end_col_offset=0)
LOAD_CONST 0 <code object from_python at 0x7fe79b2116f0, file "<disassembly>", line 2> 2 Positions(lineno=2, end_lineno=3, col_offset=0, end_col_offset=39)
MAKE_FUNCTION 0 0 4 Positions(lineno=2, end_lineno=3, col_offset=0, end_col_offset=39)
STORE_NAME 0 from_python 6 Positions(lineno=2, end_lineno=3, col_offset=0, end_col_offset=39)
RETURN_CONST 1 None 8 Positions(lineno=2, end_lineno=3, col_offset=0, end_col_offset=39)

main.py:
RESUME 0 0 0 Positions(lineno=0, end_lineno=1, col_offset=0, end_col_offset=0)
LOAD_CONST 0 0 2 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
LOAD_CONST 1 None 4 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
IMPORT_NAME 0 a 6 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
STORE_NAME 0 a 8 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
LOAD_CONST 0 0 10 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
LOAD_CONST 1 None 12 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
IMPORT_NAME 1 b 14 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
STORE_NAME 1 b 16 Positions(lineno=2, end_lineno=2, col_offset=0, end_col_offset=11)
PUSH_NULL None None 18 Positions(lineno=4, end_lineno=4, col_offset=0, end_col_offset=13)
LOAD_NAME 0 a 20 Positions(lineno=4, end_lineno=4, col_offset=0, end_col_offset=1)
LOAD_ATTR 4 from_python 22 Positions(lineno=4, end_lineno=4, col_offset=0, end_col_offset=13)
LOAD_CONST 2 sup python! 42 Positions(lineno=4, end_lineno=4, col_offset=14, end_col_offset=27)
CALL 1 1 44 Positions(lineno=4, end_lineno=4, col_offset=0, end_col_offset=28)
POP_TOP None None 52 Positions(lineno=4, end_lineno=4, col_offset=0, end_col_offset=28)
PUSH_NULL None None 54 Positions(lineno=5, end_lineno=5, col_offset=0, end_col_offset=8)
LOAD_NAME 1 b 56 Positions(lineno=5, end_lineno=5, col_offset=0, end_col_offset=1)
LOAD_ATTR 6 from_c 58 Positions(lineno=5, end_lineno=5, col_offset=0, end_col_offset=8)
LOAD_CONST 3 hi C! 78 Positions(lineno=5, end_lineno=5, col_offset=9, end_col_offset=16)
CALL 1 1 80 Positions(lineno=5, end_lineno=5, col_offset=0, end_col_offset=17)
POP_TOP None None 88 Positions(lineno=5, end_lineno=5, col_offset=0, end_col_offset=17)
RETURN_CONST 1 None 90 Positions(lineno=5, end_lineno=5, col_offset=0, end_col_offset=17)
"""

def build(ENV):

	SnapProject = ENV.SnapProject

	# TODO perform generic project operations to compile the test project
	class Project(SnapProject):

		def __init__(self, **SETTINGS):
			SnapProject.__init__(self, **SETTINGS)

	return Project


def main(ENV):
	ENV.__run_gui__(build, packages=[os.path.join(THISDIR, 'project')])

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv(gui='QT5', engine='QT5'))


