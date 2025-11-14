
from weakref import ref as weakref_ref

"""
from snap.lib.os.devices import (
	SnapDeviceNode as SnapDeviceNodeModule,
	SnapDeviceInput as SnapDeviceInputModule,
	SnapDeviceGroup as SnapDeviceGroupModule,
	)
"""

def build(ENV):

	SnapMessage = ENV.SnapMessage

	SnapNode = ENV.SnapNode
	SnapDeviceNode = ENV.SnapDeviceNode
	SnapDeviceGroup = ENV.SnapDeviceGroup

	snap_binary_search = ENV.snap_binary_search

	class SnapDevice(SnapDeviceNode):

		__slots__ = []

		@ENV.SnapProperty
		class category:
			# category is just a parent of the device

			def get(self, MSG):
				"""()->SnapDeviceCategory"""
				seen = set()
				QUEUE = self['parents'] or []
				while QUEUE:
					parent = QUEUE.pop(0)
					if id(parent) in seen:
						continue
					seen.add(id(parent))

					if isinstance(parent, ENV.SnapDeviceCategory):
						return parent

					parents = parent['parents']
					if parents:
						QUEUE.extend(parents)

		@ENV.SnapProperty
		class device:

			def get(self, MSG):
				"()->SnapDevice"
				return self


		@ENV.SnapChannel
		def changed(self, MSG):
			"""()"""
			node = MSG.source
			return SnapDeviceNode.changed(self, MSG)

		
		def __init__(self, **SETTINGS):
			SnapDeviceNode.__init__(self, **SETTINGS)

			# TODO mechanism for grouping shared names?  so we can find all related inputs through any other input with same name?

	ENV.SnapDevice = SnapDevice


