
import dis, os
THISDIR = os.path.realpath(os.path.dirname(__file__))

class MyClass(object):

	def __init__(self):
		pass

data = """
class Test:
	pass
"""
if 0:
	with open(__file__, 'r') as openfile:
		data = openfile.read()

for ins in dis.get_instructions(data):

	print(ins.opname, ins.arg, ins.argval, ins.offset, ins.positions)

