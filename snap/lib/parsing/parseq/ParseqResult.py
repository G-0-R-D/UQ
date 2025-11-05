
#from snap.lib.core import *


# avoiding isinstance because it makes the imports messy
#PARSEQ_TYPE_SEQUENCE = 1
#PARSEQ_TYPE_LAYER = 2

#SnapNode = ENV.SnapNode
#snap_warning = ENV.snap_warning


def build(ENV):

	# depends on ParseqSequence

	class ParseqResult(object):

		__slots__ = [
			'_sequence_',
			'_span_',
			'_rule_',
			'_subs_',
			]

		def span(self):
			span = self._span_ or [-1,-1] # TODO better to raise?
			return [min(span), max(span)]

		def start(self):
			return self.span()[0]

		def end(self):
			return self.span()[1]

		def sequence(self):
			return self._sequence_

		def source(self):

			sequence = self.sequence()
			if not sequence:
				return None
			while 1:

				if isinstance(sequence, ENV.ParseqLayer):#._type_code_ == PARSEQ_TYPE_LAYER:
					next_sequence = sequence.sublayer()
					if next_sequence:
						sequence = next_sequence
						continue
				break

			s = sequence.source()
			#if getattr(s, '_type_code_', None) == PARSEQ_TYPE_SEQUENCE:
			if isinstance(s, ENV.ParseqSequence):
				return s.source()
			return s

		def source_span(self):
			# get the span that would slice the source

			sequence = self.sequence()
			if not sequence:
				return [-1,-1]

			s,e = self.span()
			span = e-s
			#if span == 0:
			#	return [-1,-1]

			"""
			need to identify the current sequence type (layer or not)
			"""

			while 1:

				if isinstance(sequence, ENV.ParseqLayer):#._type_code_ == PARSEQ_TYPE_LAYER:
					# this is layer, we need to go deeper

					#out('get sub', self, sequence.length(), sequence)
					if span < 1:
						return [s,e] # probably non-capturing, TODO check it is?
					elif span > 1:
						results = [sequence[s], sequence[e-1]]
					else:
						results = [sequence[s]]

					if results[0] is None or results[-1] is None:
						raise IndexError('unable to recover value from result', self, span, sequence)

					s = results[0].start()
					e = results[-1].end()
					span = e-s

					sublayer = sequence.sublayer()
					if sublayer:
						sequence = sublayer
						continue

				break

			#out('source span', s, e)
			return [s,e]
			"""
				if span == 0:
					return [s,e]

				out('sequence', type(sequence), sequence[s])

				if span > 1:
					results = [sequence[s], sequence[e]] # just index access, we don't need everything in-between
				else:
					results = [sequence[s]]

				if results[0] is None or results[-1] is None:
					raise IndexError('unable to recover value from result', self, span, sequence)

				s = results[0].start()
				e = results[-1].end()
				span = e-s


				# TODO this is wrong!  sort out layer/sublayer/sequence/source clearly!

				sublayer = sequence.sublayer()
				if not sublayer:
					source = sequence.source()
					if source and hasattr(source, 'sublayer'):
						# trying to avoid isinstance(ParseqSequence) to avoid import dependency
						sublayer = source # TODO then the next results are pulled from sequence!
						out('has sublayer', type(source))

				#else:
				if not sublayer:
					return [s,e]

				sequence = sublayer
			"""

		def line_info(self):
			# returns line_number, column_number (char index within line), and the line from source (if applicable)
			# NOTE: lineno and colno are indices, so they start at 0 to indicate first

			source = self.source()
			if source and not isinstance(source, (str, bytes)):
				raise TypeError('source input is not a string, no line info available!', type(source))
			s,e = self.source_span()
			if not source or s < 0:
				return 0,0,''

			# we could just split on '\n' but I'm going with this algorithm to minimize the buffer overhead
			# it will be slow(er) in python, but very fast in snap/c...
			idx = 0
			line = None
			last_newline = -1 # idx of last found newline
			lineno = 0
			colno = 0
			while idx < len(source):
					
				if source[idx] == '\n':
					if idx >= s:
						# we're done
						line = source[last_newline+1:idx]
						colno = (s - last_newline) - 1
						break
					lineno += 1
					last_newline = idx

				idx += 1

			if line is None:
				if s >= len(source):
					# we're at the end so line is blank
					line = ''
				else:
					# no newlines, return full source
					if lineno != 0:
						ENV.snap_warning('lineno > 0?')
					line = source[:]

			return lineno,colno,line


		def sub_value(self):
			
			sequence = self.sequence()
			if not sequence:
				return None

			s,e = self.span()
			span = e-s
			if 0:#span == 0:
				if sequence.sublayer():
					return []
				else:
					return '' # TODO determine source type (type(sequence.source())())

			return sequence[s:e]

		def source_value(self):

			s,e = self.source_span()
			source = self.source()
			if e-s == 0 or not source:
				''#return None
			return source[s:e]


		def value(self):
			return self.source_value()

		def rule(self):
			return self._rule_

		def subs(self):
			return self._subs_ or []

		def subresults(self):
			return self.subs()

		def name(self):
			rule = self._rule_
			if rule:
				return rule.name()
			return None

		def finditer(self, *NAMES, **kwargs):

			#if not (NAMES or kwargs):
			#	return None

			recurse = kwargs.get('recurse',True)

			_type = kwargs.get('_type', None)

			after = kwargs.get('after', self.start())
			before = kwargs.get('before', self.end())

			search_mode = kwargs.get('search_mode', kwargs.get('mode', 'DFS')) # or 'BFS'
			assert search_mode in ('DFS','BFS'), 'invalid search mode: {}'.format(repr(search_mode))

			QUEUE = list(self.subs())#[:]
			while QUEUE:

				result = QUEUE.pop(0)

				rule = result.rule()
				if not rule:
					snap_warning('result without rule?', result)
					continue

				if result.sequence() == self.sequence():
					# otherwise we are in sublayer result, and it is in initial range or it wouldn't have been queued...
					s,e = result.span()
					if s < after or s > before:
						continue

				#print(result, rule.name())

				# TODO if is ParseqLayerITEM then 'subs' won't give us the source...
				#if isinstance(rule, ParseqLayerITEM):
				#	subs = result.subs()
				#	assert len(subs) == 1, 'result item without subs reference? {}'.format(result)
				#	result = subs[0]
				#	rule = result.rule()

				#out(result, repr(result.value()))

				next_subs = result.subs() # NOTE: not copied!
				if recurse:
					"""
					if result.sequence() == self.sequence():
						# otherwise we are in sublayer result, and it is in initial range or it wouldn't have been queued...
						out('got here') # XXX maybe filter result start/end as processed?
						next_subs = [s for s in next_subs if s.start() >= after and s.start() <= before]
					"""

					if next_subs:
						if search_mode == 'DFS':
							QUEUE = QUEUE + next_subs
						else:
							QUEUE = next_subs + QUEUE

				# candidacy status (all applicable conditions must be met for it to be a viable match,
				# and some conditions need to also consider status of other conditions!)
				match = {}

				if _type:
					match['type'] = isinstance(rule, _type)

				if NAMES:
					match['name'] = NAMES[0] == rule.name()


				if not match or all(match.values()):

					if len(NAMES) > 1:
						# match, but keep going if more sub-names to find
						NAMES = NAMES[1:]
						QUEUE = next_subs[:] # name matches as a tree, so next name must be found in children...
						continue

					yield result


		def find(self, *NAMES, index=None, **kwargs):

			if index is not None:
				if index < 0:
					try: return list(self.finditer(*NAMES, **kwargs))[index]
					except: pass
				else:
					idx = 0
					for result in self.finditer(*NAMES, **kwargs):
						if idx == index:
							return result
						idx += 1
			else:
				for result in self.finditer(*NAMES, **kwargs):
					return result # first result only

			

		def set(self, **kwargs):
			for k,v in kwargs.items():
				if k == 'span':
					if v:
						assert len(v) == 2, 'incorrect span format'
					self._span_ = [v[0],v[1]]
				elif k == 'start':
					self._span_[0] = int(v)
				elif k == 'end':
					self._span_[1] = int(v)

				elif k == 'sequence':
					self._sequence_ = v

				elif k == 'rule':
					self._rule_ = v

				elif k == 'subs' or k == 'subresults':
					if v:
						self._subs_ = list(v)
					else:
						self._subs_ = None

		def __init__(self, **SETTINGS):

			self._sequence_ = None
			self._span_ = [-1,-1]
			self._rule_ = None
			self._subs_ = []

			self.set(**{k:v for k,v in SETTINGS.items() if k in ('sequence','span','start','end','rule','subs','subresults')})

		def __strX__(self):
			s = super(ParseqResult, self).__str__()
			# TODO rule.name and len(self.subs())

			type_ = type(self)
			module = type_.__module__
			qualname = type_.__qualname__
			#return f"<{module}.{qualname} object at {hex(id(x))}>"
			print('type', type_)

			return s[:-1] + ' ({} {})>'.format(self.span(), self.rule())

		def __repr__(self): # TODO maybe replace this with an operator like SnapResult_as_str()? XXX or just implement as alt?  try to do it the python way, otherwise do it the .snap way?  try/except
			rule = self.rule()
			typ = "???"
			name = ""
			if rule:
				typ = type(rule).__qualname__.replace('Parseq','')
				n = rule.name()
				if n:
					name = ' "'+n+'"'
			subs = self.subs()
			span = self._span_ or [-1,-1]
			#return '<{}({}) "{}" {} [{}]>'.format(typ, hex(id(self)), name, self.span(), len(subs))
			return '<{}[{}:{}]{} subs({})>'.format(typ, span[0], span[1], name, len(subs))

		def __repr_tree__(self, **SETTINGS):
		
			indent = SETTINGS.get('indent', '.')

			output = []
			
			QUEUE = [(0,self)]
			while QUEUE:
				depth,result = QUEUE.pop(0)
				output.append('{} {}'.format(depth * indent, repr(result)))
				QUEUE = [(depth+1, sub) for sub in result.subs()] + QUEUE

			return '\n'.join(output)

		def print_tree(self, **SETTINGS):
			print(self.__repr_tree__(**SETTINGS))
			

		def __len__(self):
			if self._subs_:
				return len(self._subs_)
			return 0

		def __getitem__(self, KEY):
			subs = self._subs_
			if subs:
				return subs[KEY]
			return None

		def __bool__(self):
			return self is not None

	ENV.ParseqResult = ParseqResult
