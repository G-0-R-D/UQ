
# TODO similar to new dynamic event system, assets property leads to asset manager to easily keep track of a bunch of assets without having to define properties or just throw them into the children list...
#	-- could also handle ordering, layer swapping, and layout!  while making assets exchangable and identifiable by name
#	-- re-assigning asset should keep the original reference so we can recover the original by just passing 'asset'=True

def build(ENV):

	SnapNode = ENV.SnapNode

	# TODO set(*names, **assigns) where names are render order, and assigns are assigning the graphics to the names...

	class SnapAssetManager(SnapNode):

		__slots__ = []

		# TODO layer property, assign current layer XXX don't need layers in manager, just set() to visible names, layers can be managed aside from that...

		# TODO visible property?  assign names?  or items?

		# TODO layouts?

		def __getattr__(self, ATTR):
			'get from dict'

		def __setattribute__(self, ATTR, VALUE):
			'assign'

		def __delattr__(self, ATTR):
			'remove'

		# TODO use the item api as well?

		@ENV.SnapProperty
		class layout:
			'' # TODO assign a layout?  just a 'style'?  like 'grid' or something like that?  user can always do layout themselves on size change, while referencing assets...

		@ENV.SnapProperty
		class active:
			'' # TODO assign active names?

		def assign(self, **ASSIGNS):
			'name' # = graphic

		def remove(self, *NAMES):
			'unassigns / delete'

		def delete(self, *NAMES):
			''

		def clear(self):
			'clear all names'

		def set(self, *NAMES, **ASSIGNS):
			''

		def __init__(self):
			SnapNode.__init__(self)
			# TODO just store lists of names (layers), and then access from the assigns dict on render...

	ENV.SnapAssetManager = SnapAssetManager



def main(ENV):

	SnapContainer = ENV.SnapContainer

	class Test(SnapContainer):

		@property
		def assets(self): # this will be implemented by default in SnapContainer
			am = self.__snap_data__['__asset_manager__']
			if am is None:
				am = self.__snap_data__['__asset_manager__'] = ENV.SnapAssetManager()
			return am

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			print('AssetManager:', self.assets)

	ENV.__run_gui__(Test)


if __name__ == '__main__':
	import snap; main(snap.SnapEnv())

