
def build(ENV):

	SnapNode = ENV.SnapNode
	SnapPrimitive = ENV.SnapPrimitive

	SnapMessage = ENV.SnapMessage

	def consolidate_user_args(MSG, single_arg=False):
		l = []
		if MSG.args:
			if single_arg:
				assert len(MSG.args) == 1, 'incorrect arg format'
				l.extend(MSG.args[0])
			else:
				l.extend(MSG.args)

		l.extend(MSG.kwargs.get('items', []))
		if 'item' in MSG.kwargs:
			l.append(MSG.kwargs['item'])

		#assert all([isinstance(i, SnapNode) for i in l if i is not None]), 'SnapList members must be only SnapNode type'
		return l

	class SnapList(SnapPrimitive):

		__slots__ = []

		def __compare__(self):
			raise NotImplementedError() # ability to compare any two sequences?

		@ENV.SnapProperty
		class data:
			def get(self, MSG):
				"""()->list"""
				return SnapPrimitive.data.get(self, MSG)

			def set(self, MSG):
				"""(list|tuple)"""
				user = MSG.args[0]
				if user is not None:
					assert isinstance(user, (list,tuple)), 'SnapList.data.set requires list or tuple, got: {}'.format(type(user))
					user = [x for x in user]

				self.__snap_data__['data'] = user
				self.changed(data=user)


		@ENV.SnapProperty
		class items:

			def get(self, MSG):
				"""()->list"""
				return list(self['data'])

			def set(self, MSG):
				"""(list|tuple|SnapList)"""
				assign = MSG.args[0]
				if assign is not None:
					assert isinstance(assign, (list,tuple,SnapList)), 'unsupported items assign type: {}'.format(type(assign))
					assign = list(assign)

				self['data'] = assign

		@ENV.SnapProperty
		class item:

			def get(self, MSG):
				"""()->object"""
				data = self['data']
				if data:
					assert len(data) == 1, 'more than one entry, "item" access is invalid'
					return data[0]
				return None

			def set(self, MSG):
				"""(object)"""
				assert len(MSG.args) == 1, 'must provide single item argument'
				self['data'] = MSG.args

			def delete(self, MSG):
				"""()"""
				data = self['data']
				if not data:
					return
				if len(data) == 1:
					del self['data']
				else:
					raise ValueError('more than one entry, cannot delete item')
				


		#def data(self):
		#	return SnapPrimtive.data(self) or []

		@ENV.SnapChannel
		def set(self, MSG):
			"""(*object?, item=object?, items=list|tuple|SnapList|SnapChildren?)"""
			# either set(*a) or set(items=[...], item=x)

			try:
				items = list(MSG.args)
				for attr,value in MSG.kwargs.items():
					if attr == 'item':
						if value:
							items.append(value)
						else:
							items = None
					elif attr == 'items':
						if value:
							items.extend(value)
						else:
							items = None
					else:
						raise AttributeError(attr)

				self['items'] = items
			except Exception as e:
				ENV.snap_error(ENV.snap_exception_info(e))

		@ENV.SnapChannel
		def remove(self, MSG):
			"""(*object?, item=object?, items=list|tuple|SnapList|SnapChildren?)"""
			existing = self['data'] or []
			user = consolidate_user_args(MSG, False)
			self['data'] = [i for i in existing if i not in user]

		@ENV.SnapChannel
		def insert(self, MSG):
			"""(int, *object?, item=object?, items=list|tuple|SnapList|SnapChildren?)"""
			index = MSG.args[0]
			assert isinstance(index, int), 'index must be int, first argument'
			MSG.args = tuple(MSG.args[1:])
			existing = self['data'] or []
			user = consolidate_user_args(MSG, False)
			self['data'] = existing[:index] + user + existing[index:]

		@ENV.SnapChannel
		def append(self, MSG):
			"""(*object?, item=object?, items=list|tuple|SnapList|SnapChildren?)"""
			existing = self['data'] or []
			user = consolidate_user_args(MSG, False)
			existing.extend(user)
			self['data'] = existing

		@ENV.SnapChannel
		def add(self, MSG):
			"""(*object?, item=object?, items=list|tuple|SnapList(*object)?"""
			'append?' # TODO
			raise NotImplementedError()

		@ENV.SnapChannel
		def extend(self, MSG):
			"""(tuple|list(*object), item=object?, items=list|tuple?)"""
			existing = self['data'] or []
			user = consolidate_user_args(MSG, True)
			existing.extend(user)
			self['data'] = existing
			

		#def set(self, *NODES, **SETTINGS):
		#	return self.__snap_input__("set", SnapMessage(*NODES, **SETTINGS))

		def __iter__(self):
			data = self['data']
			if data is not None:
				for i in data:
					yield i


		def __getitem__(self, KEY):
			if isinstance(KEY, (int,slice)):
				return self['data'][KEY]
			return SnapPrimitive.__getitem__(self, KEY)

		def __setitem__(self, KEY, VALUE):
			if isinstance(KEY, (int,slice)):
				raise NotImplementedError(KEY)
			return SnapPrimitive.__setitem__(self, KEY, VALUE)

		def __delitem__(self, KEY):
			if isinstance(KEY, (int,slice)):
				raise NotImplementedError(KEY)
			return SnapPrimitive.__delitem__(self, KEY)

		# TODO copy?

		def __bool__(self):
			return bool(self['data'])

		def __len__(self):
			data = self['data']
			return len(data) if data is not None else 0

		def __call__(self, *a, **k):
			raise Exception('SnapList is not callable')

		def __init__(self, *a, **k):
			SnapPrimitive.__init__(self)

			if a or k:
				self.set(*a, **k)

			# TODO SnapChannels for list operations

		# TODO __getitem__ and all that

	ENV.SnapList = SnapList
