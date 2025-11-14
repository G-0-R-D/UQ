
from weakref import ref as weakref_ref

def build(ENV):

	SnapDeviceNode = ENV.SnapDeviceNode

	class SnapDeviceGroup(SnapDeviceNode):

		__slots__ = []

		# TODO __send_event__ stuff, or find a common baseclass other than SnapDeviceNode?  more basic?
		@SnapDeviceNode.children.shared
		class members: pass

		"""
		@ENV.SnapProperty
		class members:

			def get(self, MSG):
				"()->list(*SnapDeviceNode)"
				return (self.__snap_data__['members'] or [])[:]

			#def set(self, MSG):
			#	"(list(*SnapDeviceNode))"
			#	# TODO
			#	raise NotImplementedError()
		"""
				

		@ENV.SnapChannel
		def changed(self, MSG):
			"()"
			return SnapDeviceNode.changed(self, MSG)

		def add(self, *NODES):
			self['children'] = self['children'] + list(NODES)
			"""
			members = self.__snap_data__['members'] or []
			original_members = len(members)

			for INPUT in NODES:
				'node or group, add self to memberships'
				assert isinstance(INPUT, SnapDeviceNode), 'not a device node: {}'.format(repr(type(INPUT)))
				memberships = INPUT.__snap_data__['memberships'] or []
				INPUT.__snap_data__['memberships'] = [wk for wk in memberships if wk() is not None and wk() is not self] + [weakref_ref(self)]
				self.__snap_data__['members'] = [n for n in members if n is not INPUT] + [INPUT]
				#INPUT.changed.listen(self.changed)

			self.__snap_data__['members'] = members

			if len(members) != original_members:
				self.changed(members=members)
			"""

		def remove(self, *NODES):
			self['children'] = [n for n in self['children'] if n not in NODES]

			"""
			members = self.__snap_data__['members'] or []
			original_members = len(members)

			for INPUT in NODES:
				if not isinstance(INPUT, SnapDeviceNode):
					continue
				memberships = INPUT.__snap_data__['memberships'] or []
				INPUT.__snap_data__['memberships'] = [wk for wk in memberships if wk() is not None and wk() is not self]

				members = [n for n in members if n is not INPUT]

			if members:
				self.__snap_data__['members'] = members
			else:
				del self.__snap_data__['members']

			if len(members) != original_members:
				self.changed(members=members)
			"""

			

		def __repr__(self):
			return '<{}({}) @{}>'.format(self.__class__.__name__, repr(self['name']), hex(id(self)))

		def __init__(self, *children, **SETTINGS):
			SnapDeviceNode.__init__(self, *children, **SETTINGS)

			# NOTE: to prevent name collisions, recommend using lowercase names for inputs and then uppercase ones for groups
			assert self['name'] is not None, 'must provide a name for {}'.format(self.__class__.__name__)

			# TODO don't allow recursive groupings (a group cannot be inside of it's own groups, it must be linear)

			#if children:
			#	self.__snap_data__['members'] = self['members'] + children
			#self['members'] = None # input nodes that are in this group

			#self['groups'] = None # groups this group is a member of

	ENV.SnapDeviceGroup = SnapDeviceGroup
	return SnapDeviceGroup
