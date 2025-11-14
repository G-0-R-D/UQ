
# https://www.berrange.com/tags/gtkvnc/
# https://github.com/rust-windowing/winit/issues/753



from weakref import ref as weakref_ref

def build(ENV):

	SnapNode = ENV.SnapNode
	SnapMessage = ENV.SnapMessage

	#SnapEvent = ENV.SnapEvent

	#snap_keycode_to_name = ENV.snap_keycode_to_name
	SNAP_KEYMAP = ENV.SNAP_KEYMAP
	SnapDeviceInputButton = ENV.SnapDeviceInputButton
	SnapDeviceGroup = ENV.SnapDeviceGroup
	SnapDevice = ENV.SnapDevice

	class SnapDeviceKeyGroup(SnapDeviceGroup):

		__slots__ = []

		# TODO children are in numerical (code) order?  and also by name?

		# access by code or name


	class SnapDeviceKeyboardKeySymbol(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class name:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['name']

			"""
			def set(self, MSG):
				"(str!)"
				name = MSG.args[0]
				if name is not None:
					assert isinstance(name, str), 'name must be string'
				self.__snap_data__['name'] = name
				self.changed(name=name)
			"""

		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['text'] or ''

			"""
			def set(self, MSG):
				"(str!)"
				text = MSG.args[0]
				if text is not None:
					assert isinstance(text, str), 'text must be string'
				self.__snap_data__['text'] = text
				self.changed(text=text)
			"""

		@ENV.SnapProperty
		class code:

			def get(self, MSG):
				"()->int"
				code = self.__snap_data__['code']
				if code is None:
					return -1
				return code

			"""
			def set(self, MSG):
				"(int!)"
				value = MSG.args[0]
				if value is not None:
					assert isinstance(value, int), 'value must be int'
				self.__snap_data__['value'] = value
				self.changed(value=value)
			"""

		@code.shared
		class keycode: pass

		def __init__(self, name=None, code=None, text=None):
			SnapNode.__init__(self)

			if name is not None:
				assert isinstance(name, str), 'name must be string'
			if code is not None:
				assert isinstance(code, int), 'code must be int'
			if text is not None:
				assert isinstance(text, str), 'text must be string'

			self.__snap_data__['name'] = name
			self.__snap_data__['code'] = code
			self.__snap_data__['text'] = text

			# this is logicless, the owner needs to assign the correct values... (it's really just a dict, but with SnapNode api)

			#self.set(**{k:v for k,v in SETTINGS.items() if k in ('name', 'value', 'text')})

	ENV.SnapDeviceKeyboardKeySymbol = SnapDeviceKeyboardKeySymbol


	class SnapDeviceKeyboardKey(SnapDeviceInputButton):

		__slots__ = []

		"""
		def text(self, level=None):
			symbol = self.symbol(level=level)
			if symbol:
				return symbol.text()
			return None

		def value(self, level=None):
			symbol = self.symbol(level=level)
			if symbol:
				return symbol.value()
			return None

		def nameXXX(self):
			# key name is always scan code name
			for symbol in getattr(self, '_symbols_', []):
				if symbol:
					return symbol.name()
			return None
		"""

		# XXX instead of this do something like keyboard.shift.enabled()?
		"""
		def level(self):
			keyboard = self.device()
			if keyboard:
				return keyboard.level()
			return 0
		"""

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

		@ENV.SnapProperty
		class symbols:

			def get(self, MSG):
				"""()->list(*SnapDeviceKeyboardKeySymbol)"""
				return self.__snap_data__['symbols'] or []

		@ENV.SnapProperty
		class symbol:

			def get(self, MSG):
				"""(level=int?)->SnapDeviceKeyboardKeySymbol"""
				level = MSG.unpack('level', None)

				symbols = self['symbols']

				if level is None:
					keyboard = self['device']
					if keyboard is None:
						ENV.snap_warning('no keyboard to determine active level, assigning to 0')
						level = 0
					else:
						level = int(keyboard['shift_enabled'])

				if level > -1 and level < len(symbols):
					return symbols[level]

				return None

			#def set(self, MSG):
			#	''


		"""
		def generate_eventXXX(self, MSG):
			# TODO??

			EVENT = MSG.args[0]
			EXTRAS = MSG.kwargs

			# TODO if self is modifier (shift key), then update keyboard level
			# TODO make this snap_event(&keyboard, "MODIFIER_EVENT", ...)?  add to list of "active_modifiers"?

			level = 0
			scancode = self.code()

			if scancode == SNAP_SCANCODE_CAPSLOCK:
				'toggle on / off' # TODO RELEASE does not release a toggle button, but another press when state is true...
				# TODO just add mode=toggle to SnapDeviceInputButton...


		
			# XXX keyboard.shift_enabled() -> (shift_L | shift_R) ^ CAPSLOCK -> just find() by code?

			if keyval and (
				# TODO use self.code() == SNAP_SCANCODE_LSHIFT | RSHIFT...
				# actually use special shift group to handle this?
				keyval == SNAP_KEYVAL_Shift_L or \
				keyval == SNAP_KEYVAL_Shift_R
				# TODO keyval == SNAP_KEYVAL_Caps_Lock
				):

				keyboard = self['device']

				if EVENT == "PRESS":
					# set level 1
					# TODO check level is not 1 first?
					keyboard.set(level=1)

				elif EVENT == "RELEASE":
					# set level 0 (if all shift keys are released!)

					modifiers = keyboard.get("MODIFIERS")
					children = modifiers['children'] # XXX no more children

					#snap_out("device(%p) modifiers(%p) children(%p)", device, modifiers, children);

					still_caps = False
					for key in children:
						if key['name'] in ('Shift_L', 'Shift_R'):
							# TODO capslock on?
							if key != self and key['state'] == True:
								still_caps = True
								break

						#snap_out('modifier name', name)

					if not still_caps:
						keyboard.set(level=0)

			return SnapDeviceInputButton.generate_event(self, SnapMessage(EVENT, **EXTRAS))
		"""

		def define_symbol(self, code=None, level=None, text=None):

			# NOTE XXX text is temporary, until more robust mapping (create symbol_value -> text mapping (for applicable symbols)		

			if not (code is not None and SNAP_KEYMAP.snap_keycode_to_name(code)):
				raise ValueError("must provide valid symbol code!")

			if level is None:
				level = 0

			symbol = None

			# check if symbol already exists
			symbols = self['symbols']
			if symbols is not None and level < len(symbols) and symbols[level] is not None:
				# symbol entry exists
				symbol = symbols[level]
				keycode = symbol['code']
				if keycode != code:
					ENV.snap_error("existing symbol with different code!")
					raise KeyError('another symbol({}) already occupies level({})'.format(symbol['name'], level))
				else:
					ENV.snap_debug("symbol({}) already added to key".format(SNAP_KEYMAP.snap_keycode_to_name(code)))
			else:
				# create new and add
				if level < 0 or level > 10:
					raise ValueError('level out of acceptable range', level)

				name_before = self['name']
				while len(symbols) <= level:
					symbols.append(None) # pad with None
				symbols[level] = SnapDeviceKeyboardKeySymbol(code=code, name=SNAP_KEYMAP.snap_keycode_to_name(code), text=text)

				self.__snap_data__['symbols'] = symbols

				if name_before != self['name']:
					self.changed(name=self['name'])
			
			return None

		"""
		def add(self, MSG):

			OTHER_SETTINGS = {k:v for k,v in MSG.kwargs.items() if k not in ('symbol','level')}

			symbol,level = MSG.unpack('symbol',None, 'level',None, ignore_args=True)

			if OTHER_SETTINGS: # XXX TODO?
				SnapDeviceInputButton.add(self, SnapMessage(**OTHER_SETTINGS))

			if level is not None or symbol is not None:
				if not (level is not None and symbol is not None):
					raise ValueError('level and symbol must be defined together')
				
				if level < 0 or level > 10:
					raise ValueError('level out of acceptable range')

				existing = self['symbol', SnapMessage(level=level)]
				if existing and id(existing) != id(symbol):
					raise KeyError("another symbol({}) already occupies level({})".format(existing.name(), level))

				name_before = self['name']
				symbols = self['symbols']
				while len(symbols) <= level:
					symbols.append(None)
				symbols[level] = symbol

				self['symbols'] = symbols

				#snap_listen(symbol, self) # ?

				if name_before != self['name']:
					keyboard = self['device']
					if keyboard:
						keyboard.changed.send(name=name_before)
		"""

		def __init__(self, code=None, **SETTINGS):
			SnapDeviceInputButton.__init__(self, **SETTINGS)

			#self.define_symbol(code=code, level=level, text=text)

			self.__snap_data__['code'] = code # scan code (hardware) -- keyval code is assigned to symbol

			#self['symbols'] = []

			# code = physical key / scan code

	ENV.SnapDeviceKeyboardKey = SnapDeviceKeyboardKey


	class SnapDeviceKeyboard(SnapDevice):

		__slots__ = []

		@ENV.SnapProperty
		class shift_enabled:

			def get(self, MSG):
				"()->bool"

				keys = self.get('keys')

				LSHIFT = keys.get("LSHIFT")
				RSHIFT = keys.get("RSHIFT")
				CAPSLOCK = keys.get("CAPSLOCK")

				if not (LSHIFT and RSHIFT and CAPSLOCK):
					ENV.snap_warning('missing a shift modifier key?', LSHIFT, RSHIFT, CAPSLOCK)
					return False

				return (LSHIFT['state'] | RSHIFT['state']) ^ CAPSLOCK['state']

		@ENV.SnapProperty
		class level:

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


		@ENV.SnapChannel
		def text_event(self, MSG):
			'()'
			# TODO listen to this for text events


		@ENV.SnapChannel
		def generate_eventXXX(self, MSG): # XXX move this onto the key...

			EVENT = MSG.args[0]
			code = MSG.unpack('code',None)
			EXTRAS = {k:v for k,v in MSG.kwargs.items() if k not in ('code',)}

			# TODO if EVENT == "TEXT": generate text event through text group...  otherwise raise (key events should go through the keys direct...

			if not (EVENT == "PRESS" or EVENT == "RELEASE"):
				raise Exception('event({}) unsupported'.format(EVENT))

			if code is None or code < 0:
				raise ValueError('invalid code({}) for event'.format(code))

			key = self.get(code)
			if not key:
				raise KeyError('no key for code({})'.format(code))

			return key.generate_event(EVENT, **EXTRAS)


		@ENV.SnapChannel
		def key_for_keycodeXXX(self, MSG): # XXX just use get(code) (TODO distinguish keyval from scancode?)
			"""(keycode=int)->SnapDeviceKeyboardKey"""
			
			# key instance based on symbol on the key
			# NOTE: this is not very efficient TODO use the keymap and just consider entries with 'keys'?

			KEYCODE = MSG.unpack('keycode',None) if MSG is not None else None

			all_inputs = self.__snap_data__['__inputs_by_id__']
			if all_inputs is None:
				return None

			for key in all_inputs.values():
				symbols = key['symbols']
				if symbols is not None:
					for symbol in symbols:
						keycode = symbol['code']
						if keycode == KEYCODE:
							return key

			return None

		#@ENV.SnapChannel
		def define_keyXXX(self, code, value, text, level): # XXX TODO not a channel, make internal

			#SETTINGS = {k:v for k,v in MSG.kwargs.items() if k not in ('code','text','level')}
			#code,value,text,level = MSG.unpack('code',None, 'text',None, 'level',None)

			#if SETTINGS:
			#	ENV.snap_warning('unknown args', SETTINGS.keys())
		
			if level is None:
				level = 0

			# NOTE: code is scancode here...
			if code is None or code < 0 or not SNAP_KEYMAP.snap_keycode_to_name(code):
				raise ValueError('invalid code({}) in define_key'.format(code))

			if level > 10:
				raise ValueError('key level too high', level)

			key = self.get(code)
			if key is None:
				# create new key
				if level != 0:
					ENV.snap_warning('creating new key for level != 0')
				key = SnapDeviceKeyboardKey(code=code, device=self)
				self.register(key)

				# verify was added
				if self.get(code) != key:
					raise KeyError('unable to add key!', code, self.get(code))

			symbol = key['symbols'][level]
			if not symbol:
				# make new symbol at level
				# TODO can define_symbol(...) just be key.add(input=SnapDevice...Sym(value, level, text))?
				key.define_symbol(code=code, level=level, text=text)
			else:
				# verify symbol is same or bark
				if symbol['code'] != code:
					ValueError('key code mismatch', level, name, code, symbol['code'])


			# add modifier keys to "MODIFIERS" group
			if code in (
				SNAP_KEYMAP.SNAP_SCANCODE_LSHIFT,
				SNAP_KEYMAP.SNAP_SCANCODE_RSHIFT,
				SNAP_KEYMAP.SNAP_SCANCODE_CAPSLOCK,
				# TODO ALT, CTRL, GUI?, numlocks... all locks?
				):

				modifiers = self.get('MODIFIERS')
				if not modifiers:
					modifiers = SnapDeviceGroup(name='MODIFIERS', device=self)
					self.register(modifiers)

					if self.get('MODIFIERS') is not modifiers:
						raise KeyError('modifiers not registered properly?')

				modifiers.register(key)

			return None


		"""
		def set(self, **SETTINGS):

			for attr,value in SETTINGS.items():
				if attr == 'level':
					# TODO update self.time?
					self._level_ = int(value)
				else:
					SnapDevice.set(self, **{attr:value})
		"""


		def __init__(self, **SETTINGS):
			SnapDevice.__init__(self, **SETTINGS)

			#self._level_ = 0

			keys = []
			modifiers = []
			#code_to_key = {} # map of codes to the corresponding key for speed

			seen_names = set()

			for e in SNAP_KEYMAP.SNAP_KEYMAP:
				scancode,scanname = e['scan']

				if scanname in seen_names:
					ENV.snap_warning('duplicate keyname', scanname)
					continue
				seen_names.add(scanname)

				if scancode in ("CAPSLOCK",): # TODO numlock?  other locks?
					mode = 'TOGGLE'
				else:
					mode = 'NORMAL'

				#ENV.snap_out('key', scancode, scanname)
				key = SnapDeviceKeyboardKey(code=scancode, name=scanname, mode=mode)
				keys.append(key)

				if 'keys' in e:
					for idx, (keycode, keyname, keytext) in enumerate(e['keys']):
						key.define_symbol(code=keycode, level=idx, text=keytext)

				if scancode in (
					SNAP_KEYMAP.SNAP_SCANCODE_LSHIFT,
					SNAP_KEYMAP.SNAP_SCANCODE_RSHIFT,
					SNAP_KEYMAP.SNAP_SCANCODE_CAPSLOCK,
					# TODO ALT, CTRL, GUI?, numlocks... all locks?
					):
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
					modifiers.append(key)


			# following what SDL does, where text events are their own thing
			# (separate from keyboard configuration to make things easier)
			# just listen to the text group to get the text events
			#text = SnapDeviceGroup(name='TEXT') # XXX use text_event channel

			keys = SnapDeviceGroup(name='keys', children=keys)
			modifiers = SnapDeviceGroup(name='modifiers', children=modifiers)

			children = [keys, modifiers]#, text]

			self['children'] = children
			
			#assert self.get("TEXT") is text, 'unable to add text group to keyboard!'
			assert self.get('keys') is keys and self.get('modifiers') is modifiers

			capslock = self.get('keys', 'CAPSLOCK')
			capslock['mode'] = 'TOGGLE'


			self.device_event.listen(self.key_event_intercept)
			
				
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
		ENV.__build__('snap.core.os.devices')

	snap_test_out = ENV.snap_test_out

	k = ENV.SnapDeviceKeyboard()
	snap_test_out(k['shift_enabled'] == False)
	capslock = k.get("keys", "CAPSLOCK")
	snap_test_out(capslock is not None)
	if capslock:
		capslock.press()#generate_event("PRESS")
		capslock.release()#generate_event("RELEASE")
		snap_test_out(k['shift_enabled'] == False)
		capslock.press()##generate_event("PRESS")
		snap_test_out(capslock['state'] == True and k['shift_enabled'] == True)
		capslock.release()#generate_event('RELEASE')
		snap_test_out(capslock['state'] == False and k['shift_enabled'] == False)

	print('get x', ENV.SNAP_KEYMAP.snap_keycode_to_name(88), k.get('keys', 88))

		

