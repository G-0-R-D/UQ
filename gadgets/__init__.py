
def build(ENV):

	class SnapGadgetsModule(object):

		def __getattr__(self, ATTR):
			existing = getattr(ENV, ATTR, None)
			if existing is None:
				raise NotImplementedError() # TODO load the mode if it's one of the gadgets, and then assign it to ENV and return it
				
	ENV.gadgets = SnapGadgetsModule()

