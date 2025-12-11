
# https://builtin.com/software-engineering-perspectives/python-class-decorator

from types import FunctionType

def build(ENV):

	SnapMessage = ENV.SnapMessage

	SnapBoundChannel = ENV.SnapBoundChannel
	SnapBoundProperty = ENV.SnapBoundProperty

	class SnapChannelType(object):
		pass

	ENV.SnapChannelType = SnapChannelType

	class SnapPropertyType(SnapChannelType):
		pass

	ENV.SnapPropertyType = SnapPropertyType

	class SnapChannelProxy(SnapChannelType):
		pass

	ENV.SnapChannelProxy = SnapChannelProxy


	def snap_wrapper_factory(USER_CALL, KWARGS, TYPE, OUTPUT_SPEC):

		if TYPE == SnapPropertyType:
			assert isinstance(USER_CALL, type), 'wrong type (SnapProperty needs a class): {}'.format(USER_CALL.__qualname__)
		else:
			assert isinstance(USER_CALL, FunctionType), 'wrong type (SnapChannel needs a function): {}'.format(USER_CALL.__qualname__)


		FULLNAME = USER_CALL.__qualname__
		spl = FULLNAME.split('.')
		NAME = spl[-1]
		CLASSNAME = spl[-2]

		#if SUPERTYPE is not None:
		#	ENV.snap_warning(FULLNAME, 'deprecated supertype')

		#CLASS = getattr(ENV, CLASSNAME, None)

		#ENV.snap_out('decorate', CLASSNAME, NAME, CLASS)

		for attr in dir(USER_CALL):
			if attr.startswith('__') and attr.endswith('__'): continue
			if attr not in ('set','get','delete'):
				# TODO allow properties to have custom methods?
				ENV.snap_warning('unsupported attr', USER_CALL, repr(attr))

		IS_PROPERTY = issubclass(TYPE, SnapPropertyType)

		# TODO look for docstrings for specs, and include options for required, sets, ..., in the docstring?
		# 	-- use '!' after each required argument, and '?' after each optional argument?  if not specified assume it is optional?
		#	-- support multiple specs with parens in parens... ((arg!, arg2?, named=type!),(arg2!))->return
		"""
		HANDLERS = {}

		for attr in ('get','set','delete'):
			if not KWARGS.get(attr, True) or (hasattr(USER_CALL, attr) and not getattr(USER_CALL, attr)):
				def error(*a, **k):
					raise NotImplementedError(USER_CALL, attr)
				HANDLERS[attr] = error
			elif (hasattr(USER_CALL, attr) and getattr(USER_CALL, attr)):
				HANDLERS[attr] = getattr(USER_CALL, attr)
			else:
				pass # default behaviour for handler (direct set/get/delete)
		"""

		# TODO input/output specs...  just pass as strings?
		# TODO get,set,delete options are now for specs...

		# TODO if type provided and not input/output/return_value on property, then assume input/output is type (unless assigned to be None)
		#	-- also, if isinstance(type, str) then parse it, otherwise assume it is the type

		# TODO output supports multiple specs *BUT* all the specs data are emitted in one output...  (we can just understand how it is supposed to be used)

		class SnapDecorator(TYPE):

			__slots__ = []

			__USER__ = USER_CALL
			__NAME__ = NAME
			__BASE_NAME__ = CLASSNAME
			__OUTPUT_SPEC__ = OUTPUT_SPEC

			# TODO options...  input/output (set/get/delete) specs...

			def _register_base(self, INSTANCE, BASE):
				# this is useful/used when decorator isn't instantiated...  otherwise SnapNode.__init__() will assign the base class
				if self.__BASE__ is None and INSTANCE is None and CLASSNAME == BASE.__name__:
					#ENV.snap_out('register base', CLASSNAME, FULLNAME)
					self.__BASE__ = BASE

			if IS_PROPERTY:

				assert isinstance(USER_CALL, type), 'property requires class!  not: {}'.format(type(USER_CALL))

				def __get__(self, INSTANCE, BASE):
					if self.__BASE__ is None:
						self._register_base(INSTANCE, BASE)

					if INSTANCE is not None:
						return SnapBoundProperty(INSTANCE, NAME, self)
					return self

				def __call_direct__(self, INSTANCE, MSG):
					#return HANDLERS['set'](INSTANCE, MSG)
					return self.set(INSTANCE, MSG)
			else:

				# TODO input can be disabled, in which case calling is error?

				def __get__(self, INSTANCE, BASE):
					if self.__BASE__ is None:
						self._register_base(INSTANCE, BASE)
					if INSTANCE is not None:
						return SnapBoundChannel(INSTANCE, NAME, self)
					return self

				def __call_direct__(self, INSTANCE, MSG):
					return USER_CALL(INSTANCE, MSG)


			# BOTH:

			__direct__ = __call_direct__

			@property
			def __name__(self):
				return NAME

			def __getattr__(self, ATTR):

				#ENV.snap_out('getattr', ATTR, FULLNAME)

				try:
					return getattr(USER_CALL, ATTR)
				except AttributeError:
					pass

				#ENV.snap_out('getattr', self.__name__, SUPERTYPE)
				#SUPERCLASS = getattr(ENV, CLASSNAME, None)
				#assert SUPERCLASS is not None, 'no superclass in decorator (not assigned to ENV?) {}'.format(FULLNAME)
				#import inspect
				#frame = inspect.currentframe().f_back.f_back
				#ENV.snap_out(CLASSNAME, frame.f_globals.keys())

				# TODO how to incorporate user options?  they need to be assigned to self...  then they would be caught before this even happens...
				#CLASS = getattr(ENV, CLASSNAME, None)
				#if CLASS:
				#	return getattr(CLASS, ATTR)
				# TODO get the decorator from super and then get the attr from it...
				BASE = self.__BASE__
				if BASE is not None:
					mro = BASE.mro()[1:]
					if mro:
						SUPERDECORATOR = getattr(mro[0], NAME, None)
						if SUPERDECORATOR:
							assert isinstance(SUPERDECORATOR, SnapChannelType), 'superdecorator is not a channel type? {}'.format(FULLNAME, ATTR)
							return getattr(SUPERDECORATOR, ATTR)

					#if SUPERTYPE and SUPERDECORATOR:
					#	if SUPERDECORATOR is not SUPERTYPE:
					#		ENV.snap_error('superdecorator != supertype', SUPERDECORATOR, SUPERTYPE, FULLNAME)
				else:
					ENV.snap_debug('getattr without base', FULLNAME, USER_CALL, ATTR)

				#if SUPERTYPE: # XXX TODO get the self.__class__ and then find the 'super' decorator from there?
				#	return getattr(SUPERTYPE, ATTR)

				raise AttributeError(ATTR)

			def __call__(self, INSTANCE, MSG):
				# NOTE: this isn't *a, **k because this would really only be called 'unbound' like Class.method(self, MSG)
				return self.__call_direct__(INSTANCE, MSG)

			def shared(self, CALLABLE): # TODO rename to 'alias'?
				#@otherprop.shared to duplicate a property under a different name
				# TODO verify CALLABLE doesn't implement anything or warn?  it won't be used...

				ACCESS_NAME = self.__NAME__

				THISNAME = CALLABLE.__qualname__
				spl = THISNAME.split('.')

				# TODO store the previous decorator as well...

				# TODO we have to re-acquire the shared source from the base...
				# TODO this just needs __get__ either return the shared source, or re-acquire the name from the instance (and make sure it isn't the same name as own name)

				class SharedChannel(SnapChannelProxy):

					__NAME__ = spl[-1]
					assert __NAME__ != ACCESS_NAME, 'cannot use same name in shared: {} == {}'.format(__NAME__, ACCESS_NAME)
					__BASE_NAME__ = spl[-2]

					__BASE__ = None # owner of this property

					#def __getattr__(self, ATTR):
					#	raise NotImplementedError() # TODO

					def __get__(self, INSTANCE, BASE):
						if INSTANCE is None:
							#ENV.snap_warning('access from base', BASE, ACCESS_NAME)
							return getattr(BASE, ACCESS_NAME)
						else:
							#ENV.snap_warning('access from instance', INSTANCE, ACCESS_NAME)
							return getattr(INSTANCE, ACCESS_NAME)

				#ENV.snap_out('shared:', ACCESS_NAME, 'by:', SharedChannel.__NAME__)

				if any([a for a in dir(CALLABLE) if not (a.startswith('__') and a.endswith('__'))]):
					# class should not implement anything for this, just pass
					ENV.snap_warning('decorator.shared callable has unused params', CALLABLE)

				return SharedChannel()


			# TODO if an alias is connected, it should redirect / automatically connect to the aliased channel, the base channel
			alias = shared


			def __repr__(self):
				return '<@{}({}, TODO:options)>'.format(TYPE.__name__, FULLNAME)

			def __init__(self):
				self.__BASE__ = None # register upon __get__ retrieval, the class to which the decorator 'belongs' (so we can do hierarchies internally)


		for attr,value in KWARGS.items():
			if attr in ('input','output','type','private'):
				setattr(SnapDecorator, attr, value)
			else:
				ENV.snap_warning('skipping attr', FULLNAME, attr)

		return SnapDecorator()

	ENV.snap_wrapper_factory = snap_wrapper_factory

	def do_wrap(ARGS, KWARGS, TYPE):

		if ARGS:
			assert len(ARGS) == 1, 'unnamed args are not supported'
			USER_CALL = ARGS[0]
			if isinstance(USER_CALL, str):
			#if isinstance(USER_CALL, (SnapChannelType, SnapPropertyType)):
				#raise NotImplementedError('decorator superclass arg is deprecated', USER_CALL.__qualname__)
				def configure(FUNC):
					return snap_wrapper_factory(FUNC, KWARGS, TYPE, USER_CALL)
				return configure
			else:
				assert callable(USER_CALL), 'not a callable: {}'.format(type(USER_CALL))
			# otherwise is normal function
			return snap_wrapper_factory(USER_CALL, KWARGS, TYPE, None)
		else:
			def configure(FUNC):
				return snap_wrapper_factory(FUNC, KWARGS, TYPE, None)
			return configure
			

	def SnapChannel(*a, **k):
		return do_wrap(a, k, SnapChannelType)

	ENV.SnapChannel = SnapChannel

	def SnapProperty(*a, **k):
		return do_wrap(a, k, SnapPropertyType)

	ENV.SnapProperty = SnapProperty


def main(ENV):

	# TODO register decorator base inside SnapNode __init__ -> and mark on class?

	test_out = ENV.snap_test_out

	if 0:

		SnapNode = ENV.SnapNode

		class A(SnapNode):

			@ENV.SnapChannel
			def channel(self, MSG):
				ENV.snap_out('inside A.channel', MSG)

			@ENV.SnapProperty
			class prop:
				def get(self, MSG):
					ENV.snap_out('inside A.prop.get', MSG)

				def set(self, MSG):
					ENV.snap_out('inside A.prop.set', MSG)

				def delete(self, MSG):
					ENV.snap_out('inside A.prop.delete', MSG)

		class Test(A):

			#@ENV.SnapChannel
			#def channel(self, MSG):
			#	ENV.snap_out('inside Test.channel', MSG)

			@ENV.SnapProperty
			class prop:
				def get(self, MSG):
					ENV.snap_out('inside Test.prop.get', MSG)
					return A.prop.get(self, MSG)

				#def set(self, MSG):
				#	ENV.snap_out('inside Test.prop.set', MSG)
				#	return A.prop.set(self, MSG)

				def delete(self, MSG):
					ENV.snap_out('inside Test.prop.delete', MSG)
					return A.prop.delete(self, MSG)


			@prop.shared
			class dup:
				def get(self, MSG):
					ENV.snap_out('inside Test.dup.get', MSG)
					return self.__getitem__('prop', MSG)

		class Uninit(A):

			@ENV.SnapProperty
			class prop: pass


		t = Test()
		t['prop'] = 1
		t.prop.set(1)
		t.__setitem__('prop', 1) # this is how to do t.prop.set.__direct__ behaviour (direct call)

		t['prop']

		Uninit.prop.set(t, ENV.SnapMessage('msg', 67, 5.6, True, SnapNode(), SnapNode()))
		Uninit.channel(t, None)

		t.channel('woohoo')

		t['dup']

	else:

		# shared test
		class Base(ENV.SnapNode):

			@ENV.SnapProperty
			class prop:

				def get(self, MSG):
					return 'Base'

			@prop.shared
			class shared: pass

		class Sub(Base):

			@ENV.SnapProperty
			class prop:

				def get(self, MSG):
					return 'Sub'

			# Sub.shared redirects to Sub.prop (because we access by name, rather than just using the decorator directly)
			#	-- names are the key identifier of channels and properties...


		sub = Sub()
		test_out(sub['shared'] == 'Sub')
		ENV.snap_out(sub['shared'])
		test_out(Sub.shared.get(sub, None) == 'Sub')
		ENV.snap_out('Sub.shared is:', Sub.shared)

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

