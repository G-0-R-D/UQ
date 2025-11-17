
# https://www.berrange.com/tags/gtkvnc/
# https://github.com/rust-windowing/winit/issues/753

import os
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import * # Qt

from weakref import ref as weakref_ref

THISDIR = os.path.realpath(os.path.dirname(__file__))

CONFIG_FILE = os.path.join(THISDIR, 'config/SnapDeviceKeyboard.json')


def build(ENV):

	SnapNode = ENV.SnapNode
	SnapMessage = ENV.SnapMessage

	#SnapEvent = ENV.SnapEvent

	#snap_keycode_to_name = ENV.snap_keycode_to_name
	SnapDeviceInputButton = ENV.SnapDeviceInputButton
	SnapDeviceGroup = ENV.SnapDeviceGroup
	SnapDevice = ENV.SnapDevice


	def load_keymap(FILE):
		# if SNAP_KEYMAP.json is missing then generate a new one from Qt keynames

		if not os.path.exists(FILE):

			seen = set()
			unique_keys = []
			for attr in dir(Qt):
				if not attr.lower().startswith('key_'): continue
				if attr == 'Key_Any': continue # same value as spacebar, we'll use spacebar...
				value = getattr(Qt, attr)
				assert value not in seen, 'duplicate Qt key? {}'.format(repr(attr))
				seen.add(value)
				unique_keys.append(attr)
				

			KEYMAP = {qtname[len('key_'):]:{"Qt":qtname} for qtname in unique_keys}
			with open(FILE, 'w') as openfile:
				config = {'keymap':KEYMAP} # so we can store other config as well...  futureproof :)
				openfile.write(json.dumps(config, indent=4))
		else:
			with open(FILE, 'r') as openfile:
				config = json.loads(openfile.read())
				KEYMAP = config['keymap']

		"""
		just go through, find all entries with scan codes and register them ahead for disambiguation
			-- make a dict of 'resolve by scan code' Qt name: identity, then if we encounter name in there, it must resolve (None scan code is okay)
		then go through and if we have a scan code or a collision, disambiguate (assign scan code dict) 

		or on first pass just register Qtname:[entries] and then find those that have multiple entries that are unresolvable...
		"""

		# just verify that all mappings would be unique...
		identities = set()
		for name,entry in KEYMAP.items():

			identity = (name, entry['Qt'], entry.get('scan'))#, entry.get('key'))
			if identity in identities: # TODO what if we have a key with same name but one with scan code and one without?
				raise NameError('duplicate key?', identity)
			identities.add(identity)

		return KEYMAP

	class SnapDeviceKeyboardKey(SnapDeviceInputButton):

		__slots__ = []

		@ENV.SnapProperty
		class name:

			def set(self, MSG):
				" "
				raise NotImplementedError('setting name not allowed on keys, as it is derived from scancode')


		@ENV.SnapProperty
		class active:

			def get(self, MSG):
				""" """
				# TODO return if this key is pressed (bitmask?)
				raise NotImplementedError()

		@ENV.SnapProperty
		class modifiers:

			def get(self, MSG):
				"""()->list(*SnapDeviceNode)"""
				# TODO return list of modifiers affecting this key
				raise NotImplementedError()

		"""
		@ENV.SnapProperty
		class code:

			def set(self, MSG):
				"(int!)"
				code = MSG.args[0]
				if code is not None:
					assert isinstance(code, int), 'code must be int'
					name = SNAP_KEYMAP.snap_scancode_to_name(code)
				else:
					name = None

				self.__snap_data__['code'] = code
				self.__snap_data__['name'] = name

				self.changed(code=code, name=name)
		"""


		def __init__(self, code=None, **SETTINGS):
			SnapDeviceInputButton.__init__(self, **SETTINGS)

			#self.define_symbol(code=code, level=level, text=text)

			# TODO instead of codes maybe just use indices?
			self.__snap_data__['code'] = code # scan code (hardware) -- keyval code is assigned to symbol

			#self['symbols'] = []

			# code = physical key / scan code

	ENV.SnapDeviceKeyboardKey = SnapDeviceKeyboardKey


	class SnapDeviceKeyboard(SnapDevice):

		__slots__ = []

		KEYMAP = load_keymap(CONFIG_FILE)

		@ENV.SnapProperty
		class shift_enabled:

			def get(self, MSG):
				"()->bool"

				modifiers = self.get('modifiers')

				# supporting one "Shift" key, or "LeftShift", "RightShift" keys if enabled in config
				SHIFT_KEYS = []
				CAPSLOCK = None
				for key in modifiers:
					name = key['name']
					if 'shift' in name.lower():
						SHIFT_KEYS.append(key)
					elif 'capslock' in name.lower():
						CAPSLOCK = key

				if not (SHIFT_KEYS and CAPSLOCK):
					ENV.snap_warning('missing a shift modifier key?', SHIFT_KEYS, CAPSLOCK)
					return False

				return any(k['state'] for k in SHIFT_KEYS) ^ CAPSLOCK['state']

		@ENV.SnapProperty
		class level:

			# TODO if we implement the backend ourself then this would be useful for mapping the text,
			# but otherwise doesn't do much right now :)

			def get(self, MSG):
				"()->int"
				return int(self['shift_enabled'])




		@ENV.SnapChannel
		def device_event(self, MSG):
			''
			# TODO if event is from a key with text, send the text event through text group and device_event as well action='text'

		@ENV.SnapChannel
		def key_event_intercept(self, MSG):
			'' # TODO listen to self.device_event with this, and if it's a text key then send a text event
			ENV.snap_out('key intercept, check for text', MSG) # forward through self.text_event.send()
			# XXX backend will handle this, keyboard just has keys now (doesn't even need scancodes!)


		# XXX text events will be sent as device_event(action='text_input', ...)
		"""
		@ENV.SnapChannel
		def text_event(self, MSG):
			'()'
			# TODO listen to this for text events, generated by gui backend
		"""


		def __init__(self, **SETTINGS):
			SnapDevice.__init__(self, **SETTINGS)

			#self._level_ = 0

			keys = []
			modifiers = []
			#code_to_key = {} # map of codes to the corresponding key for speed

			seen_names = set()

			for name,entry in self.KEYMAP.items():#SNAP_KEYMAP.SNAP_KEYMAP:

				if name in seen_names:
					ENV.snap_warning("duplicate key?", repr(name))
					continue
				seen_names.add(name)

				check_name = name.lower()

				if check_name in ("capslock",): # TODO numlock?  other locks?
					mode = 'TOGGLE'
				else:
					mode = 'NORMAL'

				#ENV.snap_out('key', scancode, scanname)
				def fake_codes():
					code = -1
					while 1:
						code += 1
						yield code

				fake_code = fake_codes()
				key = SnapDeviceKeyboardKey(code=next(fake_code), name=name, mode=mode)
				keys.append(key)

				#if 'keys' in e:
				#	for idx, (keycode, keyname, keytext) in enumerate(e['keys']):
				#		key.define_symbol(code=keycode, level=idx, text=keytext)

				if 'shift' in check_name or 'ctrl' in check_name or 'control' in check_name or 'alt' in check_name or 'capslock' in check_name:
					# TODO ALT, CTRL, GUI?, numlocks... all locks?
					# https://wiki.libsdl.org/SDL2/SDL_Keymod
					"""
					KMOD_NONE
					KMOD_LSHIFT
					KMOD_RSHIFT
					KMOD_LCTRL
					KMOD_RCTRL
					KMOD_LALT
					KMOD_RALT
					KMOD_LGUI
					KMOD_RGUI
					KMOD_NUM
					KMOD_CAPS
					KMOD_MODE
					KMOD_SCROLL
					KMOD_CTRL
					KMOD_SHIFT
					KMOD_ALT
					KMOD_GUI
					"""
					#ENV.snap_debug('init modifier key', repr(name))
					modifiers.append(key)


			# following what SDL does, where text events are their own thing
			# (separate from keyboard configuration to make things easier)
			# just listen to the text group to get the text events
			#text = SnapDeviceGroup(name='TEXT') # XXX use text_event channel

			# physical keys
			keys = SnapDeviceGroup(name='keys', children=keys)
			modifiers = SnapDeviceGroup(name='modifiers', children=modifiers)

			children = [keys, modifiers]#, text]

			self['children'] = children
			
			#assert self.get("TEXT") is text, 'unable to add text group to keyboard!'
			assert self.get('keys') is keys and self.get('modifiers') is modifiers

			# TODO
			capslock = self.get('keys', 'CapsLock')
			assert capslock['mode'] == 'TOGGLE'


			#self.device_event.listen(self.key_event_intercept)
			
				
			"""
			for e in SNAP_KEYBOARD_MAPPING:
				try:
					text = chr(e['text'])
				except:
					#print('no text?', e)
					text = None
				self.define_key(code=e['code'], value=e['keyval'], text=text, level=e['level'], group=e['group'])
			"""

			# TODO add input group for text?  so text can be sent through the input group?

	ENV.SnapDeviceKeyboard = SnapDeviceKeyboard
	return SnapDeviceKeyboard


def main(ENV):

	if not getattr(ENV, 'SnapDevice', None):
		ENV.__build__('snap.os.devices')

	snap_test_out = ENV.snap_test_out

	k = ENV.SnapDeviceKeyboard()
	snap_test_out(k['shift_enabled'] == False)
	capslock = k.get("keys", "CapsLock")
	snap_test_out(capslock is not None)
	if capslock:
		capslock.press()#generate_event("PRESS")
		capslock.release()#generate_event("RELEASE")
		snap_test_out(k['shift_enabled'] == False)
		capslock.press()##generate_event("PRESS")
		snap_test_out(capslock['state'] == True and k['shift_enabled'] == True)
		capslock.release()#generate_event('RELEASE')
		snap_test_out(capslock['state'] == False and k['shift_enabled'] == False)

	#print('get x', ENV.SNAP_KEYMAP.snap_keycode_to_name(88), k.get('keys', 88))

	SnapContainer = ENV.SnapContainer

	# TODO make gui interface to configure keyboard -- make a channel for gui to send raw event info...
	class KeyboardCalibration(SnapContainer):
		# XXX make the SnapKeyboardDevice the calibration api if it is added to a scene?

		@ENV.SnapChannel
		def device_event(self, MSG):
			action,device,source = MSG.unpack('action', None, 'device', None, 'source', None)
			if isinstance(device, ENV.SnapDeviceKeyboard):
				ENV.snap_out('keyboard event', MSG.kwargs)

	ENV.__run_gui__(KeyboardCalibration)

if __name__ == '__main__':

	import snap; main(snap.SnapEnv())


