
class SnapEnv(object):

	def __getattr__(self, ATTR):
		
		try:
			return getattr(self.__PRIVATE__['parent'], ATTR)
		except:
			raise AttributeError(ATTR)

	def __init__(self, parent=None):

		if parent is not None:
			assert isinstance(parent, SnapEnv), 'SnapEnv parent must be SnapEnv'

		self.__PRIVATE__ = dict(
			parent=parent,
		)
		

		'' # TODO __bytes__ will be used to store stack info efficiently, we'll make a struct!  TODO define in core/snap_types.h

