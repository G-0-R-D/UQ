


import os, re
pjoin = os.path.join

import numpy

#from MYLIBRARY.times.timing import Stopwatch


if 0:
	VALUES = r'([^\n]+)'

	OBJECT = r'(?P<o>o\s+' + VALUES + ')'

	COMMENT = r'(#[^\n]+)'

	STATEMENTS = [r'(?P<{0}>{0}\s+([^\n]+))'.format(symbol) for symbol in ('o', 'g', 's', 'f', 'vp', 'vn','vt','v', 'mtllib', 'usemtl', 'usemat')]

	RE_GRAMMAR = re.compile('|'.join([COMMENT] + STATEMENTS))

	print(repr(RE_GRAMMAR.pattern))
	get_index = RE_GRAMMAR.groupindex
	OBJECT = get_index['o']
	GROUP = get_index['g']
	SMOOTH = get_index['s']

	MATERIAL_LIBRARY = get_index['mtllib']
	USE_MATERIAL = 'TODO'

	VERTEX_GEOMETRY = get_index['v']
	VERTEX_NORMAL = get_index['vn']
	VERTEX_TEXTURE = get_index['vt']
	VERTEX_PARAMETER = get_index['vp']
	INDICES = get_index['f']


data = ['78465//131391', '78466//131391', '78461//131391']
array = numpy.fromstring('/'.join(data).replace('//', '/'), dtype=numpy.uint32, sep='/')
#print(array)


# TODO: use a match to get first element in result chunk to determine axes, and that will validate the data!  so otherwise just collect the line tags!



def finalize(OBJECTS, merge=False, **SETTINGS):

	objects = []

	VERTEX_DATA = 0
	TEXTURE_DATA = 1
	NORMAL_DATA = 2

	for settings,point_data in OBJECTS:
		#print('finaling', settings['name'])

		face_data = point_data.get('f', None)
		if not face_data:
			'just return point data'

		sample = face_data[0]
		str_data = face_data[1]

		if '/' not in sample[0]:
			'vertex data only'
			all_faces = numpy.array(str_data, dtype=numpy.uint32) - 1 # idx fix
		else:
			samples = [int(bool(i)) for i in sample[0].split('/')]
			if len(samples) < 3:
				samples.extend([0 for i in range(3-len(samples))])
			#print('samples', samples)
			#has_vertex_data, has_texture_data, has_normal_data = sample[0].split('/')
			str_data = '/'.join(str_data)
			if not samples[1]:
				str_data = str_data.replace('//', '/')
			all_faces = numpy.fromstring(str_data, dtype=numpy.uint32, sep='/') - 1

		'make array of all face data'
		'step through array to separate out the channels'
		'subtract one from array to make the indexing correct'

		verts = ''

		new = {
			# name, smooth, material; already added
			'format':('position',3, 'texture',2, 'normal',3),
			'vertices':numpy.array([]),
			'indices':numpy.array([]),
		}
		settings.update(new)

		objects.append(settings)

	return objects

def obj_open(PATH, **SETTINGS):

	# TODO *invert_axes/swap_axes, merge into one object or keep separate

	SMOOTH_SETTING = {
		'off':0,
		'0':0,
		'on':1,
		'1':1,
		}


	objects = [] # add objects for post-processing
	objects_append = objects.append
	materials = [] # process material declarations # TODO
	materials_append = materials.append

	# active mesh object data
	settings = {} # 'name', 'smooth', 'material'
	point_data = {} # v,vn,vt,vp,f -> vertices and indices, we'll sort them out later!

	# for accumulating point data
	active_symbol = None
	sample = None
	accum = None
	accum_extend = None # localize for speed

	with open(PATH, 'r') as openfile:

		#with Stopwatch('open file'):
		# TODO: check performance using a proper regex that returns the symbol and data without newline
		for line in openfile.read().splitlines():

			if not line:
				print('warning: empty line in .obj file!  ignoring')
				continue

			values = line.split()
			symbol = values[0]
			#print(symbol, values[1:])

			#continue # XXX

			if symbol in (' ', '#'): # IGNORE
				active_symbol = None
				continue

			if symbol == active_symbol:

				# assumes that if the same symbol is encountered twice in a row then it is point data
				accum_extend(values[1:])

			else:

				# finalize accumulated point data
				if accum:
					point_data[active_symbol] = (sample, accum)

				# switch to new mode
				if symbol in ('v','vt','vn','vp','f'):
					# TODO: support faces of 3 or 4 (or arbitrary?)
					#	-- support negative indexing (from the end)
					#	-- support 2D and 3D point data (or arbitrary?)
					#	-- support int types as floats?

					sample = values[1:]
					accum = []
					accum_extend = accum.extend
					accum_extend(sample)


				else:
				
					if symbol == 'o':
						if settings: # ie. if name != None
							objects_append( (settings, point_data) ) # TODO: rest of data

						try:
							name = values[1]
							'assert name not in seen' # ?
						except:
							name = '<BADNAME>_mesh_{}'.format(len(objects))

						#print('o', name)

						settings = {'name':name}
						point_data = {}

					elif symbol == 'g':
						raise NotImplementedError('groups')

					elif symbol == 's':
						try:
							value = SMOOTH_SETTING[values[1]]
							if value: # don't bother adding if disabled
								settings['smooth'] = value
						except:
							pass

					elif symbol == 'mtllib':
						print('material', values[1])
						materials_append(values[1])

					elif symbol in ('usemtl','usemat'):
						try:
							m = values[1]
							if m != 'None': # note quotes
								settings['material'] = m
						except Exception as e:
							print('bad material', line, repr(e))

					else:
						raise Exception('undefined symbol!', symbol)

					sample = None
					accum = None
					accum_extend = None

				active_symbol = symbol

		# add any last accumulated point data
		if accum:
			point_data[active_symbol] = (sample, accum)
	
	# add last object
	if settings:
		objects_append( (settings, point_data) )

	#with Stopwatch('finalize'):
	OBJECTS = finalize(objects, **SETTINGS)

	return OBJECTS
	

def build(ENV):
	return obj_open

if __name__ == '__main__':

	import time
	#from MYLIBRARY.times.timing import Stopwatch

	THISDIR = os.path.realpath(os.path.dirname(__file__))

	#with Stopwatch('load obj file'):
	start_time = time.time()
	obj = obj_open(pjoin(THISDIR, 'obj/suzanne.obj'))
	print('finished', time.time() - start_time)



	from random import random
	a1 = numpy.array(range(8))
	a2 = numpy.array([i+1 for i in range(20)])
	a1 += 2

	print(a2[a1])
