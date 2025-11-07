

def build(ENV):

	SnapShape = ENV.SnapShape
	snap_extents_t = ENV.snap_extents_t
	#snap_incoming = ENV.snap_incoming
	snap_binary_search = ENV.snap_binary_search
	snap_warning = ENV.snap_warning
	snap_debug = ENV.snap_debug
	#snap_listen = ENV.snap_listen
	#snap_ignore = ENV.snap_ignore

	"""
	def SnapText_nearest_markups(self, *names, index=None, direction=1):

		if not index:
			index = 0

		markups = (self._markups_ or {})

		if names:
			consider = {n:snap_binary_search(markups[n], index, key=lambda x: x[0], run_to_end=True) for n in names if n in markups}
			#consider = {a:snap_binary_search(ch, index, key=lambda x: x[0], run_to_end=True) for a,ch in markups.items() if SETTINGS.get(a)}
		else:
			consider = {a:snap_binary_search(ch, index, key=lambda x: x[0], run_to_end=True) for a,ch in markups.items()}
		

		# remove indices that are out of range, and if going backwards we need to consider previous indices (binary search points to next)
		if direction < 1:
			# first checks if we hit an index in markups directly?  index == markups[attr][idx][0]
			consider = {a:(idx if idx < len(markups[a]) and markups[a][idx][0] == index else idx-1) for a,idx in consider.items()}
		# filter out indices that don't point to an existing index (markup index value)
		consider = {a:idx for a,idx in consider.items() if idx >= 0 and idx < len(markups[a])}

		#print('consider', index, consider)

		listing = [(attr,idx) for attr,idx in consider.items()]
		if not listing:
			return None

		markup_values = [markups[attr][i][0] for attr,i in listing]
		if direction > 0:
			markup_idx = min(markup_values)
		else:
			markup_idx = max(markup_values)

		# then remove listings where markup is not markup_idx
		#listing = [(attr,idx) for attr,idx in listing if markups[attr][idx][0] == markup_idx]

		return (markup_idx, {a:markups[a][i][1] for a,i in listing if markups[a][i][0] == markup_idx})
	"""

	ENV.SnapText_MARKUPS = set(['color', 'underline_color', 'strikeout_color', 'background_color', 'overline_color'])

	class SnapText(SnapShape):

		__slots__ = []
		#__slots__ = ['_format_', '_needs_update_', '_ink_extents_', '_text_extents_', '_text_', '_markups_']

		@ENV.SnapProperty
		class format:

			def get(self, MSG):
				"""()->str"""
				return self.__snap_data__['format'] or 'UTF8'

			def set(self, MSG):
				"""(str)"""
				c = MSG.args[0]
				if c is None:
					c = 'UTF8'
				assert isinstance(c, str), 'must be string'
				self.__snap_data__['format'] = c
				self.changed(format=c)

		@ENV.SnapProperty
		class needs_update:
			def get(self, MSG):
				"""()->bool"""
				return bool(self.__snap_data__['needs_update'])

		@ENV.SnapProperty
		class ink_extents:
			def get(self, MSG):
				"""()->snap_extents_t"""
				if self['needs_update']:
					self.update()
				try:
					metrics = self['metrics']
					if metrics is not None:
						return metrics.ink_extents()
				except NotImplementedError:
					pass
				return None

		@ENV.SnapProperty
		class text_extents:
			def get(self, MSG):
				"""()->snap_extents_t"""
				#return self.__snap_data__['text_extents'] or snap_extents_t()
				if self['needs_update']:
					self.update()
				try:
					metrics = self['metrics']
					if metrics is not None:
						return metrics.text_extents()
				except NotImplementedError:
					pass
				return None

		@ENV.SnapProperty
		class wrap_width:

			def get(self, MSG):
				"()->float"
				v = self.__snap_data__['wrap_width']
				if v is None:
					ext = self['extents']
					if ext is None or ext[3]-ext[0] < 1:
						#v = 300 # TODO or get extents width?  problem is if extents width is 0...
						return None
					else:
						v = ext[3]-ext[0]
				return float(v)

			def set(self, MSG):
				"(float|int!)"
				v = MSG.args[0]
				if v is not None:
					assert isinstance(v, (float,int)), 'wrong type: {}'.format(type(v))
					v = float(v)
				self.__snap_data__['wrap_width'] = v
				self.changed(wrap_width=v)

		@ENV.SnapProperty
		class metrics:

			def get(self, MSG):
				"()->SnapTextMetrics"
				return ENV.SnapTextMetrics(self)

		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"""()->str"""
				return self.__snap_data__['text'] or ''

			def set(self, MSG):
				"""(str)"""
				t = MSG.args[0]
				if t is None:
					t = ''
				assert isinstance(t, str), 'must be string'
				self.__snap_data__['text'] = t
				self.__snap_data__['needs_update'] = True
				self.changed(text=t)

		@ENV.SnapProperty
		class markups:

			def get(self, MSG):
				"""()->dict"""
				return self.__snap_data__['markups'] or {}

			def set(self, MSG):
				"""(dict)"""
				d = MSG.args[0]
				if d is None:
					d = {}
				assert isinstance(d, dict), 'markups are a dict'
				self.__snap_data__['markups'] = d

		@ENV.SnapProperty
		class __engine_data__:

			def get(self, MSG):
				"""()->?"""
				# update before access
				if self.__snap_data__['needs_update']:
					self.update() # XXX just re-implement this in the class to check for update and update before returning the engine data...
					self.__snap_data__['needs_update'] = False
				return SnapShape.__engine_data__.get(self, MSG)


		@ENV.SnapChannel
		def changed(self, MSG):
			"""()"""
			if MSG is not None and MSG.source is not self:
				self.__snap_data__['needs_update'] = True
			return SnapShape.changed(self, MSG)

		@ENV.SnapChannel
		def changed_data(self, MSG):
			return self.changed()

		@ENV.SnapChannel
		def update(self, MSG):
			"""()"""
			# re-implement in subclass to do the actual update
			self.__snap_data__['needs_update'] = False
			return None

		@ENV.SnapChannel
		def allocate(self, MSG):

			# TODO set the visible text to fit in the extents?  TODO also only consider markups for that section in update()
			# also sets word wrap?

			return SnapShape.allocate(self, MSG)


		@ENV.SnapChannel
		def nearest_markups(self, MSG):
			"""(index=int?, direction=int?)->tuple(int, dict)"""
			# (self, *names, index=None, direction=1):

			index,direction = MSG.unpack('index',None, 'direction',1, ignore_args=True)
			names = MSG.args

			if not index:
				index = 0

			markups = self['markups']
			if not markups:
				return None

			if names:
				consider = {n:snap_binary_search(markups[n], index, key=lambda x: x[0], run_to_end=True) for n in names if n in markups}
				#consider = {a:snap_binary_search(ch, index, key=lambda x: x[0], run_to_end=True) for a,ch in markups.items() if SETTINGS.get(a)}
			else:
				consider = {a:snap_binary_search(ch, index, key=lambda x: x[0], run_to_end=True) for a,ch in markups.items()}
			

			# remove indices that are out of range, and if going backwards we need to consider previous indices (binary search points to next)
			if direction < 1:
				# first checks if we hit an index in markups directly?  index == markups[attr][idx][0]
				consider = {a:(idx if idx < len(markups[a]) and markups[a][idx][0] == index else idx-1) for a,idx in consider.items()}
			# filter out indices that don't point to an existing index (markup index value)
			consider = {a:idx for a,idx in consider.items() if idx >= 0 and idx < len(markups[a])}

			#print('consider', index, consider)

			listing = [(attr,idx) for attr,idx in consider.items()]
			if not listing:
				return None

			markup_values = [markups[attr][i][0] for attr,i in listing]
			if direction > 0:
				markup_idx = min(markup_values)
			else:
				markup_idx = max(markup_values)

			# then remove listings where markup is not markup_idx
			#listing = [(attr,idx) for attr,idx in listing if markups[attr][idx][0] == markup_idx]

			return (markup_idx, {a:markups[a][i][1] for a,i in listing if markups[a][i][0] == markup_idx})


		@ENV.SnapChannel
		def define_markup(self, MSG):

			submsg,index = MSG.unpack('index',None, extract=True)
			SETTINGS = submsg.kwargs

			if not index:
				index = 0
			else:
				assert isinstance(index, int), 'index must be int {}'.format(repr(index))

			if not SETTINGS:
				ENV.snap_debug('no markups added', index)
				return

			for attr,value in SETTINGS.items():

				is_SnapNode = attr in ENV.SnapText_MARKUPS

				if is_SnapNode:
					assert isinstance(value, SnapNode)
					#snap_listen(value, self) # TODO listen to which?  gc?
				elif attr in ('bold', 'italic', 'size', 'gravity'): # caps?
					assert isinstance(value, (float,int))
				elif attr in ('font',):
					assert isinstance(value, (str,)) # or SnapString?  name of font?
				elif attr in ('strikeout', 'underline', 'overline'):
					value = bool(value)
				else:
					ENV.snap_warning("markup not recognized:", attr)
					continue

				markups = self['markups']
				if not markups:
					self['markups'] = {attr:[(index, value)]}
				else:
					channel = markups.get(attr, [])
					idx = snap_binary_search(channel, index, key=lambda x: x[0], run_to_end=True)
					if idx < len(channel) and channel[idx][0] == index:
						if is_SnapNode:
							existing = channel[idx][1]
							if existing is not None:
								''#snap_ignore(existing, self) # TODO ignore gc?
						channel[idx] = (index, value)
					else:
						channel.insert(idx, (index, value))
					markups[attr] = channel
					self['markups'] = markups

				self.__snap_data__['needs_update'] = True

			return None

		@ENV.SnapChannel
		def remove_markup(self, MSG):

			submsg,index = MSG.unpack('index',None, ignore_kwargs=True, extract=True)
			names = submsg.args

			if not index:
				index = 0

			markups = self['markups']

			if not names:
				names = list(markups.keys())
			else:
				names = [n for n in names if n in markups]

			for name in names:
				idx = snap_binary_search(markups[name], index, key=lambda x: x[0], run_to_end=False)
				if idx < 0:
					continue
				value = markups[name].pop(idx)[1]
				if value is not None and name in ENV.SnapText_MARKUPS:
					''#snap_ignore(value, self) TODO gc ignore?
				if not markups[name]:
					del markups[name]

			self['markups'] = markups

			self.__snap_data__['needs_update'] = True

			return None

		@ENV.SnapChannel
		def clear_markup_channels(self, MSG):

			names = MSG.args

			markups = self['markups']
			if not markups:
				return None

			for name in names:
				if attr in ENV.SnapText_MARKUPS:
					for entry in markups[name]:
						if entry[1] is not None:
							''#snap_ignore(entry[1], self) # TODO ignore gc?
				try:
					del markups[name]
				except:
					pass

			self['markups'] = markups

			self.__snap_data__['needs_update'] = True

			return None


		@ENV.SnapChannel
		def clear_markup_channel(self, MSG):
			return self.clear_markup_channels(MSG.args[0])


		@ENV.SnapChannel
		def find_markup(self, MSG):
			# (self, index=None, **SETTINGS):
			'find markup that matches settings type? or is at/after index'
			raise NotImplementedError()

		@ENV.SnapChannel
		def get_markup_channel(self, MSG):
			# (self, NAME):
			NAME = MSG.args[0]
			markups = self['markups']
			if markups:
				return markups.get(NAME, [])
			return []

		@ENV.SnapChannel
		def next_markup(self, MSG):
			# (self, *names, index=None):
			index = MSG.unpack('index',None, ignore_args=True)
			names = MSG.args
			return self.nearest_markups(self, *names, index=index, direction=1)

		@ENV.SnapChannel
		def previous_markup(self, MSG):
			# (self, *names, index=None):
			index = MSG.unpack('index',None, ignore_args=True)
			names = MSG.args
			return self.nearest_markups(self, *names, index=index, direction=-1)

		@ENV.SnapChannel
		def iter_markups(self, MSG):
			# (self, *names, index=None, direction=1):

			index,direction = MSG.unpack('index',None, 'direction',1, ignore_args=True)
			names = MSG.args

			if index is None:
				index = 0

			if direction > 0: direction = 1
			else: direction = -1

			while 1:
				m = self.nearest_markups(self, *names, index=index, direction=direction)
				if not m:
					break
				yield m
				index = m[0] + direction


		@ENV.SnapChannel
		def clear(self, MSG):
			"""(markups=bool?, text=bool?)"""

			markups,text = MSG.unpack('markups', False, 'text', False)

			if not (markups or text):
				markups = text = True

			elif markups:
				self['markups'] = {}

				self.__snap_data__['needs_update'] = True

			elif text:
				self['text'] = ''
				self.__snap_data__['ink_extents'] = self.__snap_data__['text_extents'] = snap_extents_t(0,0,0, 0,0,0)

				self.__snap_data__['needs_update'] = True



		def draw(self, CTX):
			CTX.cmd_draw_text(self)

		def lookup(self, CTX):
			''#ENV.snap_warning('NotImplemented: generic text lookup')
			# TODO this could just be inbounds check...


		def __init__(self, text=None, **SETTINGS):
			SnapShape.__init__(self, text=text, **SETTINGS)

			#if text is None:
			#	self['text'] = ''

			#self['format'] = None # hint of text encoding (assumed "UTF8" if not defined)
			self.__snap_data__['needs_update'] = True # True|False flag to update before render (when engine data is accessed if true it will update then submit for render)
			#self.__snap_data__['ink_extents'] = snap_extents_t() # (double[6]) of the ink min/max, ie. tight fit around lettering
			#self.__snap_data__['text_extents'] = snap_extents_t() # (double[6]) of the text min/max
			# NOTE: self._extents_ is a designation, if NULL or 0 then text will take the room it needs, otherwise it will be limited to fit within the extents area
			#self['text'] = None # string of text data for all markups (markups index into it)
			#self['markups'] = {} # each channel is a list of pairs (index, value), value will apply until next marker or end of text


	ENV.SnapText = SnapText


def main(ENV):

	t = ENV.SnapText()
	t.set(text="hello world")
	t.define_markup(0, bold=2, italic=3)
	t.define_markup(5, strikeout=True)
	t.define_markup(8, strikeout=False)

	for attr,channel in t['markups'].items():
		ENV.snap_out(attr,':',channel)

	for markup in t.iter_markups():
		ENV.snap_out('markup iter result', markup)

	ENV.snap_out(t.previous_markup('bold', index=1))

	ENV.graphics.load('QT5')
	ENV.__run_gui__(ENV.GRAPHICS.Text, text='hello world')

	ENV.snap_out('ok')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


