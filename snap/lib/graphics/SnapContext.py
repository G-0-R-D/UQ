
def build(ENV):

	SnapNode = ENV.SnapNode

	snap_matrix_t = ENV.snap_matrix_t
	SnapMatrix = ENV.SnapMatrix
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX

	snap_matrix_invert = ENV.snap_matrix_invert
	snap_matrix_multiply = ENV.snap_matrix_multiply

	#SnapProperty = ENV.SnapProperty

	# NOTE: deliberately not a SnapNode subtype for speed!
	class SnapContext(SnapNode):

		__slots__ = [
		#'_config_', '_engine_context_',#'_config_defaults_',
		#'_current_container_', '_current_items_', '_render_mode_', '_items_attr_', # so they are visible everywhere context is... makes it easier this way!
		#'_depth_', '_only_first_lookup_', '_lookup_results_',
		]

		CONFIG_DEFAULTS = {
			
			'cmd_set_antialias':0.0,
			}

		MAX_RENDER_DEPTH = 100

		@ENV.SnapProperty
		class image:

			def get(self, MSG):
				"""()->SnapImage"""
				return self.__snap_data__['image']

			"""
			def setXXX(self, MSG):
				"(SnapImage!)"
				raise NotImplementedError('image cannot be changed after context is initialized')
				image = MSG.args[0]
				if image is not None:
					assert isinstance(image, ENV.SnapImage), 'not a SnapImage: {}'.format(type(image))
				self.__snap_data__['image'] = image
			"""

		@ENV.SnapProperty
		class matrix:

			def get(self, MSG):
				"""()->snap_matrix_t"""
				m = self.__snap_data__['matrix']
				if m is None:
					m = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
					self.__snap_data__['matrix'] = m
				return m

			def set(self, MSG):
				"""(snap_matrix_t|SnapMatrix)"""
				m = MSG.args[0]
				if m is None:
					self.__snap_data__['matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
				else:
					if isinstance(m, SnapMatrix):
						m = m['matrix']
					assert isinstance(m, snap_matrix_t), 'not a matrix type? {}'.format(type(m))
					self.__snap_data__['matrix'] = m

				try:
					self.cmd_apply_matrix()
				except:
					if self['engine_context'] is None:
						pass
					else:
						raise Exception('unable to apply matrix.set() to context', self.__class__.__name__)

		@ENV.SnapProperty
		class current_container:

			def get(self, MSG):
				"""()->SnapContainer"""
				return self.__snap_data__['current_container']

			# set not allowed at user level

		def cmd_check_interact(self, threshold=0):
			return None # engine must implement, does pixel check for visibility (pixel alpha >= threshold)

		def cmd_render_subitems(self):

			data = self.__snap_data__

			items = data['current_items']
			if items:

				if data['depth'] <= 0:
					ENV.snap_debug('max render depth reached')#, CHANNEL)
					return None

				data['depth'] -= 1

				# localize to set back after...
				container = data['current_container']

				render_mode = data['render_mode']
				items_attr = data['items_attr']

				CTX_matrix = self['matrix']

				saved_offset = snap_matrix_t(*CTX_matrix)

				if render_mode == 'lookup':
					# doing lookup backwards can lead to faster checks in some instances since most forward element will be what is 'under the mouse'
					i = len(items) - 1 # index of last, not length (using != end)
					direction = -1
					end = -1
					#items_attr = 'lookup_items'
				else: # 'draw'
					i = 0
					direction = 1
					end = len(items)
					#items_attr = 'render_items'

				while i != end:
					# NOTE: at beginning of DRAW|LOOKUP event of container, context is set to current container and offset (self)
					# so rendering would be 'inside' container, or in the local space of the container

					c = items[i]

					if c is None:
						i += direction
						continue

					CTX_matrix[:] = saved_offset

					data['current_container'] = c
					#data['current_items'] = getattr(c, items_attr)() # render_items()|lookup_items()
					data['current_items'] = c[items_attr]

					try:
						item_matrix = c['render_matrix']
					except Exception as e:
						ENV.snap_debug_print_exception(e)
						item_matrix = None

					if item_matrix is not None:
						snap_matrix_multiply(saved_offset, item_matrix, CTX_matrix)
						self.cmd_apply_matrix() # ?

					# c.draw(self)|c.lookup(self)
					call = getattr(c, render_mode, None)
					if call is not None:
						# allow for non-renderables to be in scene
						call(self)
					#	-> this forwards to shader program or any other handling the container wants to do...

					i += direction

				# reset because there might be more ins to call in same shader or at same level...
				# like a shader could call this to render subitems in the middle of other ins calls...

				#self._pop_config()

				CTX_matrix[:] = saved_offset
				data['current_container'] = container
				data['current_items'] = items

				data['depth'] += 1


		"""
		def cmd_set_fill_color(self, COLOR):
			self._config_['cmd_set_fill_color'] = COLOR

		def cmd_set_fill_gradient(self, GRADIENT):
			self._config_['cmd_set_fill_gradient'] = GRADIENT

		def cmd_set_fill_texture(self, TEXTURE):
			self._config_['cmd_set_fill_texture'] = TEXTURE

		def cmd_set_fill_pattern(self, PATTERN):
			self._config_['cmd_set_fill_pattern'] = PATTERN


		def cmd_set_stroke_color(self, COLOR):
			self._config_['cmd_set_stroke_color'] = COLOR

		def cmd_set_stroke_gradient(self, GRADIENT):
			self._config_['cmd_set_stroke_gradient'] = GRADIENT

		def cmd_set_stroke_texture(self, TEXTURE):
			self._config_['cmd_set_stroke_texture'] = TEXTURE

		def cmd_set_stroke_pattern(self, PATTERN):
			self._config_['cmd_set_stroke_pattern'] = PATTERN
		"""

		def cmd_set_transform(self, MATRIX):
			raise NotImplementedError()


		def cmd_set_matrix(self, MATRIX):
			# NOTE: this is user api in local coordinates, set relative to current offset!
			"""
			m = snap_matrix_t()
			# NOTE: that self._matrix_ stays what it is...
			snap_matrix_multiply(self._matrix_, MATRIX.__snap_data__['matrix'], m)
			self._engine_context_.setWorldTransform(QTransform(m[0], m[4], m[1], m[5], m[3], m[7]))
			"""
			raise NotImplementedError()

		def cmd_transform(self, MATRIX):
			# MATRIX is the change to apply to self._matrix_
			"""
			m = snap_matrix_t()
			snap_matrix_multiply(MATRIX.__snap_data__['matrix'], self._matrix_, m) # TODO local?
			self._engine_context_.setWorldTransform(QTransform(m[0], m[4], m[1], m[5], m[3], m[7]))
			"""
			raise NotImplementedError()

		def cmd_apply_matrix(self): # XXX don't do this anymore, just always apply when it is changed
			# because engine context matrix doesn't actually have to be set until we use it
			# this is always the first call of a shader...

			"""
			m = self._matrix_
			self._engine_context_.setWorldTransform(QTransform(
				m[0], m[4],
				m[1], m[5],
				m[3], m[7],
				))
			"""

			raise NotImplementedError()



		def cmd_clip(self, SHAPE):
			raise NotImplementedError()

		def cmd_clip_extents(self, EXTENTS):
			# to be able to clip to a rect quick and easy
			raise NotImplementedError()



		# TODO other primitives?  arc?  triangle?  rect?


		def cmd_draw_text(self, TEXT):
			# this is full text rendering (as a document, with markups etc...),
			# otherwise convert the text to a spline and use it as a spline
			raise NotImplementedError()


		def cmd_fill_spline(self, PAINT, SPLINE):
			raise NotImplementedError()

		#cmd_fill_shape = cmd_fill_spline

		def cmd_fill_mesh(self, PAINT, MESH):
			raise NotImplementedError()

		# cmd_fill_rect just use this:
		def cmd_fill_extents(self, PAINT, EXTENTS):
			# NOTE: image as a shape can be used here...  draws a rectangle using extents() parameter
			raise NotImplementedError()

		def cmd_fill_circle(self, PAINT, x,y, radius):
			# POS_RADIUS is (x,y,radius)
			raise NotImplementedError()


		def cmd_stroke_spline(self, PAINT, SPLINE):
			raise NotImplementedError()

		#cmd_stroke_shape = cmd_stroke_spline

		def cmd_stroke_mesh(self, PAINT, MESH):
			raise NotImplementedError()

		def cmd_stroke_extents(self, PAINT, EXTENTS):
			# NOTE: to do a simple rectangle render you can make a Metrics(...) instance just for the rect...
			raise NotImplementedError()

		def cmd_stroke_circle(self, PAINT, x,y, radius):
			raise NotImplementedError()


		def cmd_set_blendmode(self, MODE):
			raise NotImplementedError()


		def cmd_save(self):
			# self._config_['cmd_save'] = self._config_ ?  self._config_ = self._config_.copy()?
			raise NotImplementedError()

		def cmd_restore(self):
			raise NotImplementedError()




		#def cmd_set_stroke_after(self, BOOL):
		#	'' # XXX this is just the order of operations of draw/stroke calls, put in operator!

		# NOTE: Qt puts these onto the pen, but I don't want to have a different 'paint' for line/fill, paint is paint!

		def cmd_set_line_width(self, UNITS):
			# 0.0->1.0?
			self._config_['cmd_set_line_width'] = UNITS
			raise NotImplementedError()

		def cmd_set_line_miter(self, MODE):
			self._config_['cmd_set_line_miter'] = MODE
			raise NotImplementedError()

		def cmd_set_line_miter_limit(self, LIMIT):
			self._config_['cmd_set_line_miter_limit'] = LIMIT
			raise NotImplementedError()

		def cmd_set_line_join(self, MODE):
			self._config_['cmd_set_line_join'] = MODE
			raise NotImplementedError()

		def cmd_set_line_cap(self, MODE):
			self._config_['cmd_set_line_cap'] = MODE
			raise NotImplementedError()

		#def cmd_set_fill_rule(self, MODE) XXX make this engine specific only...

		def cmd_set_dash(self, POINTS):
			# points are (offset, on, off, on, off, ...)
			self._config_['cmd_set_dash'] = POINTS
			raise NotImplementedError()
		


		def cmd_set_maskXXX(self, MASK):
			'' # TODO masking and alpha override behaviour?  requires another layer, maybe just restrict it to pre-creating render target surface to render to before mixing down...
			# was cairo push_group/pop_group
			# XXX to do masking/alpha_over, just use an intermediary container and render to the image on it, then mix that image down...


		def cmd_set_antialias(self, NORMALIZED_FLOAT):
			# 0.0 -> 1.0 percentage, just remap to intermediate values if there are any...
			#self._config_['cmd_set_antialias'] = PERCENTAGE
			raise NotImplementedError()



		"""
		def draw_elements(self, *SHAPES, fill=None, stroke=None, stroke_after=True, mask=None, **SETTINGS):

			# TODO this might work better with pre-checking, we need a render node that represents clip, config, draw, and lookup ins...  as a set
			# XXX keep shader, clipping and config as attribute of shader?  draw/lookup 'inside'

			if fill is None and stroke is None:
				ENV.snap_debug("no fill or stroke provided; no-op")
				return

			raise NotImplementedError() # implement in subclass

			for shape in SHAPES:
				''

			# stroke before / after
			# -- fill, stroke as paint (color, gradient, texture)
			# -- mask?
			# config can be done here as well, just for the one operation and then it sets back?

		# TODO lookup is just a draw and then a check and clear, so it should use draw_elements() as well!
		"""

		#def set(self, **SETTINGS):
		#	'' # TODO image?  non-rendering config?


		@ENV.SnapChannel
		def activate(self, MSG):
			"""()"""
			# activate in some engines will initialize the engine_context (if it has one)
			return None

		@ENV.SnapChannel
		def reset(self, MSG):
			"""()"""
			# undo configuration options to defaults, implement in subclass
			return None

		@ENV.SnapChannel
		def finish(self, MSG):
			"""()"""
			image = self['image']
			if image:
				image.changed_data.send()
			data = self.__snap_data__
			data['current_container'] = data['current_items'] = None
			return None

		@ENV.SnapChannel
		def clear(self, MSG):
			"""()"""
			image = self['image']
			if image is not None:
				image.clear() # TODO bg/default color from self._engine_context_?
			return None

		"""
		# cmd calls that change configuration for further rendering save the previous value and then restore it
		def _config(self):
			# just add new slot to config list (as None)
			# TODO pass the config from the shader? ready to go?
			self._config_.append(None)
			return None

		def _deconfig(self):

			cfg = self._config_.pop()
			if cfg:
				ctx = self._engine_context_
				for command,args in cfg:
					command(ctx, *args)
			return None

		def _register_deconfig(self, SET_FUNC, *args):

			curr = self.data()['config'][-1]
			if curr is None:
				curr = {}
			if SET_FUNC not in curr:
				'' # TODO
				#curr[SET_FUNC] = args or SnapShader.EMPTY_ARGS
				#self._config_[-1] = curr
		"""

		def __init__(self, image=None, depth=None, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			# XXX this needs to happen once context is assigned...
			#for k,v in self.CONFIG_DEFAULTS.items():
			#	getattr(self, k)(v) # TODO v is *args?

			data = self.__snap_data__

			data['engine_context'] = None # the actual context of the engine if it provides one (where the actual draw instructions are)

			data['current_container'] = None
			data['current_items'] = None
			data['render_mode'] = 'draw'
			data['items_attr'] = 'render_items'

			data['depth'] = depth

			# XXX these can be passed into the render call direct
			#self._container_ = None
			#self._items_ = []

			# TODO these are lookup only
			data['only_first_lookup'] = True
			data['lookup_results'] = []

			data['config'] = {}

			assert image is not None, 'must provide image for context to render onto'
			data['image'] = image


	ENV.SnapContext = SnapContext
 
def main(ENV):

	ENV.SnapContext(image=ENV.SnapImage())

	ENV.snap_out('ok')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

