
# TODO abandon codes, make the keys identities string-based...?

from snap.os.devices.keymap import SNAP_KEYMAP # TODO move this into ENV.__build__, in __init__.py (add a build() to the bottom of keymap)

def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapKeymap(SnapNode):

		"""
		SNAP_KEYCODES = SNAP_KEYMAP.SNAP_KEYCODES
		SNAP_KEYCODES_LOOKUP = SNAP_KEYMAP.SNAP_KEYCODES_LOOKUP
		SNAP_SCANCODES = SNAP_KEYMAP.SNAP_SCANCODES
		SNAP_SCANCODES_LOOKUP = SNAP_KEYMAP.SNAP_SCANCODES_LOOKUP
		SNAP_KEYMAP = SNAP_KEYMAP.SNAP_KEYMAP

		def snap_keycode_to_name(self, KEYCODE):
			return SNAP_KEYMAP.SNAP_KEYCODES_LOOKUP.get(KEYCODE)

		def snap_name_to_keycode(self, NAME):
			return SNAP_KEYMAP.SNAP_KEYCODES_LOOKUP.get(NAME)

		def snap_scancode_to_name(self, SCANCODE):
			return SNAP_KEYMAP.SNAP_SCANCODES_LOOKUP.get(SCANCODE)

		def snap_name_to_scancode(self, NAME):
			return SNAP_KEYMAP.SNAP_SCANCODES_LOOKUP.get(NAME)

		def snap_number_to_string(self, NUMBER):
			return SNAP_KEYMAP.snap_number_to_string(NUMBER)

		"""

		def __init__(self):
			SnapNode.__init__(self)

			for attr in dir(SNAP_KEYMAP):
				if not attr.lower().startswith('snap'): continue
				setattr(self, attr, getattr(SNAP_KEYMAP, attr))


	ENV.SnapKeymap = SnapKeymap
	ENV.SNAP_KEYMAP = SnapKeymap()

if __name__ == '__main__':

	"""
	from snap.lib.core import SNAP_GLOBAL_ENV as ENV
	from snap.lib import extern
	extern.build(ENV)
	build(ENV)
	"""
