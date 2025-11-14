
try:
	from collections import Counter
except:
	class Counter(object):

		def most_common(self, count=None):
			if count is None:
				count = len(self.dict)
			return list(sorted([(k,v) for k,v in self.dict.items()], key=lambda x: x[-1]*-1))[:count]

		def __init__(self, LIST):
			d = {}
			for i in LIST:
				d[i] = d.get(i, 0) + 1
			self.dict = d

def build(ENV):

	class SnapMessage(object):

		# this is to standardize the node api, because input arguments and return value of a python function are mis-matched,
		# the node interface passes a message in, and returns a message (or None), which can then be forwarded

		__slots__ = ['args', 'kwargs', 'source', 'channel']

		# TODO extract() series (remove from) and unpack() series (reference)

		def unpack_args(self, *ENTRIES, **OPTIONS):
			raise NotImplementedError()

		def unpack_kwargs(self, *ENTRIES, **OPTIONS):
			raise NotImplementedError()

		def extract(self, *ENTRIES, **OPTIONS):
			# return the values, and remove them from the message? XXX the principle of not changing the message should apply...
			# the objective is to extract the arguments and see what is left over...
			raise NotImplementedError()

		def unpack(self, *ENTRIES, **OPTIONS):
			# usage: a,b,c = MSG.unpack('a', 'default_a', 'b', 2, 'c', var, **OPTIONS)

			# ENTRIES = 'key', value, 'key2', value2, ...

			error_if_missing = False
			include_args = True
			include_kwargs = True
			only_these_kwargs = []
			extract = False

			# XXX all of this is invalid: to work with only arg/kwargs, just access them directly!  and extractions shouldn't be allowed, create a new message with the selection using a comprehension or something...  messages should not be altered!
			for attr,value in OPTIONS.items():
				if attr == 'error_if_missing': error_if_missing = bool(value)
				elif attr == 'include_args': include_args = bool(value)
				elif attr == 'ignore_args': include_args = not bool(value)
				elif attr == 'include_kwargs': include_kwargs = bool(value)
				elif attr == 'ignore_kwargs': include_kwargs = not bool(value)
				elif attr == 'only_these_kwargs': value # list of names to consider (ignore the rest)
				elif attr == 'extract': extract = bool(value)
				else: raise NameError('unsupported option', repr(attr))

			len_ENTRIES = len(ENTRIES)
			assert len_ENTRIES > 1 and len_ENTRIES % 2 == 0, 'must provide atleast one argument and value to unpack!'
			len_names = len_ENTRIES // 2

			out = list(ENTRIES[1::2]) # start with default values

			#if self is None:
			#	return out

			args = self.args
			len_args = len(args)
			kwargs = self.kwargs

			if not include_args:
				len_args = 0

			if not include_kwargs:
				kwargs = {}
			elif only_these_kwargs:
				kwargs = {k:v for k,v in kwargs.items() if k in only_these_kwargs}

			removed_names = None
			if extract:
				removed_names = set()

			i = 0
			while i < len_names:
				name = ENTRIES[i*2]
				if i < len_args:
					assert name not in kwargs, 'double entry for arg[{}]: {}'.format(i, repr(name))
					out[i] = args[i]
				else:
					try:
						out[i] = kwargs[name]
						if extract:
							removed_names.add(name)
					except KeyError:
						if error_if_missing:
							raise KeyError('missing arg[{}], kwarg[{}]'.format(i, repr(name)))
				i += 1

			if extract:
				if not include_args:
					# 'include' means for processing, so they haven't been consumed; keep them in the message
					i = 0
				submsg = SnapMessage(*args[i:], **{k:v for k,v in kwargs.items() if k not in removed_names})
				out = [submsg] + out

			if len(out) < 2:
				return out[0] # otherwise when we unpack a single arg it will be in a list!
			return out


		def __getattr__(self, ATTR):
			try:
				return self.kwargs[ATTR]
			except:
				return None

		def __getitem__(self, KEY):

			if isinstance(KEY, (int,slice)):
				return self.args[KEY]
			elif isinstance(KEY, str):
				return self.kwargs[KEY]
			else:
				raise KeyError(KEY)

		def __setitem__(self, KEY, VALUE):
			raise NotImplementedError('setting disabled')

		def __delitem__(self, KEY):
			raise NotImplementedError('deleting disabled')

		#def __len__(self): # XXX use len(self.args) or len(self.settings) instead...
		#	return len(self.args)# + len(kwargs)

		def __bool__(self):
			return bool(self.args or self.kwargs)

		def __repr__(self):

			if self.args:
				# TODO just take top 3 by count, then put ... if more
				unique_types = [pair[0] for pair in Counter(str(type(a).__name__) for a in self.args).most_common(4)]
				#unique_types = set(str(type(a).__name__) for a in self.args)
				template = '{}'
				if len(unique_types) > 1:
					template = '(' + template + ')'
				if len(unique_types) > 3:
					unique_types = unique_types[:3]
					template = template.format('{}|...')

				template = template.format('|'.join(unique_types))
				args = '{}*{}'.format(len(self.args), template)
			else:
				args = ''

			if self.kwargs:
				if args:
					args = args + ', '
				kwargs = ', '.join([k + '=*' for k in self.kwargs.keys()])
			else:
				kwargs = ''
			return self.__class__.__name__ + '(' + args + kwargs + ')'

		def __init__(self, *args, **kwargs):

			self.args = args
			self.kwargs = kwargs
			self.source = None
			self.channel = None # the output channel that (originally?) sent the message

	ENV.SnapMessage = SnapMessage


	def unpack_msg_from_key(KEY):
		if isinstance(KEY, tuple) and len(KEY) == 2 and isinstance(K[1], SnapMessage):
			return KEY[0], KEY[1]
		else:
			return KEY, SnapMessage()

	ENV.unpack_msg_from_key = unpack_msg_from_key

