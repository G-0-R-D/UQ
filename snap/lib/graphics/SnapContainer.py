
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

	def snap_get_full_extents(CONTAINER, max_depth=None):

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

	ENV.snap_get_full_extents = snap_get_full_extents
		

	class SnapContainer(SnapMetrics):

		__slots__ = []

		# this is the basic graphical unit, it can draw using a shader pipeline, and have child elements 'inside' of it...

		#__slots__ = ['_children_', '_shader_',
		#	'_node_render_info_', # when added into node rendering scenes, it is wrapped in a SnapNodeDisplay() item, which is stored in local dict here {<scene>:SnapNodeDisplay(self)}
		#	]

		# TODO bring this back as a container that is expected to have a matrix and extents (but doesn't have to)
		#	-- and is expected to be renderable, providing ins list and children property
		#	-- note: this renderability is not node rendering (that is done by the task)

		# TODO provide matrix and extents properties that forward to matrix and metrics base types
		#	-- if they are None, then use identity for the operation, and only set if not identity in result
		#	-- also if None then ins does not queue transform commands...?  or should that just always be done?
		# TODO matrix is on shader?  or that one is an extra one?


		# TODO compose matrix and metrics methods instead of subclassing
		#	-- make a Transformable class for that


		# XXX shader.callback instead of separate items!  context can just walk container tree, reversing lookup, and checking for shader...  (if shader then we just pass the render to the shader...)
		# shader()
		# items() # or children()?
		# TODO put lookup intercept on shader?  shader forwards to the container?
		# full_extents()
		# then SnapIO api?  add,remove,insert,remove?  or just to __setitem__, __getitem__, __delitem__?
		# TODO lookup_intercept is an option on shader.cmd_lookup()?  does the override
		# -- lookup intercept is option enable/disable, pass dict to store the data?  and then rendering children defaults to true, but can be set false and custom child rendering can be done directly...

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

		# XXX this will be implemented as an event?  then we can accept it and we get the HUD to use?  handed from the window...
		"""
		@ENV.SnapProperty
		class focused_windows:

			# owning window can assign itself here, to 'lock in', at which point this module can use the window HUD...

			def get(self, MSG):
				"()->list(*SnapWindow)"
				return [wk() for wk in (self.__snap_data__['focused_windows'] or [])]

			def set(self, MSG):
				"(list(*SnapWindow))"
				# TODO assign as weakref,

		@ENV.SnapProperty
		class focused_window:

			def get(self, MSG):
				"()->SnapWindow"
				windows = self['focused_windows']
				return windows[0] if windows else None

			def set(self, MSG):
				"(SnapWindow!)"
				window = MSG.args[0]
				self['windows'] = [window]
		"""

		@ENV.SnapProperty
		class interactive:

			# lookup checks interactive status by default

			def get(self, MSG):
				'()->bool'
				return self.__snap_data__['interactive'] is not False # False only if assigned to be False

			def set(self, MSG):
				'(bool!)'
				state = MSG.args[0]
				if state is not None:
					self.__snap_data__['interactive'] = bool(state)
				else:
					del self.__snap_data__['interactive']

		# moved to SnapMatrix base
		#@ENV.SnapProperty
		#class render_matrix:
		#	# in case an operation needs to be performed (like SnapCamera does inversion here)
		#	def get(self, MSG):
		#		"""()->snap_matrix_t"""
		#		return self['matrix']

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
				"""(next_depth=int)->snap_extents_t"""
				return snap_get_full_extents(self)

			# set just assigns locally as normal

		@ENV.SnapProperty
		class visible_extents: # TODO rename to 'frustrum_culling'? or 'visible_frustrum' or something like that?

			# TODO this needs to follow the logic of frustrum culling...  pass frustrum data instead?

			def get(self, MSG):
				"()->snap_extents_t"
				#ENV.snap_warning("not implemented") # TODO
				return self.__snap_data__['visible_extents']

			def set(self, MSG):
				"(snap_extents_t!)"
				ext = MSG.args[0]
				if ext is not None:
					assert isinstance(ext, snap_extents_t), 'not an extents type: {}'.format(type(ext))
					self.__snap_data__['visible_extents'] = ext
				self.changed(visible_extents=ext)

		@ENV.SnapProperty
		class shader:

			def get(self, MSG):
				"()->SnapShader"
				return self.__snap_data__['shader']

			def set(self, MSG):
				"(SnapShader!)"
				shader = MSG.args[0]
				if shader is not None:
					assert isinstance(shader, ENV.SnapShader), 'not a shader type? {}'.format(type(shader))
				existing = self.__snap_data__['shader']
				self.__snap_data__['shader'] = shader
				if shader != existing:
					self.changed(shader=shader)


		"""
		def __getitem__(self, KEY):

			KEY, MSG = unpack_msg_from_key(KEY)

			if KEY == 'render_matrix':
				return self['matrix']

			elif KEY in ('items', 'render_items', 'lookup_items'):
				return self['children']

			elif KEY == 'engine':
				engine = self['__engine__']
				if engine is not None:
					return engine

				seen = set()

				L = [self]
				while L:

					check = L.pop(0) # Breadth First Search

					if check in seen:
						continue
					seen.add(check)

					shader = check['shader']
					if shader is not None:
						engine = shader['engine'] # TODO if container is in shader this could be a recursion error?
						if engine is not None:
							self['__engine__'] = engine
							return engine

					render_items = check['render_items']
					if render_items:
						L.extend(render_items)

				return None



			elif KEY == 'extents':

				next_depth = 1000 # TODO
				if MSG is not None:
					next_depth = MSG.unpack('max_depth', next_depth) - 1
				if next_depth < 0:
					return None

				# if extents are assigned it means the extents are known/cached, so just return them
				extents = SnapMetrics.__getitem__(self, 'extents')
				if extents is not None:
					return extents

				for item in self['children']:

					try:
						e = item['extents', SnapMessage(max_depth=next_depth)]
					except:
						continue

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

			value = SnapMetrics.__getitem__(self, KEY)

			if value is None:
				if KEY == 'children':
					''#value = self['children'] = SnapChildren()
					''#value.changed.listen(self.changed) # ?

			return value


		def __setitem__(self, KEY, VALUE):

			if KEY == 'children' and VALUE is not None:

				children = self['children']
				if children is None:
					children = self['children'] = SnapChildren()
					children.changed.listen(self.changed)

				children.set(*VALUE)

				return None

			return SnapMetrics.__setitem__(self, KEY, VALUE)
		"""

		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"
			#ENV.snap_out('unhandled device event', MSG.kwargs)


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

		@ENV.SnapChannel
		def set(self, MSG):
			"""(item=SnapNode?, items=list(*SnapNode)?, children=list?)"""
			return SnapMetrics.set(self, MSG)
			"""
			'items?' # args and kwargs

			# TODO handle shader here, forward item/items to self.children() to handle...

			for attr,value in MSG.kwargs.items():

				if attr in ('item', 'items'):
					self.children().set(**{attr:value})
					self.changed()
				else:
					SnapTransformable.set(self, **{attr:value})
			"""


		@ENV.SnapChannel
		def add(self, MSG):
			"""(*SnapNode, item=SnapNode?, items=list|tuple|SnapChildren(*SnapNode)?)"""

			if MSG.args:
				self['children'] = self['children'] + list(MSG.args)

			for attr,value in MSG.kwargs.items():
				if attr == 'item':
					self['children'].append(value)
				elif attr == 'items':
					self['children'] = self['children'] + value
				else:
					raise KeyError(attr)

		"""
		elif CHANNEL in ('add', 'remove', 'insert', 'append', 'extend', '__getitem__', '__setitem__', '__delitem__'):
			children = self.children()
			if children is not None:
				return children._(self, CHANNEL, MSG)
			raise NotImplementedError('no children?')
		"""




		"""
		def snap_draw(self, CTX):
			''
			# TODO just render CTX.cmd_render_subitems()

		def snap_lookup(self, CTX):
			''
			# TODO if self.interactive then do extents lookup?

			# TODO do lookup using sub-assignment (container?)  which is normal render, uses draw, but then we do the check after...

		def snap_lookup_intercept(self, CTX):
			# TODO move this to shader operation
			# just call this from snap_lookup() to use, this will claim a sub-interaction for itself

			saved_offset = snap_matrix_t(*CTX._matrix_)

			lookup_results = CTX._lookup_results_

			original_length = len(lookup_results)

			container = CTX.current_container

			SnapContainer.lookup(self, CTX)

			if len(lookup_results) > original_length:

				lookup_results.append((container, saved_offset))
		"""

		# TODO config:
		#	-- restore before / after
		#	-- interactive (lookup will function, default to extents) -- assign a container for the lookup rendering?
		#		-- also alpha threshold
		#	-- visible
		

		def full_extentsXXX(self, MSG):
			# (self, max_depth=None, consider_assigned=True, consider_shaders=True, run_to_end=False):

			# TODO full extents means call full_extents of each subitem, and if it is None then call extents?
			#	-- extents implementation should be specific with full_extents whenever possible...  and generalized to just call extents() on each subitem by default...
			# TODO include max_depth param for subcalls if not included, do subcalls with max_depth -1
			raise NotImplementedError('TODO what does full extents mean in new shader design?')

			max_depth, consider_assigned, consider_shaders, run_to_end = MSG.unpack(
				'max_depth', None, 'consider_assigned', True, 'consider_shaders', True, 'run_to_end', False)

			depth = max_depth if max_depth is not None else ENV.SnapContext_RENDER_MAX_DEPTH

			# here's the problem: extents don't have to be at 0, so we want the min and max of what IS assigned
			# which might not be 0.  If we start with 0 then SNAP_MIN(0, 1) will choose the 0, but the 1 would be
			# the real min if < 1 was never encountered... SO we allocate extents once they are used to know they
			# have been assigned (they exist completely or not at all; assigned as a set)
			extents = None # allocated once assigned

			if depth < 1:
				return extents

			# NOTE: don't consider own matrix, because queried extents are relative to self (inside own matrix space)
			offset = snap_matrix_t(*SNAP_IDENTITY_MATRIX)

			queue = [(depth, offset, self)]

			while queue:

				d, o, c = queue.pop(0)

				if consider_assigned:

					e = c.extents()
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
					# XXX TODO container.extents() will default to attempting to get extents from draw_program['extents']?
					shader = c.shader()
					if shader:
						# standard shader has just one shape, but shader could define extents any way it wants to; may have multiple shapes
						e = shader.extents()
						if e:
							e = snap_extents_t(*e)

							snap_matrix_map_extents(o, e, 0, e)
							if extents is None:
								extents = e
							else:
								snap_extents_mix(e, extents, extents)

				if d > 0:

					items = c.items()

					if items:
						for item in items:

							item_matrix = snap_matrix_t(*(item.matrix() or SNAP_IDENTITY_MATRIX))

							snap_matrix_multiply(o, item_matrix, item_matrix)
							queue.append((d-1, item_matrix, item))

			if extents is None:
				extents = snap_extents_t(0,0,0, 0,0,0)

			return extents




		def __bool__(self):
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
				self['children'] = self['children'] + items

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

