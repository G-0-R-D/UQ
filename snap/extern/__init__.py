
import os
from snap.extern.ctypes import my_ctypes as ctypes
from snap.extern import Qt5

def build(ENV):

	#ENV.os = os
	#ENV.ctypes = ctypes # TODO phase this out?

	#Qt5.build(ENV)
	#OpenGL.build(ENV)
	# TODO ExternModule.build(self)

	class SnapExtern(object):

		def __init__(self):

			self.os = os
			self.ctypes = ctypes

			Qt5.build(self)

	ENV.extern = SnapExtern()
