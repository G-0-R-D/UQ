from ctypes import *
import ctypes # so we can disambiguate if needed

import os

def snap_c_offset(PTR, OFFSET):
	"""
		# https://www.programcreek.com/python/?code=skelsec%2Fminidump%2Fminidump-master%2Fminidump%2Futils%2Fprivileges.py
		buf = ctypes.create_string_buffer(4 * ctypes.sizeof(ctypes.c_double))
		PTR = ctypes.cast(buf, POINTER(c_double * 4)).contents # the .contents because this is essentially a pointer(pointer())!
	or:
		PTR = (ctypes.c_double * 4)()
	"""

	#PTYPE = POINTER(TYPE)
	TYPE = POINTER(PTR._type_)
	#print('type', TYPE) # this gives the wrong type (like c_double_4 instead of c_double...) for buffers...
	return cast(addressof(PTR) + sizeof(TYPE) * OFFSET, TYPE)

# https://gist.github.com/JonathonReinhart/b6f355f13021cd8ec5d0101e0e6675b2

def snap_recompile_support_library(FILEPATH, **SETTINGS):

	FILEPATH = os.path.realpath(FILEPATH)

	#print(FILEPATH)

	dirname = os.path.join(os.path.dirname(FILEPATH), 'CExtensions')
	basename = os.path.basename(FILEPATH)
	naked_name = '.'.join(basename.split('.')[:-1])# + 'Ext'
	srcfile = os.path.join(dirname, naked_name + '.c')
	libfile = os.path.join(dirname, naked_name + '.so')

	if not os.path.exists(libfile) or os.stat(srcfile).st_mtime >= os.stat(libfile).st_mtime:
		#snap_debug('recompiling {} support library {}'.format(repr(basename), repr(libfile)))
		os.system("gcc -shared -fpic -Wall -Werror -lm -o {} {}".format(libfile, srcfile))

	return ctypes.CDLL(libfile)

#ENV.recompile_support_library = recompile_support_library
