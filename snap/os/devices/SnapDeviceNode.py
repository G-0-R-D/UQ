
from weakref import ref as weakref_ref
from collections import OrderedDict

def build(ENV):

	"""
	if SNAP_DEBUG_ALL or (SNAP_DEBUG and SNAP_DEBUG_DEVICES):
		SNAP_DEBUGGING_DEVICES = True
		snap_debug_devices = snap_debug
	else:
		snap_debug_devices = lambda *args: None
	snap_debug_device = snap_debug_devices
	"""

	SnapNode = ENV.SnapNode
	SnapMessage = ENV.SnapMessage

	snap_time = ENV.snap_time

	snap_binary_search = ENV.snap_binary_search

	class SnapDeviceNode(SnapNode):

		__slots__ = []

		#def __getattribute__(self, ATTR):
		#	return SnapNode.__getattribute_strict__(self, ATTR)

		# TODO ENV.SnapProperty -> interaction = list of elements actively interacting with node (like button for drag event)
		#	-- include json descriptions of the interaction?

		@ENV.SnapProperty
		class last_time:

			def get(self, MSG):
				"""()->float"""
				return self.__snap_data__['last_time'] or 0.

			# set not in user space
			"""
			def set(self, MSG):
				"(float!)"
				value = MSG.args[0]
				if value is not None:
					value = float(value)
				else:
					value = 0. # TODO snap_time()?
				self.__snap_data__['last_time'] = value
				#self.changed(time=value)
			"""

		@last_time.shared
		class time: pass

		@ENV.SnapProperty
		class name:

			def get(self, MSG):
				"""()->str"""
				return self.__snap_data__['name']

		"""
		@ENV.SnapProperty
		class code:

			def get(self, MSG):
				"()->int"
				return -1 # only inputs have codes

		@ENV.SnapProperty
		class value:

			def get(self, MSG):
				"()->float"
				return 0.0 # only inputs have values, but 0.0 is common default...
		"""

		@ENV.SnapProperty
		class memberships:

			def get(self, MSG):
				"""()->list(*SnapDeviceGroup)"""
				return [p for p in (self['parents'] or []) if isinstance(p, ENV.SnapDeviceGroup)]
				#return [wk() for wk in (self.__snap_data__['memberships'] or [])]

			# TODO make this an internal access performed by group, this shouldn't be user accessible
			"""
			def set(self, MSG):
				# TODO
				# assume group will add the node to it's own members
				if VALUE:
					groups = self['memberships'] # weakrefs de-referenced by getitem
					for group in VALUE:
						assert isinstance(group, ENV.SnapDeviceGroup), 'not a group type {}'.format(repr(type(group)))
						if group not in groups:
							groups.append(group)
					return SnapNode.__setitem__(self, KEY, [weakref_ref(g) for g in groups])	
			"""

		@ENV.SnapProperty
		class children:

			def get(self, MSG):
				"""()->list(*SnapDeviceNode)"""
				d = self.__snap_data__['children']
				if not d:
					return []
				else:
					return list(d.values())

			def set(self, MSG):
				"""(list(*SnapDeviceNode))"""

				children = MSG.args[0]
				if not children:
					children = []

				assert all([isinstance(c, SnapDeviceNode) and c['name'] is not None for c in children]), 'children of device nodes must be SnapDeviceNode with a name'

				previous_children = self.__snap_data__['children']

				new_children = OrderedDict()

				seen = set()
				for child in children:
					if id(child) in seen:
						continue
					seen.add(id(child))

					child.changed.listen(self.changed)

					parents = child['parents']
					if parents:
						if self not in parents:
							child.__snap_data__['parents'] = child.__snap_data__['parents'] + [weakref_ref(self)]
					else:
						child.__snap_data__['parents'] = [weakref_ref(self)]

					name = child['name']
					assert name is not None and name not in new_children, 'name already in use! {}'.format((name, self))
					new_children[name] = child

				self.__snap_data__['children'] = new_children

				if previous_children:
					for child in previous_children.values():
						if id(child) not in seen:
							child.__snap_data__['parents'] = [weakref_ref(p) for p in child['parents'] if p is not self]
							child.changed.ignore(self.changed)

				#device = self['device']
				#if device is not None:
				#	device.unregister(self)
				#	device.register(self)

		@ENV.SnapProperty
		class parents:

			def get(self, MSG):
				"()->list(*SnapDeviceNode)"
				return [wk() for wk in (self.__snap_data__['parents'] or [])]

			# set not in user domain, done by children.set

		@ENV.SnapProperty
		class device:

			def get(self, MSG):
				"""()->SnapDevice"""

				seen = set()
				QUEUE = self['parents'] or []
				while QUEUE:
					parent = QUEUE.pop(0)
					if id(parent) in seen:
						continue
					seen.add(id(parent))

					if isinstance(parent, ENV.SnapDevice):
						return parent

					parents = parent['parents']
					if parents:
						QUEUE.extend(parents)

		@ENV.SnapProperty
		class interact_info:

			def get(self, MSG):
				'()->dict'
				return self.__snap_data__['interact_info'] or {}


			def set(self, MSG):
				'(dict!)'

				info = MSG.args[0]
				if info is not None:
					assert isinstance(info, dict)# and all([key in ('window','graphic','graphic_offset') for key in info.keys()])

					d = {}
					d.update(self.__snap_data__['interact_info'] or {})
					d.update(info)
					d = {k:v for k,v in d.items() if v is not None} # if None then remove
					if d:
						self.__snap_data__['interact_info'] = d
					else:
						del self.__snap_data__['interact_info']
				else:
					del self.__snap_data__['interact_info']
				self.changed(interact_info=self.__snap_data__['interact_info'])

			def delete(self, MSG):
				if MSG.kwargs or MSG.args:
					'delete just what is declared True?'
					raise NotImplementedError()
				else:
					self.__snap_data__['interact_info'] = None

		"""
		def __getitem__(self, KEY):

			if KEY == 'time':
				KEY = 'last_time'

			value = SnapNode.__getitem__(self, KEY)
			if value is not None and KEY == 'device':
				return value() # weakref de-reference
			if value is None:
				# TODO this kind of logic should be assigned to property info, as 'default' type or callable if assigned?
				#if KEY in ('parents','children'):
				#	value = []
				if KEY == 'last_time':
					value = 0.
				elif KEY == 'code':
					value = -1 # only inputs have codes
				elif KEY == 'value':
					value = 0.0 # only inputs have values, but 0.0 is common default...
				elif KEY == 'memberships':
					return []

			else:
				if KEY == 'memberships':
					value = [wk() for wk in value] # de-reference weakrefs before returning to user...
			return value
		"""

		"""
		def __setitem__(self, KEY, VALUE):

			# TODO set interaction object?

			if KEY == 'name':

				if VALUE != self['name']:
					SnapNode.__setitem__(self, 'name', VALUE)
					self.changed.send(name=VALUE) # device will get this and update

				return None

			elif KEY == 'code':
				# only inputs have codes, this is re-implemented there
				raise TypeError('not a coded input', self, VALUE)

			elif KEY == 'value':
				raise ValueError('input does not implement value', self)

			elif KEY == 'device':

				current_device = self['device']

				if current_device is not None and current_device != VALUE:
					current_device.unregister(self)

				#if VALUE is not None and id(self) not in VALUE['_inputs_by_id_']:
				#	# value is a device
				#	VALUE.register(self)

				if VALUE is not None:
					VALUE = weakref_ref(VALUE)

				return SnapNode.__setitem__(self, 'device', VALUE)

			elif KEY == 'memberships':
				# assume group will add the node to it's own members
				if VALUE:
					groups = self['memberships'] # weakrefs de-referenced by getitem
					for group in VALUE:
						assert isinstance(group, ENV.SnapDeviceGroup), 'not a group type {}'.format(repr(type(group)))
						if group not in groups:
							groups.append(group)
					return SnapNode.__setitem__(self, KEY, [weakref_ref(g) for g in groups])		

			elif KEY == 'time':
				KEY = 'last_time'
				VALUE = float(VALUE) if VALUE is not None else VALUE #snap_time()

			return SnapNode.__setitem__(self, KEY, VALUE)
		"""

		@ENV.SnapChannel
		def device_event(self, MSG): pass

		@ENV.SnapChannel
		def generate_event(self, MSG):
			raise NotImplementedError('generate_event() must be implemented in subclass')


		"""
		def walk(self, MSG):

			dfs = MSG.unpack('dfs', True)

			QUEUE = [[[],self]]
			while QUEUE:
				root,node = QUEUE.pop(0)

				yield root,node

				if not root:
					# can be cleared during yield (del root[:]) to prevent crawling in a certain direction...
					continue

				next_root = root + [node]
				if dfs:
					QUEUE = QUEUE + [[root, child] for child in node['children']]
				else:
					QUEUE = [[root, child] for child in node['children']] + QUEUE
		"""


		@ENV.SnapChannel
		def get(self, MSG):
			"""(*int|str!)->SnapDeviceNode"""

			assert not MSG.kwargs, 'kwargs not supported'
			assert MSG.args, 'no term'

			KEY = MSG.args[0]
			SUBTERM = MSG.args[1:]

			"""
			device = self['device']
			if device is not None:

				if isinstance(KEY, int):
					return (device.__snap_data__['__inputs_by_code__'] or {}).get(KEY)

				elif isinstance(KEY, str):
					result = (device.__snap_data__['__inputs_by_name__'] or {}).get(KEY)
					if result is not None:
						return result
					return (device.__snap_data__['__groups__'] or {}).get(KEY) # groups can't have same name as another input

				elif KEY is None:
					return None

				else:
					raise KeyError('invalid key:', repr(KEY))

			else:
				'full tree walk?' # TODO full *term? if *term is provided then do a walk?
			"""

			match = None

			children = self.__snap_data__['children']
			if children:

				try:
					if isinstance(KEY, int):
						# NOTE: this is by index, has nothing to do with scan/codes
						match = list(children.values())[KEY]
					elif isinstance(KEY, str):
						match = children[KEY]
					else:
						raise KeyError(repr(KEY))
				except Exception as e:
					#ENV.snap_warning('no key', KEY)
					pass # soft get() like dict.get()

				if SUBTERM and match:
					return match.get(*SUBTERM)

			return match
		
		def findXXX(self, MSG):
			# XXX use self['device'].input(key) or .group(key)

			KEY = MSG.unpack('key', None)
			assert KEY is not None, 'key must not be None'

			device = self['device']
			if device is not None:
				node = device.find.__direct__(MSG)
				if node is not None:
					return node

			return None
			"""
			if isinstance(KEY, str):
				def do_compare(key,node):
					return key == node['name']

			elif isinstance(KEY, int):
				def do_compare(key,node):
					return key == node['code']

			elif isinstance(KEY, SnapDeviceNode):
				def do_compare(key,node):
					return id(key) == id(node)
			else:
				raise KeyError('unknown key type', repr(type(KEY)))

			for root in self.walk():
				if do_compare(KEY, root[-1]):
					return root[-1]

			raise ValueError('not found', repr(KEY))
			"""

		#get = search = find

		"""
		def input_in_use(self, MSG):

			INPUT = MSG.unpack('input', None)

			device = self['device']
			if device is None:
				return False

			return id(INPUT) in device['_inputs_by_id_']
		"""

		def __compare__XXX(self, OTHER):

			# -1 = self is left/before OTHER, 1 = self is right/after OTHER, 0 = equal/same

			if OTHER is self:
				return 0

			elif isinstance(OTHER, SnapDeviceNode):
				'get code and name'
				code = self['code']
				other_code = OTHER['code']
				if code is not None or other_code is not None:
					if code is not None and other_code is not None:
						if code < other_code: return -1
						elif code > other_code: return 1
						else: return 0
					elif code is None:
						return 1
					else: # other_code is None
						return -1

				name = self['name']
				other_name = OTHER['name']
				if name is not None or other_name is not None:
					if name is not None and other_name is not None:
						if name < other_name: return -1
						elif name > other_name: return 1
						else: return 0
					elif name is None:
						return 1
					else: # other_name is None
						return -1

			id_self = id(self)
			id_other = id(OTHER)
			if id_self < id_other: return 1
			elif id_self > id_other: return -1
			else: return 0

		"""
		def add(self, MSG):

			for attr,value in MSG.kwargs.items():

				if attr == 'group':
					self.add(groups=[value])

				elif attr == 'groups':

					if not value:
						continue

					self['groups'] = self['groups'] + value

				else:
					raise AttributeError(attr)


		def remove(self, MSG):

			for attr,value in MSG.kwargs.items():
				if attr == 'group':
					self.remove(groups=[value])

				elif attr == 'groups':

					if not value:
						continue

					self['groups'] = [i for i in self['groups'] if i not in value]

				else:
					raise AttributeError(attr)
		"""
		def __iter__(self):
			children = self['children']
			if children:
				for child in children:
					yield child

		def __repr__(self):
			return '<{} {}>'.format(self.__class__.__name__, hex(id(self)))

		def __init__(self, *CHILDREN, name=None, children=None, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			#SnapNode.__setitem__(self, 'name', None) # keyboard blocks setting name, but I like initting here
			#self['device'] = None # device reference for fast lookup, inputs must be 'owned' by a single device
			#self['memberships'] = None # list of group instances this node is a member of (acts as parents, but it is a tagging system)

			# XXX ditch parent/child tree structure for flat input lists (by code, by name) and group tags (parents are groups)
			#self['parents'] = []#set() # parent inputs or groups XXX set() requires hashable type
			#self['children'] = []#set() # subordinate inputs or groups
			# TODO also have children by code of just the children
			#self['last_time'] = 0 # snap_time() of last event (NOTE: not set by emit calls, must be set before)
			#self['__interact_info__'] = None # SnapDeviceInteractInfo instance to manage interaction information for a device, if assigned

			if name is not None:
				self.__snap_data__['name'] = str(name)
			#if code is not None:
			#	self.__snap_data__['code'] = int(code)
			#if value is not None:
			#	self.__snap_data__['value'] = float(value)

			self.__snap_data__['last_time'] = snap_time()

			if CHILDREN:
				self['children'] = CHILDREN

			if children:
				self['children'] += children

			#if device is not None:
			#	self['device'] = device

			#defaults = {k:v for k,v in SETTINGS.items() if k in (
			#	#"group", "groups",
			#	"name", "device",)}
			#defaults['time'] = SETTINGS.get('time', snap_time())

			#self.set(**defaults)

			#XXX put interact graphic data in GUI.INTERACT
			#interact_graphic, /*gui-assigned reference to graphic being interacted with by input (like mouse button drag)*/\
			#interact_offset /*gui-assigned matrix for when object interaction is initialized (graphic space from root when found)*/
			# TODO make interact offset an object so it can be updated and known everywhere?  if parent changes during drag we can update it in place?



	ENV.SnapDeviceNode = SnapDeviceNode

