
from weakref import ref as weakref_ref

def build(ENV):

	ENV.__build__('snap.lib.os.devices.snap_device_util')

	ENV.__build__('snap.lib.os.devices.SnapDeviceNode')
	ENV.__build__('snap.lib.os.devices.SnapDeviceInput')
	ENV.__build__('snap.lib.os.devices.SnapDeviceGroup')

	ENV.__build__('snap.lib.os.devices.SnapDevice')

	if 1:
		ENV.__build__('snap.lib.os.devices.SnapKeymap')
		ENV.__build__('snap.lib.os.devices.SnapDeviceKeyboard')

		ENV.__build__('snap.lib.os.devices.SnapDevicePointer')


		SnapNode = ENV.SnapNode
		SnapDeviceNode = ENV.SnapDeviceNode
		SnapDevice = ENV.SnapDevice

		class SnapDeviceCategory(SnapNode):

			__slots__ = []

			#def name(self, MSG):
			#	return self.data()['name']

			#def devices(self, MSG):
			#	return self.data()['devices'][:]

			@ENV.SnapProperty
			class name:

				def get(self, MSG):
					"""()->str"""
					return self.__snap_data__['name']

			@ENV.SnapProperty
			class devices:

				def get(self, MSG):
					"""()->list(*SnapDevice)"""
					return [d for d in (self.__snap_data__['devices'] or [])]

			"""
			def device_event(self, MSG): # XXX use __getitem__ instead?
				index = MSG.unpack('index',0)
				try:
					return self['devices'][index]
				except:
					return None

			def __getitem__(self, KEY):
				VALUE = SnapNode.__getitem__(self, KEY)
				if VALUE is not None and KEY == 'devices':
					VALUE = VALUE[:] # copy
				return VALUE
			"""

			@ENV.SnapChannel
			def device_event(self, MSG):
				''

			def add(self, *DEVICES):

				devices = self.__snap_data__['devices'] or []

				for device in DEVICES:

					if not isinstance(device, SnapDevice):
						ENV.snap_warning('cannot add non-device({}) to category({})'.format(device, self['name']))
						continue

					if device in devices:
						ENV.snap_debug('device already added to', self['name'], device)
						continue

					if device['category']:
						if device['category'] is not self:
							ENV.snap_warning('device already registered with different category?', self['name'], device)
						continue

					parents = device['parents'] or []
					if self not in parents:
						parents.append(self)
					device.__snap_data__['parents'] = [weakref_ref(p) for p in parents]

					devices.append(device)

				self.__snap_data__['devices'] = devices

			def __getitem__(self, KEY):
				if isinstance(KEY, (int,slice)):
					return (self.__snap_data__['devices'] or [])[KEY]
				return SnapNode.__getitem__(self, KEY)

			def __iter__(self):
				for device in (self.__snap_data__['devices'] or []):
					yield device

			def __bool__(self):
				return bool(self.__snap_data__['devices'])

			def __len__(self):
				devices = self.__snap_data__['devices']
				if devices is not None:
					return len(devices)
				return 0

			def __init__(self, name=None):
				SnapNode.__init__(self)

				assert name is not None, 'category name must be string'
				self.__snap_data__['name'] = name
				self.__snap_data__['devices'] = []

		ENV.SnapDeviceCategory = SnapDeviceCategory


		class SnapDevices(SnapNode):

			__slots__ = []

			#def categories(self, MSG):
			#	return self.data().get('categories')

			@ENV.SnapProperty
			class keyboards:

				def get(self, MSG):
					"""()->SnapDeviceCategory(*SnapDevice)"""
					cat = (self.__snap_data__['categories'] or {}).get('keyboards')
					if cat is None:
						cat = self.__snap_data__['categories']['keyboards'] = SnapDeviceCategory(name='keyboards')
					return cat

			@ENV.SnapProperty
			class keyboard:

				def get(self, MSG):
					"""()->SnapDevice"""
					keyboards = self['keyboards']
					if keyboards:
						return keyboards[0]
					return None

			@ENV.SnapProperty
			class pointers:

				def get(self, MSG):
					"""()->SnapDeviceCategory(*SnapDevice)"""
					cat = (self.__snap_data__['categories'] or {}).get('pointers')
					if cat is None:
						cat = self.__snap_data__['categories']['pointers'] = SnapDeviceCategory(name='pointers')
					return cat

			@pointers.shared
			class mice: pass

			@ENV.SnapProperty
			class pointer:

				def get(self, MSG):
					"""()->SnapDevice"""
					pointers = self['pointers']
					if pointers:
						return pointers[0]
					return None

			# TODO tablets is pointers with touch?  check pointers for pressure?

			@pointer.shared
			class mouse: pass

			@ENV.SnapProperty
			class gamepads:

				def get(self, MSG):
					"""()->SnapDeviceCategory(*SnapDevice)"""
					cat = (self.__snap_data__['categories'] or {}).get('gamepads')
					if cat is None:
						cat = self.__snap_data__['categories']['gamepads'] = SnapDeviceCategory(name='gamepads')
					return cat

			@ENV.SnapProperty
			class devices:

				def get(self, MSG):
					"""()->list(*SnapDevice)"""
					return [d for d in cat for s,cat in (self.__snap_data__['categories'] or {}).items()]

			@ENV.SnapProperty
			class categories:

				def get(self, MSG):
					"""()->list(*SnapDeviceCategory)"""
					return (self.__snap_data__['categories'] or {}).values()

			@ENV.SnapChannel
			def get(self, MSG):
				"""(name=str!, index=int?)->SnapDevice"""
				name,index = MSG.unpack('name', None, 'index', 0)
				if name is None:
					return None
				cat = (self.__snap_data__['categories'] or {}).get(name)
				if cat:
					return cat[index]

			def __init__(self):
				SnapNode.__init__(self)

				if self.__snap_data__['categories'] is None:
					self.__snap_data__['categories'] = {}

				categories = self.__snap_data__['categories']

				# TODO this should just get a list of all devices and connect to them ideally...
				if not self['keyboard']:
					self['keyboards'].add(ENV.SnapDeviceKeyboard(name='default_keyboard'))
				if not self['pointer']:
					self['pointers'].add(ENV.SnapDevicePointer(name='default_pointer'))

		ENV.SnapDevices = SnapDevices

		ENV.DEVICES = SnapDevices()

def main(ENV):

	# make a fake device and test it's events

	class User(ENV.SnapNode):

		def device_event(self, MSG):
			ENV.snap_out(MSG.source, MSG.channel, MSG)

		def node_event(self, MSG):
			ENV.snap_out(MSG.source, MSG.channel, MSG)

		def group_event(self, MSG):
			ENV.snap_out(MSG.source, MSG.channel, MSG)


	class Device(ENV.SnapDevice):

		def __init__(self):
			ENV.SnapDevice.__init__(self)

			for idx,base in enumerate((ENV.SnapDeviceInputButton,)):#, ENV.SnapDeviceInputAxis)):
				i = base(code=idx, name=base.__name__)
				# TODO make a group for each input as well
				g = ENV.SnapDeviceGroup(name=(base.__name__ + '_group').upper())
				g['children'] = [i]
				self['children'] = [g]

			# TODO make a group of the groups

			# TODO add to fake category, check for event


	user = User()
	
	fake_device = Device()

	QUEUE = [(0,fake_device)]
	while QUEUE:
		depth,node = QUEUE.pop(0)

		print('.' * depth, node.__class__.__name__)

		children = node['children']
		if children:
			QUEUE.extend([(depth+1,n) for n in children])


