
# TODO similar to new dynamic event system, assets property leads to asset manager to easily keep track of a bunch of assets without having to define properties or just throw them into the children list...
#	-- could also handle ordering, layer swapping, and layout!  while making assets exchangable and identifiable by name
#	-- re-assigning asset should keep the original reference so we can recover the original by just passing 'asset'=True

def build(ENV):

	# TODO
	"""
	assets can be assigned by int index or str name
	asset manager is just api to assign to local data
	local data = ([render_items], {<named assigns>}, [<int assigns>])
	use __getitem__,__setitem__,__delitem__ for assign (by int or str)
	use set(*INT_STR) to set active render_items (missing are silently ignored?)
		-- set() with no args will just list indexed and then dict in original order...?
	"""

	SnapNode = ENV.SnapNode

	# TODO set(*names, **assigns) where names are render order, and assigns are assigning the graphics to the names...

	class SnapAssetManager(object):

		__slots__ = ['__parent__']

		def __getitem__(self, KEY):

			if isinstance(KEY, str):
				return self.named[KEY]
			elif isinstance(KEY, (int, slice)):
				return self.indexed[KEY]
			elif isinstance(KEY, tuple):
				# TODO assert no more tuples in key?
				assert not any([True for k in KEY if isinstance(k, tuple)]), 'nested tuples unsupported'
				return [self.__getitem__(k) for k in KEY]

			raise KeyError(KEY)

		def __setitem__(self, KEY, VALUE):

			if isinstance(KEY, str):
				self.named[KEY] = VALUE
			elif isinstance(KEY, int):
				self.indexed.insert(KEY, VALUE)
			elif isinstance(KEY, slice):
				'overwrite/insert'
			elif isinstance(KEY, tuple):
				for k in KEY:
					self.__setitem__(k, VALUE)

			else:
				raise KeyError(KEY)

		def __delitem__(self, KEY):
			
			if isinstance(KEY, str):
				del self.named[KEY]
			elif isinstance(KEY, (int, slice)):
				del self.indexed[KEY]
			elif isinstance(KEY, tuple):
				for k in KEY:
					self.__delitem__(k)
			else:
				raise KeyError(KEY)


		@property
		def assets(self):
			assets = self.__parent__.__snap_data__['__SnapAssetManager_assets__']
			if assets is None:
				# assets = ([<render items>], [<indexed items>], {<named items>})
				assets = self.__parent__.__snap_data__['__SnapAssetManager_assets__'] = ([],[],{})
			return assets

		@property
		def render_items(self):
			# returned can be edited directly...
			return self.assets[0]			

		@property
		def indexed(self):
			# returned can be edited directly...
			return self.assets[1]

		@property
		def named(self):
			# returned can be edited directly...
			return self.assets[2]

		@property
		def names(self):
			assets = self.__parent__.__snap_data__['__SnapAssetManager_assets__']
			if assets:
				return tuple(map(str, assets[2].keys()))
			else:
				return ()


		# TODO layouts as commands?  like pack() or layout_grid()?  which would act on just the visible elements?
		#	-- layouts would just require running a layout function on self.render_items...
		#	-- make layout functions that operate on *args...

		def set(self, *ANYTHING):
			# TODO allow this to accept just a list of any items, and then we use the internal item lists directly?
			# like assets.set(*assets.indexed + [assets.named.values()])
			# or assets.set(assets['a'], assets['b'], assets[0], assets[5:])
			assets = get_assets(self.__parent__)
			render_items,indexed,named = assets[0],assets[1],assets[2]

			if not ANYTHING:
				render_items[:] = indexed + list(named.values())
			else:
				'set or quietly ignore'
				
				render_items[:] = list(ANYTHING)

		def assign(self, *ORDERED, **NAMED):
			'name' # = graphic
			# TODO this is full replacement (previous entries overwritten)
			# removed ordered from render_items... XXX let that be a separate step, render_items don't have to be in the asset manager...

		def remove(self, *INTS_OR_NAMES):
			'unassigns / delete'
			# TODO also remove from render items if it is in there...

		def clear(self):
			try:
				del self.__parent__.__snap_data__['__SnapAssetManager_assets__']
			except:
				pass

		def __iter__(self):
			assets = self.__parent__.__snap_data__['__SnapAssetManager_assets__']
			if assets is not None:
				for indexed in assets[2]:
					yield indexed
				for named in assets[1].values():
					yield named
			

		def __len__(self):
			assets = self.__parent__.__snap_data__['__SnapAssetManager_assets__']
			if assets is not None:
				return len(assets[1]) + len(assets[2])
			return 0

		def __bool__(self):
			return self.__len__() > 0

		def __init__(self, PARENT):
			assert isinstance(PARENT, SnapNode), 'asset manager parent must be SnapNode'
			self.__parent__ = PARENT

	ENV.SnapAssetManager = SnapAssetManager



def main(ENV):

	SnapContainer = ENV.SnapContainer

	class Test(SnapContainer):

		@property
		def assets(self): # this will be implemented by default in SnapContainer
			return ENV.SnapAssetManager(self)

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			print('AssetManager:', self.assets.__parent__)

	ENV.__run_gui__(Test)


if __name__ == '__main__':
	import snap; main(snap.SnapEnv())

