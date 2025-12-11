
from types import MethodType, FunctionType

from weakref import ref as weakref_ref

"""
can't do better than __getitem__(self, KEY) 
	"prop(type='x', default='?', return='?', input='()', output='()')"
	# XXX don't need default, it is implementation detail...  should always return expected type (or None)

prop send does set()  call does get() (forget delete?)

just declare channel and property specs inside class body?

class SnapNode(object):

	SnapProperty('name', type='name', return_value='?', input='()|()|...', output='()')

	or define method for property, put docstring on it, method handles incoming?


so methods define channels and properties?  but property set/get/del implemented with __getitem__, ..., api?

"""
def build(ENV):

	SnapMessage = ENV.SnapMessage

	SnapBoundChannel = ENV.SnapBoundChannel
	SnapBoundProperty = ENV.SnapBoundProperty

	def snap_unpack_msg_from_key(KEY):
		if isinstance(KEY, tuple) and len(KEY) == 2 and isinstance(KEY[-1], SnapMessage):# and isinstance(KEY[0], str):
			return KEY # (unpack 2) # XXX TODO get rid of this, passing arguments to a property key access looks awful and is unintuitive, plus it adds overhead!
		else:
			return KEY,SnapMessage()

	ENV.snap_unpack_msg_from_key = snap_unpack_msg_from_key

	class SnapNodeData(object):

		__slots__ = ['dictionary']

		# this should be used directly when properties aren't used, or in the properties to do the actual access
		# this is so property data doesn't share the channel namespace (attrs)

		def __getitem__(self, STR):
			return self.dictionary.get(STR)

		def __setitem__(self, STR, VALUE):
			assert isinstance(STR, str), 'keys must be strings, not: {}'.format(type(STR))
			self.dictionary[STR] = VALUE

		def __delitem__(self, STR):
			try:
				del self.dictionary[STR]
			except KeyError:
				pass

		def get(self, *a, **k):
			return self.dictionary.get(*a, **k)

		def pop(self, KEY):
			try: 
				return self.dictionary.pop(KEY)
			except:
				return None

		def __repr__(self):
			return '{}({})'.format(self.__class__.__name__, self.dictionary)

		def __init__(self):
			self.dictionary = {}
			# TODO slots = set() ?  then error for any key that isn't included in the set for strict behaviour?

	ENV.SnapNodeData = SnapNodeData


	class SnapNodeListeners(object):

		__slots__ = ['channels']#, 'blocking']

		def send(self, INSTANCE, CHANNEL, MSG):

			# TODO check if blocked, and if so then do the appropriate action...
			#if self.blocking:
				# TODO blocking is a count, type, and handler?  handler registers the type string uniquely?  only one handler to filter the messages...
				#for wk in blocked:
				#	ref = wk()
				#	if ref is not None:
				#		ref.handle('__send__', MSG)
			#	raise NotImplementedError()
			#	return None

			listeners = self.channels.get(CHANNEL)
			if not listeners:
				return None

			if MSG is None:
				msg = SnapMessage()
			else:
				msg = MSG # ?
			#msg.args = MSG.args
			#msg.kwargs = MSG.kwargs
			msg.source = INSTANCE
			msg.channel = CHANNEL

			for l in listeners[:]: # copied in case this is changed during the call

				# TODO just bind the method?  listener just needs the input method!

				try:
					ref,channel,converter = l
					ref = ref()
				except:
					continue

				#print('ref', ref)

				# just in case message was re-used...
				msg.source = INSTANCE
				msg.channel = CHANNEL

				# TODO if return value is a generator then call it to completion?  or just don't do that here...
				#try:
				if isinstance(ref, SnapNode):
					bound = getattr(ref, channel, None)
					if isinstance(bound, SnapBoundChannel) and bound.__data__[-1] is not None:
						bound.__data__[-1].__direct__(bound.__data__[0], msg)
				elif ref:
					ref(msg)
				#else:
				#	ENV.snap_debug('null listener', INSTANCE.__class__.__name__, CHANNEL)

				#target._(target, l.channel, msg)
				#except Exception as e:
					# TODO internally capture lineinfo when emit or send is called, and on error report where the actual call occurred from! XXX not in python
					#ENV.snap_error(self, OUTPUT_CHANNEL, repr(e))
					# TODO traceback report?
					#try:
				#	ENV.snap_print_exception(e)
				#	ENV.snap_print_stack()
					#except:	
					#ENV.snap_error('error emitting to channel', repr(INSTANCE), repr(OUTPUT_CHANNEL))

			#ENV.__SNAP_RECURSION_GUARD__ += 1

		#def silence(self, CHANNEL):
		#	raise NotImplementedError()

		#def aggregate(self, CHANNEL):
		#	raise NotImplementedError()

		#def register_block(self, **CHANNEL_OP):
		#	'channel=silence|aggregate' # put the logic internally?
		#	raise NotImplementedError()

		def unused(self):
			return bool(not self.channels)

		def has_node(self, NODE):
			try:
				return NODE in [wk() for channel in self.channels.values() for wk in channel]
			except:
				return False

		def connect(self, OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL, CONVERTER):

			if isinstance(LISTENER, ENV.SnapNode):
				_L = weakref_ref(LISTENER)
			else:
				def fake_weakref():
					return LISTENER
				_L = fake_weakref
			L = (_L, INPUT_CHANNEL, CONVERTER)

			if OUTPUT_CHANNEL not in self.channels:
				self.channels[OUTPUT_CHANNEL] = [L]
			else:
				self.channels[OUTPUT_CHANNEL] = [(wk,ch,con) for (wk,ch,con) in self.channels[OUTPUT_CHANNEL] if wk() is not None and not (wk() is LISTENER and ch == INPUT_CHANNEL)] + [L]

			return None

		def disconnect(self, OUTPUT_CHANNEL, LISTENER, INPUT_CHANNEL):

			if OUTPUT_CHANNEL not in self.channels:
				return None

			remaining = [(wk,ch,con) for (wk,ch,con) in self.channels[OUTPUT_CHANNEL] if wk() is not None and not (wk() is LISTENER and ch == INPUT_CHANNEL)]

			if not remaining:
				del self.channels[OUTPUT_CHANNEL]
			else:
				self.channels[OUTPUT_CHANNEL] = remaining

			return None


		def __init__(self):
			self.channels = {}
			#self.blocking = None # when channel is silenced or aggregated it is registered here
			# TODO do the blocked like a refcount system...  once released then the action is taken (like aggregate event sent)

	ENV.SnapNodeListeners = SnapNodeListeners

	"""
	def snap_handle_item_access(self, KEY, VALUE, MODE, DEFAULT_HANDLER):

		assert MODE in ('get','set','delete'), 'unrecognized mode: {}'.format(repr(MODE))

		KEY,MSG = snap_unpack_msg_from_key(KEY)

		if isinstance(KEY, str):

				# TODO if property is provided then ALL handling goes through property?  ie. if set/get/delete is not defined or declared then it is disabled not bypassed?
				bound_prop = getattr(self, KEY, None)
				if isinstance(bound_prop, SnapBoundProperty):
					callable = bound_prop.__data__[-1]
					if callable is not None:
						call = getattr(callable, MODE, None)
						if call:
							if MODE == 'set':
								if MSG.args or MSG.kwargs:
									# TODO error if existing args?  that's kinda ambiguous...
									MSG = SnapMessage(VALUE, *MSG.args, **MSG.kwargs)
								else:
									MSG = SnapMessage(VALUE)
							# TODO check if callable is marked private?  XXX forget private, refuse connections by specifying no protocol...
							_return = call(self, MSG)
							getattr(bound_prop, {'get':'accessed', 'set':'assigned', 'delete':'deleted'}[MODE]).emit()
							return _return
					#ENV.snap_out('is bound', KEY, self, MODE)
					if MODE == 'get':
						return None # soft on get, hard on others
					raise KeyError('{}[{}]'.format(self.__class__.__name__, KEY)) # if property exists then it must handle all i/o...

				elif getattr(self, 'SNAP_STRICT_PROPERTIES', False):
					# whether to allow setting properties that aren't declared directly (useful for private stuff)
					raise KeyError('{}[{}]'.format(self.__class__.__name__, KEY))

				#elif bound_prop is not None: # allow?  this isn't technically a collision...  they are in different namespaces...
				#	raise KeyError('in use for non-property', KEY)

				if MODE == 'set':
					return DEFAULT_HANDLER(self, KEY, VALUE)
				return DEFAULT_HANDLER(self, KEY)

		# TODO send numerical slices and indexing to a different set of properties?  or make a special property for data streams?

		raise KeyError('{}[{}]'.format(self.__class__.__name__, KEY))
	"""

	"""
	def SnapNode_get_property(self, NAME, ATTR):
		bound_prop = getattr(self, NAME, None)
		if isinstance(bound_prop, SnapBoundProperty):
			callable = bound_prop.__data__[-1]
			if callable is not None:
				call = getattr(callable, ATTR, None)
				return bound_prop, call
			return bound_prop, None
		return None,None

	ENV.SnapNode_get_property = SnapNode_get_property
	"""

	class SnapNode(object):

		__slots__ = ['__snap_data__', '__snap_listeners__', '__snap_init__', '__weakref__']

		# __SNAP_STRICT_PROPERTIES__ = True|False # properties must be declared (otherwise we can just assign any value at any time)

		def __snap_save__(self):

			TYPE_NAME = self.__class__.__name__ # should be same as ENV
			assert self.__class__ is getattr(ENV, TYPE_NAME, None)

			data = {'__type__':TYPE_NAME,
				#'__snap_data__':self.__snap_data__.deepcopy(), # TODO we have to serialize all types...  if isinstance(SnapNode) then .__snap_save__()
			}
			#return data

			raise NotImplementedError()

		def __snap_load__(self, JSON):
			raise NotImplementedError()		



		def __getitem__(self, KEY):
			# this access is argumentless, and we're gonna keep it that way
			# if you want to access with arguments use: node.prop.get(*args) (instead of node['prop'])

			if isinstance(KEY, str):

				bound_prop = getattr(self, KEY, None)
				if isinstance(bound_prop, SnapBoundProperty):
					callable = bound_prop.__data__[-1]
					if callable is not None:
						# need to catch "get = None" as a block
						has = False
						try:
							get = getattr(callable, 'get')
							has = True
						except AttributeError:
							pass

						if has:
							if get is not None:
								return get(self, SnapMessage())
							else:
								raise ValueError(self.__class__.__name__, KEY, 'get() disabled')

					if getattr(self, '__SNAP_STRICT_PROPERTIES__', None):
						raise KeyError('{}["{}"]'.format(self.__class__.__name__, KEY))
					else:
						# if bound property exists but a get() doesn't, then we forbid access quietly; return None
						return None

				return self.__snap_data__[KEY]

			raise KeyError('{}["{}"]'.format(self.__class__.__name__, KEY))


		def __setitem__(self, KEY, VALUE):

			if isinstance(KEY, str):

				bound_prop = getattr(self, KEY, None)
				if isinstance(bound_prop, SnapBoundProperty):
					callable = bound_prop.__data__[-1]
					if callable is not None:
						# need to catch "set = None" as a block
						has = False
						try:
							set = getattr(callable, 'set')
							has = True
						except AttributeError:
							pass

						if has:
							if set is not None:
								return set(self, SnapMessage(VALUE))
							else:
								raise ValueError(self.__class__.__name__, KEY, 'set() disabled')
				else:
					self.__snap_data__[KEY] = VALUE
					return

			raise KeyError('{}[{}] = {}'.format(self.__class__.__name__, KEY, type(VALUE)))

		def __delitem__(self, KEY):

			if isinstance(KEY, str):

				bound_prop = getattr(self, KEY, None)
				if isinstance(bound_prop, SnapBoundProperty):
					callable = bound_prop.__data__[-1]
					if callable is not None:
						# need to catch "delete = None" as a block
						has = False
						try:
							delete = getattr(callable, 'delete')
							has = True
						except AttributeError:
							pass

						if has:
							if delete is not None:
								return delete(self, SnapMessage())
							else:
								raise ValueError(self.__class__.__name__, KEY, 'delete() disabled')
						

					raise KeyError('del {}["{}"]'.format(self.__class__.__name__, KEY))

				del self.__snap_data__[KEY]

			raise KeyError('del {}["{}"]'.format(self.__class__.__name__, KEY))

		# add: self['prop'] = self['prop'] + [new]
		# remove: self['prop'] = self['prop'].remove(new) (or self['prop'] = [x for x in self['prop'] if x not y]

		@ENV.SnapChannel
		def changed(self, MSG):
			"""()"""
			# NOTE: property changes go through node.changed channel, rather than the individual properties
			# this is because the properties belong to the node, and don't stand on their own,
			# and it makes it easier for the interested party to just listen to node.changed rather than each
			# property individually...
			# ALSO NOTE: it is still possible to emit through properties though...
			self.changed.__emit__(MSG)

		@ENV.SnapChannel
		def set(self, MSG):
			"""()"""

			if MSG.args:
				ENV.snap_warning('SnapNode.set(*args) does nothing')

			for attr,value in MSG.kwargs.items():

				bound_prop = getattr(self, attr, None)
				if isinstance(bound_prop, SnapBoundProperty):
					bound_prop.set(value)
				else:
					raise KeyError('{}.set() missing property: {}'.format(self.__class__.__name__, repr(attr)))


		def __repr__(self):
			return '<{} {}>'.format(self.__class__.__name__, hex(id(self)))

		def __init__(self, **SETTINGS):

			# TODO what if we made __snap_data__ into just a 'data' SnapProperty?  then it can emit...
			if getattr(self, '__snap_data__', None) is None:
				self.__snap_data__ = SnapNodeData()

			# __snap_listeners__ created when needed

			# NOTE: this is for the decorators to be able to perform their own mro search to lookup
			# superclass properties...  (might be a better way...)
			#	-- if I recall, I couldn't find a way to access the class from inside the channel
			#	so this assigns the base to each channel...
			#ENV.snap_debug('init', [c.__name__ for c in self.__class__.mro()])
			for base in self.__class__.mro():
				if base == object: continue
				if base.__dict__.get('__snap_init__', False):
					#ENV.snap_debug('already init', base.__name__)
					break
				for attr,value in base.__dict__.items():
					if isinstance(value, ENV.SnapChannelType) and value.__BASE__ is None:
						value.__BASE__ = base
						#ENV.snap_out('found channel', base.__name__, attr, value.__BASE__)
				base.__snap_init__ = True

			if SETTINGS:
				self.set(**SETTINGS) # -> goes to individual properties for assign


	ENV.SnapNode = SnapNode




def main(ENV):

	test_out = ENV.snap_test_out

	class User(ENV.SnapNode):

		__slots__ = []

		@ENV.SnapChannel
		def channel(self, MSG):
			ENV.snap_out('user channel', self, MSG)
			return 8

		@ENV.SnapProperty
		class myprop:
			def get(self, MSG):
				ENV.snap_out('inside prop get', self, MSG)
				return 777

			def set(self, MSG):
				ENV.snap_warning('setting', self, MSG.args)

			# TODO validate(self, MSG): MSG.arg[0] is value to make sure is supported type?  if it's more complex than isinstance...
			#	-- call before set and get?

		@myprop.shared
		class duplicate: pass

		@ENV.SnapProperty
		class default:
			pass

		@ENV.SnapProperty
		class no_get:

			def set(self, MSG):
				ENV.snap_out('no_get.set()', MSG)
			#set = None

			get = None

		def __init__(self):
			ENV.SnapNode.__init__(self)

			self['myprop'] = 10


	class Subclass(User):

		@ENV.SnapChannel
		def channel(self, MSG):
			return User.channel(self, MSG)

		@ENV.SnapProperty
		class myprop:
			def get(self, MSG):
				# NOTE: in here we don't want to call __getitem__ of the same name, either call the superclass property or use SnapNode_get_prop() to get prop directly
				return User.myprop.get(self, MSG)

			#def set(self, MSG):
			#	return User.myprop.set(self, MSG)

		@ENV.SnapChannel
		def subclassed_channel(self, MSG):
			ENV.snap_out('inside subclassed channel')
			return User.channel(self, MSG)


		"""
		@ENV.SnapProperty
		class attachable:

			# TODO add attachable property to BoundProperty, which just checks if this is on callable...
			def attached(self):
				# TODO this is get?  returns the attachment if assigned?
				"(int)" # if missing then set() must describe a single type
				return self.__snap_data__['attachable'] is not None

			def set(self, MSG):
				"(int)"
				# TODO set would do attachment, set to None to 'detach'
				num = MSG.args[0]
				if num is not None:
					assert isinstance(num, int), 'must provide int'
					self.__snap_data__['attachable'] = num
				else:
					del self.__snap_data__['attachable']

			def get(self, MSG):
				"()->type"
				# this is normal get behaviour, just return the attachment if assigned
				return self.__snap_data__['attachable']
		"""


	user = Subclass()
	#print(user.channel)

	#ENV.snap_warning(user.myprop)

	test_out(user['myprop'] == 777)
	test_out(user['duplicate'] == 777)

	test_out(user.channel() == 8)
	test_out(user['myprop'] == user.myprop.get() == 777)

	test_out(user.subclassed_channel() == 8)

	try:
		del user['myprop']
		test_out('my prop del went through' == None)
	except:
		test_out('my prop del key error')

	#test_out(user.attachable.attachable is True)#.attached)
	#test_out(user.attachable.attached() is False)

	"""
	try:
		user.myprop.attached()
		test_out('myprop attached() called!' == 'x')
	except AttributeError:
		test_out('my prop has no attached()')
	"""

	#test_out(Subclass.attachable.attached(user) is False)

	"""
	try:
		Subclass.myprop.attached(user)
		test_out('myprop attached() called' == 'x')
	except AttributeError:
		test_out('myprop has no attached()')

	user['attachable'] = 3
	test_out(user['attachable'] == 3)
	test_out(user.attachable.attached() is True)
	user['attachable'] += 3 # add like this?
	test_out(user['attachable'] == 6)
	user['attachable'] -= 2 # remove like this?
	test_out(user['attachable'] == 4)
	user['attachable'] = None
	test_out(user['attachable'] is None)
	test_out(user.attachable.attached() is False)
	"""


	# test non-channel listeners

	called = [False]
	def weaktest():
		def callback(MSG):
			ENV.snap_out('hello from callback!', MSG)
			called[0] = True

		user.channel.listen(callback)
		return callback
	callback = weaktest()
	user.channel.send(1,2,3,a=1,b=2,c=3)
	test_out(called[0] == True)
	user.channel.ignore(callback)
	called[0] = False
	user.channel.send('ok?')
	test_out(called[0] == False)

	user['no_get'] = 1
	try:
		user['no_get']
		test_out(False)
	except ValueError:
		test_out(True)

	#user.channel()

	#print('got prop', user.prop.get(), user['prop'], user.prop.get() == user['prop'] == User.__getitem__(user, 'prop'))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

