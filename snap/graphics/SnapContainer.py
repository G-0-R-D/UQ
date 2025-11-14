
from weakref import ref as weakref_ref

def build(ENV):

	SnapNode = ENV.SnapNode
	SnapMetrics = ENV.SnapMetrics

	SnapMessage = ENV.SnapMessage

	#SnapMatrix = ENV.SnapMatrix
	#SnapMetrics = ENV.SnapMetrics

	#GRAPHICS = ENV.GRAPHICS # preferred engine TODO

	snap_matrix_t = ENV.snap_matrix_t
	snap_extents_t = ENV.snap_extents_t
	SNAP_IDENTITY_MATRIX = ENV.SNAP_IDENTITY_MATRIX
	snap_extents_mix = ENV.snap_extents_mix
	snap_matrix_map_extents = ENV.snap_matrix_map_extents
	snap_matrix_multiply = ENV.snap_matrix_multiply

	snap_extents_are_null = ENV.snap_extents_are_null

	snap_list_set_items = ENV.snap_list_set_items
	snap_list_add_items = ENV.snap_list_add_items
	snap_list_insert_items = ENV.snap_list_insert_items

	"""
	def snap_get_full_extentsX(CONTAINER, max_depth=None):

		if max_depth is None:
			max_depth = 1000 # TODO
		elif max_depth < 1:
			return None

		# if extents are locally assigned it means the extents are known/cached, so just return them
		#extents = SnapMetrics.extents.get(self, SnapMessage())
		extents = CONTAINER.__snap_data__['extents']
		if extents is not None:
			return extents

		for item in CONTAINER['children'] or []:
			#ENV.snap_out('check item', self.__class__.__name__, item.__class__.__name__)

			try:
				e = snap_get_full_extents(item, max_depth=max_depth-1)
			except Exception as e:
				ENV.snap_print_exception(e)
				continue

			# TODO also attempt to get from shader?

			if e is None or snap_extents_are_null(e):
				continue

			offset = snap_matrix_t(*(item['matrix'] or SNAP_IDENTITY_MATRIX))

			e = snap_extents_t(*e)

			snap_matrix_map_extents(offset, e, 0, e)

			if extents is None:
				# here's the problem: extents don't have to be at 0, so we want the min and max of what IS assigned
				# which might not be 0.  If we start with 0 then SNAP_MIN(0, 1) will choose the 0, but the 1 would be
				# the real min if < 1 was never encountered... SO we allocate extents once they are used to know they
				# have been assigned (they exist completely or not at all; assigned as a set)
				extents = e
			else:
				snap_extents_mix(e, extents, extents)

		if extents is None:
			extents = snap_extents_t(0,0,0, 0,0,0)

		return extents
	"""

	#ENV.snap_get_full_extents = snap_get_full_extents

	def snap_get_full_extents(CONTAINER, max_depth=None, consider_assigned=True, consider_shaders=True, run_to_end=False):
	# (self, max_depth=None, consider_assigned=True, consider_shaders=True, run_to_end=False):

		# TODO full extents means call full_extents of each subitem, and if it is None then call extents?
		#	-- extents implementation should be specific with full_extents whenever possible...  and generalized to just call extents() on each subitem by default...
		# TODO include max_depth param for subcalls if not included, do subcalls with max_depth -1


		depth = max_depth if max_depth is not None else ENV.SnapContext.MAX_RENDER_DEPTH

		# here's the problem: extents don't have to be at 0, so we want the min and max of what IS assigned
		# which might not be 0.  If we start with 0 then SNAP_MIN(0, 1) will choose the 0, but the 1 would be
		# the real min if < 1 was never encountered... SO we allocate extents once they are used to know they
		# have been assigned (they exist completely or not at all; assigned as a set)
		extents = None # allocated once assigned

		if depth < 1:
			return extents

		# NOTE: don't consider own matrix, because queried extents are local to self (inside own matrix space)
		offset = snap_matrix_t(*SNAP_IDENTITY_MATRIX)

		queue = [(depth, offset, CONTAINER)]

		while queue:

			d, o, c = queue.pop(0)

			if consider_assigned:

				e = c.__snap_data__['extents'] # prevents recursion, but we also only want to consider assigned extents...
				if e:

					e = snap_extents_t(*e)

					snap_matrix_map_extents(o, e, 0, e)
					if extents is None:
						extents = e
					else:
						snap_extents_mix(e, extents, extents)

					if not run_to_end:
						# if an extents is assigned, then take that to be the extents of the container and all of it's subitems!
						# it should mean crop assigned the extents from the top down, and the container made sure it's own
						# internal metrics are correct!
						# aka. if extents is assigned to SnapContainer, it is taken as the size of all objects
						# in the remaining sub-tree
						break

			if consider_shaders:
				shader = c['shader']
				if shader:
					# standard shader has just one shape, but shader could define extents any way it wants to; may have multiple shapes
					e = shader['extents']
					if e:
						e = snap_extents_t(*e)

						snap_matrix_map_extents(o, e, 0, e)
						if extents is None:
							extents = e
						else:
							snap_extents_mix(e, extents, extents)

			if d > 0:

				items = c['children']

				if items:
					for item in items:

						item_matrix = snap_matrix_t(*(item['matrix'] or SNAP_IDENTITY_MATRIX))

						snap_matrix_multiply(o, item_matrix, item_matrix)
						queue.append((d-1, item_matrix, item))

		if extents is None:
			extents = snap_extents_t(0,0,0, 0,0,0)

		return extents

	ENV.snap_get_full_extents = snap_get_full_extents
		

	class SnapContainer(SnapMetrics):

		# this is the basic graphical unit, it can draw using a shader pipeline, and have child elements 'inside' of it...

		__slots__ = []

		"""
		@ENV.SnapProperty
		class extents:

			def set(self, MSG):
				"(snap_extents_t!)"
				ext = MSG.args[0]
				if ext is not None:
					assert isinstance(ext, snap_extents_t)
					e = snap_extents_t(*ext)
					if e[3] <= e[0]: e[3] = e[0]
					if e[4] <= e[1]: e[4] = e[1]
					if e[5] <= e[2]: e[5] = e[2]
					x,y = e[0],e[1]
					e[0] = e[1] = 0
					m = self.__snap_data__['matrix']
					if m is None:
						m = self.__snap_data__['matrix'] = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
					m[3] = x
					m[7] = y
					self.__snap_data__['extents'] = ext
				else:
					self.__snap_data__['extents'] = None
				self.changed(extents=ext)
		"""


		# moved to SnapMatrix base
		#@ENV.SnapProperty
		#class render_matrix:

		@ENV.SnapProperty
		class children:

			# NOTE: logic for scene management would be in the container when it is applicable...

			def get(self, MSG):
				"""()->list(*SnapNode)"""
				return (self.__snap_data__['children'] or [])[:]

			def set(self, MSG):
				"""(list|tuple(*SnapNode))"""

				# NOTE: there should be no duplicates, but we'll just assume they weren't added...
				
				assign = MSG.args[0] if MSG.args else None

				if assign:
					
					assert isinstance(assign, (list,tuple)), 'incorrect argument for children.set: {}'.format(type(assign))
					assign = list(assign)

					self.__snap_data__['children'] = assign
				else:
					self.__snap_data__['children'] = None
					assign = None

				self.changed(children=assign)

			def delete(self, MSG):
				"""()"""
				self.__snap_data__['children'] = None


		@children.shared
		class items: pass				

		@children.shared
		class render_items: pass

		@children.shared
		class lookup_items: pass

		@ENV.SnapProperty
		class item:

			def get(self, MSG):
				"""()->SnapNode"""
				children = self['children']
				if children:
					assert len(children) == 1, 'more than one item'
					return children[0]
				return None

			def set(self, MSG):
				"""(SnapNode!)"""
				self['children'] = [MSG.args[0]]


		@ENV.SnapProperty
		class engine:

			def get(self, MSG):
				"""()->SnapEngine"""

				# TODO but how does this get invalidated when children change?  listen to changed?
				#engine = SnapMetrics.engine.get(self, MSG)
				engine = self.__snap_data__['engine']
				if engine is not None:
					return engine
				
				seen = set()

				L = [self]
				while L:

					check = L.pop(0) # Breadth First Search
					if check is None:
						continue

					if id(check) in seen:
						continue
					seen.add(id(check))

					#shader = check['shader']
					#if shader is not None:
					#	engine = shader['engine'] # TODO if container is in shader this could be a recursion error?
					#	if engine is not None:
					#		#SnapMetrics.engine.set(self, SnapMessage(engine))
					#		break

					#engine = check['engine']
					#if engine is not None:
					#	break

					render_items = check['render_items']
					if render_items:
						L.extend(render_items)

				if engine is None:
					# if we don't find an engine then it's pretty safe to assume engine is ENV.GRAPHICS?
					engine = getattr(ENV, 'GRAPHICS', None)
				self.__snap_data__['engine'] = engine
				return engine


		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"""(int max_depth?, bool consider_containers?, bool consider_shaders?, bool run_to_end?)->snap_extents_t"""
				return snap_get_full_extents(self, **MSG.kwargs)

			# set just assigns locally as normal

		@ENV.SnapProperty
		class shader:

			def get(self, MSG):
				"()->SnapShader"
				return self.__snap_data__['shader']

			def set(self, MSG):
				"(SnapShader!)" # TODO does it need to be a shader type?  doesn't it just need draw/lookup?  this is just a delegation...
				shader = MSG.args[0]
				if shader is not None:
					assert isinstance(shader, ENV.SnapShader), 'not a shader type? {}'.format(type(shader))
				existing = self.__snap_data__['shader']
				self.__snap_data__['shader'] = shader
				if shader != existing:
					self.changed(shader=shader)



		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"
			#ENV.snap_out('unhandled device event', MSG.kwargs)

		@ENV.SnapChannel
		def window_event(self, MSG):
			"()"

			# NOTE: any parent can use this protocol, and this protocol should be considered 2-way, so parent
			# should listen to child window_event, for focus requests (move camera...), etc...

			action = None
			for attr,value in MSG.kwargs.items():
				if attr == 'action': action = value

			if action == 'focus':
				'' # notify that this object has focus, can register foreground or background elements...
				# fg,bg,extents of focus area?

				# TODO device_event.emit(action='focus', anim_curve='x')

			elif action == 'motion':
				'' # notify that the containing container has moved (useful for shake-type animations...)
				# local position and delta

			elif action == 'resize':
				'' # notify the parent is now a different size, treat this as a visibility event?  The parent might be far larger, but we can calculate if we're still 'onscreen' from this, without implicitly assigning extents...

			elif action == 'visibility':
				'' # separate from resize, because window might stay same size while camera moves...  this should describe a visible extents in local coordinates...

			else:
				ENV.snap_debug('unhandled window_event', repr(action), 'in', self.__class__.__name__)


		@ENV.SnapChannel
		def changed(self, MSG):
			"""()"""
			if MSG is not None and MSG.source is not self:
				shader = self['shader']
				if shader is not None:
					shader.update(self)

			return SnapMetrics.changed(self, MSG)

			
		def draw(self, CTX):

			# NOTE: CTX can be used here directly if render behaviour needs to be hard-coded and not user changeable via the program...

			shader = self['shader']

			if shader is not None:
				# NOTE: program responsible for calling CTX.cmd_render_subitems()
				return shader.draw(CTX)
			else:
				CTX.cmd_render_subitems()

			# send draw?

			return None

		def lookup(self, CTX):

			if self['interactive'] is False:
				return None

			shader = self['shader']

			if shader is not None:
				return shader.lookup(CTX)
			else:
				CTX.cmd_render_subitems()

			# send lookup?

			return None

		def lookup_intercept(self, CTX):
			# intercept a lookup for a subitem, and claim it for ourself
			# to use this in subclass just define lookup to call this instead:
			# def lookup(...):
			#	return self.lookup_intercept(...)
			# XXX now:
			# def render(self, MSG):
			#	CTX = MSG.args[0]
			#	if CTX.render_mode == 'lookup':
			#		return self.lookup_intercept.__direct__(MSG)
			#	else:
			#		return Container.render(self, MSG)
			# XXX or implement as special shader program assignable to lookup?

			saved_offset = snap_matrix_t(*CTX['matrix'])

			lookup_results = CTX['lookup_results']

			original_length = len(lookup_results)
			
			_return = SnapContainer.lookup(self, CTX)

			if len(lookup_results) > original_length:

				#CTX['lookup_results'] = lookup_results[:original_length] + [self, saved_offset] + lookup_results[original_length:]
				CTX['lookup_results'].insert(original_length, dict(graphic=self, offset=saved_offset))

			return _return



		def __bool__(self):
			# NOTE: not all widgets will think of themselves as False if they don't have children...
			return self is not None #bool(self['children'])

		def __iter__(self):
			children = self['children']
			if children:
				for child in children:
					yield child

		def __repr__(self):
			# cancel the matrix repr
			return SnapNode.__repr__(self)


		def __init__(self, *items, **SETTINGS):
			SnapMetrics.__init__(self, **SETTINGS)

			if items:
				self['children'] = items + self['children']

			#self['draw_program'] = None
			#self['lookup_program'] = None

			#self['__node_display__'] = None # list of graphics, one for each scene added to...
			#self['__node_render_info__'] = None # when containers are added to a task or program they are wrapped in a SnapNodeGraphic, and that is referenced along with the 'scene' it belongs in here... TODO

			# TODO self._scenes_ = {} # {Scene():SceneItem(self), ...} # when in node display...

			#SNAP_INIT(self, SETTINGS,
			#	'shader')

			#if items:
			#	self.set(items=items)

			#self.set(**{k:v for k,v in SETTINGS.items() if k in ('item','items')})


		"""
		def __snap_description__(self):
			d = SnapMetrics.__snap_description__(self)
			d.update({
				'render':SnapEvent('(SnapContext)', required=[0], output=SnapOutput('(SnapContext)', required=[0])),
			})
			return d
		"""



	ENV.SnapContainer = SnapContainer



