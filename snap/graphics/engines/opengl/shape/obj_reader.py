
import numpy

# https://community.khronos.org/t/loading-obj-file-how-to-triangularize-polygons/74965

def _finalize_obj(OBJ, opengl_format=True):

	point_data = OBJ.get('point_data', {})

	if not opengl_format:
		raise NotImplementedError() # just keep them as they are?  v, vn, vt, vp, f, ... but as numpy arrays?
	else:

		#'vertices: [position(x,y,z), normal(x,y,z), texture(u,v), ...]
		#'indices': [vertex_index, ...] # triangles...

		fmt = [] # vertices, normals, uv (strides and order)

		v = point_data.get('v')
		assert v, 'no vertex data in object? {}'.format([OBJ.get('name'), OBJ.get('index'), OBJ.keys(), point_data.keys()])

		assert len(v['sample']) == 3, 'axes != 3 unsupported; obj vertex data must be 3D'
		fmt.append(('vertices',3))

		vn = point_data.get('vn')
		if vn:
			assert len(vn['sample']) == 3, 'axes != 3 unsupported; obj normal data must be 3D'
			fmt.append(('normals',3))
		vt = point_data.get('vt')
		if vt:
			# TODO, also make it optional to disregard?
			print('warning: vt data not yet supported')

		if 'vp' in point_data:
			# TODO?
			print('warning: vp data not yet supported')


		# TODO numpy.float32?

		stride = sum([f[1] for f in fmt])
		print(len(v['accum']), stride, fmt)
		# TODO get full stride size, allocate a numpy array in one go
		# then assign the strings to an array and broadcast it...

		num_points = int(len(v['accum']) / 3)

		vertices = numpy.empty((num_points, stride), dtype=numpy.float32)
		vertices[:, :3] = numpy.array(v['accum'], dtype=numpy.float32).reshape(num_points, 3)

		last_position = 3
		if vn: 
			vertices[:, last_position:last_position+3] = numpy.array(vn['accum'], dtype=numpy.float32).reshape(num_points,3)
			last_position += 3

		if vt:
			vertices[:, last_position:last_position+2] = numpy.array(vt['accum'], dtype=numpy.float32).reshape(num_points,2)
			last_position += 2 # just in case?

		vertices = vertices.reshape(num_points * stride)
		

		# Face with only geometric vertices.
		# f v1 v2 v3 ...
		# Face with geometric vertices and texture coordinates.
		# f v1/vt1 v2/vt2 ...
		# Face with geometric vertices and vertex normals (note the double slash).
		# f v1//vn1 v2//vn2 ...
		# Face with geometric vertices, texture coordinates, and vertex normals.
		# f v1/vt1/vn1 v2/vt2/vn2 ...

		# TODO faces can be negative indices too?  make them positive again?

		f = point_data.get('f')
		if f:
			sample = f['sample']
			strings = f['accum']

			if '/' in sample[0]:
				if '//' in sample[0]:
					# v//vn
					assert [x[0] for x in fmt] == ['vertices', 'normals'], 'invalid face configuration'
					strings = [i for entry in strings for i in entry.split('//')]
				else:
					# v/vt/vn or v/vt
					assert [x[0] for x in fmt] in (['vertices','normals','uv'], ['vertices','uv']), 'invalid face configuration'
					strings = [i for entry in strings for i in entry.split('/')]
			else:
				# v positions only
				assert [x[0] for x in fmt] == ['vertices'], 'invalid face configuration'
			faces = numpy.array(strings, dtype=numpy.int32) - 1 # (-1 index fix; start from 0)

			# TODO do the faces/indices need to be re-ordered?
		else:
			# just vertex data, no faces specified...
			faces = None

		OBJ['point_data'] = {
			'format':tuple(fmt),
			'vertices':vertices,
			'indices':faces,
		}

	return OBJ

def read_objects(filepath, **SETTINGS):

	SMOOTH_SETTINGS = {
		'off':False,
		'0':False,
		'on':True,
		'1':True,
		}

	obj = None
	# {
	#	# name
	#	# settings
	#	# materials
	#	'point_data':{}, # 'v','vn','vt','vp', 'f', ... we'll sort it out after
	#}

	settings = {
		# smooth
		# use_materials = []
	}

	point_data = None #obj['point_data']

	accum = None
	accum_extend = None
	active_symbol = None

	obj_count = 0

	with open(filepath, 'r') as openfile:
		for line in openfile:

			if line[0] in ('#', ' ', '\n'):
				continue

			values = line.split()
			if not values:
				continue
			symbol = values.pop(0)

			if symbol == active_symbol:
				# accum the string values, we'll convert them in a batch after
				accum_extend(values)
			else:

				#if accum:
				#	# adding the accum in case symbols are in a messed up order or some reason...
				#	point_data[active_symbol] = point_data.get(active_symbol, []) + accum

				if symbol in ('v', 'vn', 'vt', 'vp', 'f'):
					# TODO apparently 'f' can be arbitrarily sized ngons, but opengl only works with triangles... assuming triangles for now...
					sample = values
					entry = point_data[symbol] = point_data.get(symbol, {}) # in case they aren't in order?
					if 'sample' in entry:
						'verify compat?'
						assert len(entry['sample']) == len(sample), 'incompatible entries'
					entry['sample'] = sample
					accum = entry['accum'] = entry.get('accum', [])
					accum_extend = accum.extend
					accum_extend(sample)
					active_symbol = symbol

				else:
					# these symbols are not (expected) to be accumulating
					active_symbol = None
					accum = accum_extend = None

					if symbol == 'o':
						# obj definition begins (there can be multiple objects in the file)
						if obj:
							if settings:
								obj['settings'] = settings

							yield _finalize_obj(obj, **SETTINGS)

							settings = {}

						try:
							name = values[0]
						except:
							name = 'unknown{}'.format(obj_count)

						point_data = {}
						obj = {
							'index':obj_count,
							'name':name,
							# settings added if used
							'point_data':point_data,
							}

						if settings: # with no previous obj, then it belongs to this (next) one
							obj['settings'] = settings

						obj_count += 1

					elif symbol == 's':
						try:
							value = SMOOTH_SETTINGS[values[0]]
							if value: # don't bother adding if disabled
								settings['smooth'] = value
						except:
							pass

					elif symbol == 'mtllib':
						settings['materials'] = settings.get('materials', []) + [values[0]] # just a material name...

					elif symbol in ('usemtl','usemat'):
						try:
							mat = values[0]
							if mat != 'None': # note quotes
								settings['use_materials'] = settings.get('use_materials', []) + [mat]
						except Exception as e:
							print('bad', repr(symbol), 'value', repr(values))

					elif symbol == 'g':
						raise NotImplementedError('groups')

					else:
						print('warning: unidentified symbol', repr(symbol))

	if obj:
		yield _finalize_obj(obj, **SETTINGS)

def build(ENV):
	return read_objects

if __name__ == '__main__':

	import time
	start_time = time.time()
	for obj in read_objects('obj/suzanne.obj'):
		print('completed obj', obj)#.keys())
	print('finished', time.time()-start_time)

