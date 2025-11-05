
# https://stackoverflow.com/questions/661017/access-to-errno-from-python

import os, ctypes

def __errno(FUNC):
	return FUNC()

@__errno
def e():
	return ctypes.get_errno() # python 2.6 and higher

print('errno', e, os.strerror(e))

