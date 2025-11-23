

def build(ENV):

	SnapNode = ENV.SnapNode

	snap_matrix_multiply = ENV.snap_matrix_multiply
	snap_matrix_t = ENV.snap_matrix_t
	snap_matrix_invert = ENV.snap_matrix_invert
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX

	SnapMessage = ENV.SnapMessage


	class SnapLookupResults(object):

		__slots__ = ['results', '__callback__', 'position']

		def __iter__(self):
			for result in getattr(self, 'results', []):
				yield result

		def __getitem__(self, KEY):
			'' # TODO results by index

		def __init__(self, X, Y, callback=None):

			self.position = [float(X),float(Y)]

			self.__callback__ = callback # TODO use a default?

			self.results = None # assigned once lookup call is complete

	class SnapEngine(SnapNode):

		"""
		__slots__ = ['_name_', '_axes_',
			'_lookup_image_', '_lookup_context_',

			'ENGINE',
			# these are assigned to be the engine specific types with engine specific names removed...
			'Color', 'Gradient', 'Texture',
			'Path', 'Mesh', 'Text',
			'Image',
			'Context', 'Shader', 'CompositeShader', 'ParticleShader',

			'Shape', 'PreferredShape', 'DefaultShape',

			'fill_color', 'line_color',
			]
		"""
		@ENV.SnapProperty
		class remap_coordinates:
			# TODO matrix that re-orients the coordinate system (while maintaining same local orientation for graphics?)
			# TODO accomplish this by changing matrix class such that it moves into the remap coordinates space as if it was a parent transform, for all transforms...?  then it undoes it internally?  so effectively the transform happens in the remap space, but the original orientation is maintained...  TODO we would have to assign the matrix on a different channel if we're working with it in local coordinates...

			def get(self, MSG):
				"""()->SnapMatrix"""
				#raise NotImplementedError()
				ENV.snap_warning('not implemented', 'remap_coordinates')

			def set(self, MSG):
				matrix = MSG.args[0]
				if matrix is not None:
					raise NotImplementedError()

		@ENV.SnapProperty
		class axes:

			def get(self, MSG):
				"""()->int"""
				return 2

		@ENV.SnapProperty
		class name:

			def get(self, MSG):
				"""()->str"""
				return self.__class__.__name__


		def do_draw(self, image=None, items=None, offset=None, max_depth=None, clear=True):

			assert isinstance(image, self.Image), 'cannot use context without image'

			ctx = self.Context(image=image)

			ctx.activate()
			ctx.reset()
			if clear:
				ctx.clear()

			ctx_data = ctx.__snap_data__
			
			engine_context = ctx_data['engine_context']

			#assert engine_context is not None, 'context cannot be used without image and engine_context'

			ctx_data['depth'] = max_depth if max_depth is not None else ctx.MAX_RENDER_DEPTH
			assert ctx['depth'] <= ctx.MAX_RENDER_DEPTH, 'depth: {} exceeds limit: {}'.format(ctx['depth'], ctx.MAX_RENDER_DEPTH)

			ctx['matrix'] = offset if offset is not None else snap_matrix_t(*SNAP_IDENTITY_MATRIX)

			ctx_data['current_container'] = None
			ctx_data['current_items'] = items # will be the items of the container when applicable...
			ctx_data['render_mode'] = 'draw'
			ctx_data['items_attr'] = 'render_items'

			# TODO check for RENDER_INFO error message?
			ctx.cmd_render_subitems()

			ctx.finish()

			return None


		def do_lookup(self, image=None, x=0, y=0, items=None, offset=None, max_depth=None, clear=True, **SETTINGS):

			assert isinstance(image, self.Image), 'cannot use context without image'

			ctx = self.Context(image=image)

			ctx.activate()
			ctx.reset()
			if clear:
				ctx.clear()

			#ENV.snap_out('lookup begin pixel', ctx['image']['pixels']['data'], ctx['image'] is image)

			ctx_data = ctx.__snap_data__

			# NOTE: we can't initialize the image here because the engine_context also needs to be initialized for the image,
			# and that is engine specific, this is the general implementation
			engine_context = ctx_data['engine_context']
			#image = self.image

			#assert engine_context is not None, 'context cannot be used without engine_context'

			# NOTE: lookup assumes the context is being used as a lookup context itself (separately from a render context)
			if image['size'] != [1,1]:
				ENV.snap_warning('lookup context != [1,1]', image['size'])

			#if SETTINGS:
			#	ENV.snap_warning('unknown settings({})'.format(SETTINGS.keys()))

			# TODO
			""" implement non-render based lookup (but still using shader ins!)
			https://en.wikipedia.org/wiki/Point_in_polygon
			https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule
			https://en.wikipedia.org/wiki/Nonzero-rule
			https://stackoverflow.com/questions/6554313/algorithm-for-determining-whether-a-point-is-inside-a-3d-mesh
				-- what if we already have a per-axis listing of 'closed' ranges?  then check if within those ranges?
			XXX how to do text with font settings?
			and how to consider render states like clipping... maintain a 'pixel' ourselves?
			also, mesh points may be on gpu...
			"""

			ctx_data['depth'] = max_depth if max_depth is not None else ctx.MAX_RENDER_DEPTH
			assert ctx['depth'] <= ctx.MAX_RENDER_DEPTH, 'depth: {} exceeds limit: {}'.format(ctx['depth'], ctx.MAX_RENDER_DEPTH)

			mat = ctx['matrix'] = snap_matrix_t(*offset) if offset is not None else snap_matrix_t(*SNAP_IDENTITY_MATRIX)#offset if offset is not None else snap_matrix_t()

			ctx_data['current_container'] = None
			ctx_data['current_items'] = items
			ctx_data['render_mode'] = 'lookup'
			ctx_data['items_attr'] = 'lookup_items'

			ctx_data['only_first_lookup'] = SETTINGS.get('only_first_lookup', True)
			ctx_data['lookup_results'] = []

			# apply user position into matrix itself
			mat[3] = x
			mat[7] = y

			# save the initial offset so we can undo it later in the lookup_results
			initial_offset = snap_matrix_t(*mat)

			# now invert and add in user if applicable
			snap_matrix_invert(mat, mat)
			if offset is not None:
				snap_matrix_multiply(mat, offset, mat)

			# TODO set antialias to off by default? XXX do this when creating the lookup context in INIT
			# NOTE: this is the engine context for doing lookups, it is re-used
			#self.reset() # XXX do these outside, like draw requires...
			#self.clear()
			# make sure image format is RGBA?  or just always expect that to be true implicitly by using engine image?

			# NOTE: image changed data event should be sent in RESET, when rendering is considered complete
			# multiple draw/lookup calls can be made

			ctx.cmd_render_subitems()

			results = ctx_data['lookup_results']
			if results:
				# results = [graphic, offset_matrix, ...]
				for lookup_result in results:
					# undo the x,y position offset so coordinates are in their actual positions!
					offset = lookup_result['offset']
					snap_matrix_multiply(offset, initial_offset, offset)

			#ctx_data['lookup_results'] = None

			ctx.finish()

			return results

		def __init__(self, remap_coordinates=None, **SETTINGS):
			SnapNode.__init__(self)

			#data = self.data()

			#self.data['name'] = name
			#data['axes'] = axes

			"""
			if remap_coordinates is not None:
				raise NotImplementedError('remap_coordinates') # will be a matrix to redefine the coordinate space of the engine (without changing graphics orientation?)
			else:
				self.remap_coordinates = None # matrix if used
			"""

			# subclass needs to assign it's own types for these...
			# TODO these used to assign engine to self!
			# TODO assign onto base class here?  like self.Color._engine_ = self?

			# TODO this could probably be done better...?

			# TODO make dummy env to build into, then re-assign to local names...

			#ENV.__LOCAL_ENGINE__ = self # for build() calls of engine components to know which engine is their parent, this is internal

			#self.ENGINE = self # TODO weakref? XXX TODO ENV.ENGINE = self, and then switch it back?

			"""
			SnapMatrixModule.build(self)
			SnapMetricsModule.build(self)
			SnapContainerModule.build(self)
			SnapEngineDataModule.build(self)

			SnapColorModule.build(self)
			SnapGradientModule.build(self)
			SnapTextureModule.build(self)

			SnapPathModule.build(self)
			SnapMeshModule.build(self)
			SnapImageModule.build(self)
			SnapTextModule.build(self)

			SnapContextModule.build(self)

			SnapShaderModule.build(self)

			SnapProxyModule.build(self)

			SnapCameraModule.build(self)
			SnapWindowModule.build(self)
			"""

			# XXX if matrix and metrics are to be changed then the ones from the ENV should be swapped!
			#self.Matrix = ENV.SnapMatrix
			#self.Metrics = ENV.SnapMetrics
			#self.Container = ENV.SnapContainer
			self.EngineData = ENV.SnapEngineData

			self.Color = ENV.SnapColor
			self.Gradient = ENV.SnapGradient
			self.Texture = ENV.SnapTexture
			self.Spline = ENV.SnapSpline
			self.Mesh = ENV.SnapMesh
			self.Image = ENV.SnapImage
			self.Text = ENV.SnapText

			self.Context = ENV.SnapContext

			self.Shader = ENV.SnapShader
			# TODO CompositeShader, ParticleShader

			#self.Proxy = ENV.SnapProxy

			# XXX get these from ENV
			#self.Camera = ENV.SnapCamera
			#self.Window = ENV.SnapWindow


			self.Shape = self.PreferredShape = self.DefaultShape = self.Spline # mesh or path depending on engine preference, so user doesn't have to care if they don't need to...


			# TODO matrix to indicate orientation of engine?

			"""
			double one = 1;
			SnapNode lookup_image = (SnapNode)snap_event(self, "Image", "width", &one, "height", &one, "format", "RGBA", "pixels", NULL);

			double rgba[4] = {0,0,0,1};
			SnapNode fill_color = (SnapNode)snap_event(self, "Color", "RGBA", rgba);

			rgba[0] = .5; rgba[1] = .5; rgba[2] = .5;
			SnapNode line_color = (SnapNode)snap_event(self, "Color", "RGBA", rgba);

			snap_setattrs_SnapNodes(self,
				// just so defaults are listed after
				"__lookup_image__", lookup_image
				);

			snap_setattrs_SnapNodes(self,
				"default_fill_color", fill_color,
				"default_line_color", line_color
				);
			snap_setattrs(self,
				"default_style", "SOLID"
				);


			// TODO matrix to indicate "orientation" of engine (put on context?)
			"""

	ENV.SnapEngine = SnapEngine


