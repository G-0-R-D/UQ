
# ctypesgen didn't wrap the key values properly (need to be numeric values not strings)

from snap.lib.extern.SDL.ctypesgen_SDL.SDL2 import *

# https://stackoverflow.com/questions/1885181/how-to-un-escape-a-backslash-escaped-string
import ast

import os,re

header = '/home/user/.SETUP/install/include/SDL2/SDL_keycode.h'
with open(header, 'r') as openfile:
	lines = openfile.readlines()

pattern = re.compile(r"\s*SDLK_(\S+)\s*\=\s*'([^']+)'")
for line in lines:
	line = line.strip(' \t\n')

	match = pattern.match(line)
	if not match:
		if line.startswith('SDLK_') and line.count("'") >= 2:
			print('miss?', line)
		continue
	name,o = match.groups()
	#print(name, repr(o))
	q = '"' if '"' not in o else "'"
	if o != '\\':
		o = ast.literal_eval(q*3+o+q*3)
	#print(name, ord(o))
	globals()['SDLK_'+name] = ord(o)


