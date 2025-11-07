
# moved to own file cause I keep getting it confused with the SnapGuiWindowBase when it's at the top XD

def build(ENV):

	SnapWindow = ENV.SnapWindow

	snap_matrix_t = ENV.snap_matrix_t
	snap_extents_t = ENV.snap_extents_t
	snap_matrix_map_extents = ENV.snap_matrix_map_extents

	class SnapGuiDummyWindow(SnapWindow):

		# XXX instead of this, we just need to create a SnapContext for the ENV.GRAPHICS and then pass that to the user to use, with image already connected into it!
		# 	-- XXX except we want window behaviour at the toplevel...?  or do we?

		__slots__ = []

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"()->snap_extents_t"
				return SnapWindow.extents.get(self, MSG)

			def set(self, MSG):
				"(snap_extents_t!)"

				# TODO this needs to be nicer...
				cam_matrix = snap_matrix_t(*self['camera']['matrix'])
				ext = snap_extents_t(*MSG.args[0])
				#snap_matrix_invert(cam_matrix, cam_matrix)
				snap_matrix_map_extents(cam_matrix, ext, 0, ext)
				self['item']['extents'] = ext

				SnapWindow.extents.set(self, MSG)

		@ENV.SnapProperty
		class children:

			def set(self, MSG):
				"list(SnapNode)"
				SnapWindow.children.set(self, MSG)

				item = self['item']
				if item and getattr(item, 'parent_event', None):
					self['focus'] = item

				ENV.snap_out('now resize child to self?') # resize camera...

		@ENV.SnapProperty
		class matrixXXX:

			def get(self, MSG):
				"()->snap_matrix_t"
				return SnapWindow.matrix.get(self, MSG)

			def set(self, MSG):
				"(snap_matrix_t!)"

				SnapWindow.matrix.set(self, MSG)

				m = MSG.args[0]
				self['item']['matrix'] = m


		@ENV.SnapChannel
		def device_event(self, MSG):
			# TODO I think what needs to happen here is we need to replace the dummy window idea with passing a render context to the window that is ready to use...  (or just calling draw/lookup on user!)
			user = self['item']
			if user is not None:
				
				device = MSG.kwargs.get('device')
				if isinstance(device, ENV.SnapDevicePointer):
					#ENV.snap_debug('unhandled device event', MSG.kwargs.keys())
					cam = self['camera']#['inverted']
					msg = device.remap_event(MSG, cam)
				else:
					msg = MSG
				_return = user.device_event.__direct__(msg)
				if _return is True:
					return True

			return SnapWindow.device_event(self, MSG)

		@ENV.SnapChannel
		def allocateXXX(self, MSG):
			ENV.snap_debug("allocate", MSG)

			# there will only be one item; user
			items = self['items']
			if items:
				for item in items:
					item.allocate.__direct__(MSG)

			return SnapWindow.allocate(self, MSG)

		def __init__(self, **SETTINGS):
			SnapWindow.__init__(self, **SETTINGS)

			self.__snap_data__['__extents_needs_set__'] = True # so we can just resize user once


	ENV.SnapGuiDummyWindow = SnapGuiDummyWindow

