

# everything is really implemented in the engine subclass, but adding this class for completeness

# https://stackoverflow.com/questions/14022574/float-rgb-values-vs-ubyte-rgb-values-for-colour
""" why use float:
Pro:
    doesn't need to be converted to/from float when doing math
    preserves intermediate values much more accurately when applying a number of processing steps sequentially
    has much greater dynamic range and resolution
    float is natural format for GPU etc
Con:
    requires more storage
"""

def build(ENV):

	SnapPaint = ENV.SnapPaint

	SnapMessage = ENV.SnapMessage

	class SnapColor(SnapPaint):

		__slots__ = []

		"""
		@ENV.SnapProperty
		class rgba:

			def get(self, MSG):
				""()->list(4 * float)""
				#return self._as('rgba')
				return self['data', SnapMessage(format='rgba')]

			def set(self, MSG):
				""(list(4*int|float)!)""
				# TODO self['data'] = MSG...
		"""

		"""
		@ENV.SnapProperty(private=True)
		class __engine_data__:
			# NOTE: engine will access self.__snap_data__['__properties__']['__engine_data__'] directly...
			# this is the only thing that needs to be re-implemented in engine class to map into engine data...

			def get(self, MSG):
				""()->list(4 * float)""
				data = SnapNode_get(self, '__engine_data__')
				if data is None:
					return [0., 0., 0., 1.]
				return data

			def set(self, MSG):
				""(list(4 * float))"" # strict, this is internal
				data = MSG.args[0]
				clamp = lambda v: max(0.0, min(v, 1.0))
				if data is not None:
					assert len(data) == 4, 'incorrect format for rgba color'
					data = [float(clamp(n)) for n in data]
				SnapNode_set(self, '__engine_data__', data)
		"""

		@ENV.SnapProperty
		class data: # TODO data is just rgba or configuration of, hex gets it's own property...  (it's a different model)

			def get(self, MSG):
				"""(format=str?)->list(4 * float)|list(3 * float)"""
				FORMAT = MSG.kwargs.get('format', 'rgba').lower()
				assert ''.join(sorted(FORMAT)) in ('abgr','bgr'), 'invalid format: {}'.format(repr(FORMAT))

				rgba = self['data']

				return [rgba['rgba'.index(c)] for c in FORMAT]

			def set(self, MSG):
				"""(
				(r=int|float?, g=int|float?, b=int|float?, a=int|float?),
				(list|tuple(4 * int|float)!, format=str?),
				(list|tuple(3 * int|float)!, format=str?),
				(4 * int|float!, format=str?),
				(3 * int|float!, format=str?),
				)"""
				FORMAT = MSG.kwargs.get('format', 'rgba').lower()
				assert ''.join(sorted(FORMAT)) in ('abgr','bgr'), 'invalid format: {}'.format(repr(FORMAT))

				#ENV.snap_out("format", FORMAT, MSG)

				# TODO verify only rgba letters in format, and check if 3 or 4?

				#rgba = self['__engine_data__'][:] # XXX this is the other way around
				rgba = self.__snap_data__['data'] or [0., 0., 0., 1.]

				clamp = lambda v: max(0.0, min(v, 1.0))

				user = None

				if len(MSG.args) == 1:
					user = MSG.args[0]

				elif len(MSG.args) in (3,4):
					user = MSG.args

				else:
					args = {k:v for k,v in MSG.kwargs.items() if k in 'rgba'}
					if args:
						for k,v in args.items():
							rgba['rgba'.index(k)] = clamp(v)
					else:
						rgba = [0.,0.,0.,1.]

				if user is not None:
					assert len(user) == len(FORMAT), 'format,data length mismatch'
					for idx,c in enumerate(FORMAT):
						rgba['rgba'.index(c)] = clamp(user[idx])

				self.__snap_data__['data'] = rgba
				self.changed(data=rgba)
	
		# TODO make __engine_data__ a property and then it can be intercepted to assign to engine...


		@ENV.SnapProperty
		class relative:

			# TODO if relative (base) color then we evaluate ourself as an offset from that...

			def get(self, MSG):
				"()->SnapColor"
				return self.__snap_data__['relative']

			def set(self, MSG):
				"(SnapColor!)"
				color = MSG.args[0]
				if color is not None:
					assert isinstance(color, SnapColor), 'relative of a color must be another color'
				self.__snap_data__['relative']


		@ENV.SnapProperty
		class hex:
			def get(self, MSG):
				raise NotImplementedError()

			def set(self, MSG):
				raise NotImplementedError()


		"""
		@ENV.SnapChannel
		def as(self, MSG):
			""(key=str)->list(4 * float)""

			KEY = MSG.unpack('key', 'RGBA')

			if KEY is None:
				KEY = 'RGBA'

			# TODO make a get property that can support a lot of outputs?
			l = self.__engine_data__()
			if KEY.upper() == 'RGBA' and l:
				return l[:]
			if l is None:
				return [0.,0.,0.,1.]
			if not isinstance(l, (list, tuple)):
				raise TypeError('wrong engine data type?')
			return self._reformat(KEY, l)

		def _reformat(self, MSG):

			FORMAT, RGBA = MSG.unpack('format', 'RGBA', 'rgba', [])

			'return in another format'
			lower_format = FORMAT.lower()

			if lower_format == 'rgba':
				return RGBA[:]
			elif lower_format == 'rgb':
				return RGBA[:3]

			spl = sorted([ch for ch in lower_format]) if len(FORMAT) <= 4 else []

			if spl == ['a','b','g','r']:
				return [RGBA['rgba'.index(c)] for c in lower_format]
			elif spl == ['b','g','r']:
				return [RGBA['rgb'.index(c)] for c in lower_format]

			elif lower_format in ('r','g','b','a'):
				return RGBA['rgba'.index(lower_format)]

			elif lower_format == 'hex':
				raise NotImplementedError(FORMAT)

			raise TypeError(FORMAT, 'unsupported')


		def _decode_setting(self, MSG):
			# return r,g,b,a list or None if attr is not a color assignment...

			ATTR,VALUE,existing_color = MSG.unpack('format', '', 'value', None, 'existing_color', None)

			lower_attr = ATTR.lower()

			clamp = lambda v: max(0.0, min(v, 1.0))

			# for speed because these settings are common...
			if lower_attr == 'rgba':
				if VALUE is not None:
					assert len(VALUE) == 4, 'wrong arguments for "{}" {}'.format(ATTR, repr(VALUE))
					return [clamp(v) for v in VALUE]
				else:
					return [0.,0.,0.,1.]

			elif lower_attr == 'rgb':
				if VALUE is not None:
					assert len(VALUE) == 3, 'wrong arguments for "{}" {}'.format(ATTR, repr(VALUE))
					return [clamp(v) for v in VALUE] + [1.]
				else:
					return [0.,0.,0.,1.]


			spl = sorted(lower_attr.split()) if len(ATTR) <= 4 else []

			if spl == ['a','b','g','r']:
				if VALUE is not None:
					return [clamp(VALUE[lower_attr.index(c)]) for c in 'rgba']
				else:
					return [0.,0.,0.,1.]

			elif spl == ['b','g','r']:
				if VALUE is not None:
					return [clamp(VALUE[lower_attr.index(c)]) for c in 'rgb'] + [1.]
				else:
					return [0.,0.,0.,1.]

			elif lower_attr in ('r','g','b','a'):
				if existing_color is None:
					existing_color = [0.,0.,0.,1.]
				existing_color['rgba'.index(lower_attr)] = clamp(VALUE)
				return existing_color

			elif lower_attr == 'hex':
				raise NotImplementedError('hex')

			return None
		"""

		"""
		def set(self, MSG):

			changed = False

			color = self.rgba()

			for attr,value in MSG.kwargs.items():

				color = self._decode_setting(attr, value, color)
				if color is not None:
					self.data()['__engine_data__'] = color
					changed = True
				else:
					SnapPaint.set(self, SnapMessage(**{attr:value}))

			if changed:
				self.changed(color=color, format='rgba') # TODO store format?
		"""

		def __init__(self, r=None, g=None, b=None, a=None, **SETTINGS):
			SnapPaint.__init__(self, **SETTINGS)

			init = [r or 0.,g or 0.,b or 0.,a if a is not None else 1.]

			for k,v in SETTINGS.items():
				if k == 'rgba': # also 'color'?
					init[:] = v
				elif k not in ('extents','matrix'):
					ENV.snap_warning('unhandled color init', k)

			self['data'] = init

			
	ENV.SnapColor = SnapColor

def main(ENV):

	color = ENV.SnapColor()

	color['data', ENV.SnapMessage(format='bgra')] = [.1, .2, .3, .4]

	ENV.snap_test_out(color['__engine_data__'] == [.3, .2, .1, .4])

	ENV.snap_out('ok')

