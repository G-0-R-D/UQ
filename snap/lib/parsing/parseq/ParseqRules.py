
#from snap.lib.core.SnapObject import *
#from snap.lib.parsing.parseq.ParseqResult import *
#from snap.lib.parsing.parseq.ParseqSequence import *

#from snap.lib.parsing.parseq import ParseqDebugger as ParseqDebuggerModule

"""
try:
	from snap.lib.core.parsing.parseq.snap_core import *
	from snap.lib.core.parsing.parseq.ParseqDebugger import *
	from snap.lib.core.parsing.parseq.ParseqResult import *
except ImportError:
	from snap_core import *
	from ParseqDebugger import *
	from ParseqResult import *
"""


def build(ENV):

	#ENV.__build__('snap.lib.core.parsing.parseq.ParseqDebugger')

	#SnapObject = ENV.SnapObject

	ParseqResult = ENV.ParseqResult

	snap_out = ENV.snap_out
	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error
	snap_debug = ENV.snap_debug

	snap_binary_search = ENV.snap_binary_search

	PARSEQ_MATCH_FAIL = ENV.PARSEQ_MATCH_FAIL

	"""
	parseq_debug_reset_closest_match = ENV.parseq_debug_reset_closest_match
	parseq_debug_register_closest_match = ENV.parseq_debug_register_closest_match
	parseq_debug_incr = ENV.parseq_debug_incr
	parseq_debug_decr = ENV.parseq_debug_decr
	"""


	def ParseqRule___return_results__(self, SEQUENCE, subresults):#, MATCH_START, MATCH_END):

		#ENV.snap_debug('match', [SEQUENCE.MATCH_START, SEQUENCE.MATCH_END], self)

		#if SEQUENCE.DEBUGGER is not None:
		#	#assert SEQUENCE.MATCH_START != PARSEQ_MATCH_FAIL and SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL
		SEQUENCE.DEBUGGER.register_closest_match(SEQUENCE, self, SEQUENCE.MATCH_START,SEQUENCE.MATCH_END) # >>DEBUG

		# TODO turn this into ParseqRule method so it can be overridden with custom behaviour!  we could possibly decode directly into a tree by returning subresults of the target type!

		if self.suppress():
			# NOTE: suppress only applies to subresults, self can still capture (unless unnamed or explicitly set to not capture)
			subresults = None

		rule_settings = SEQUENCE.rule_settings or {}

		simplify = rule_settings.get('simplify')

		#simplify = self._simplify_ or kwargs.get('simplify')

		capture = self.capture() # can be None at this point

		capture_all = rule_settings.get('capture_all')
		if capture_all is not None:
			capture = capture_all # if set to False then rules explictly won't be captured...

		# simplify only if capture is not explicitly set to true
		if simplify and not capture and subresults and len(subresults) == 1:

			# NOTE: layer change logically shouldn't simplify...
			subresult = subresults[0]
			if SEQUENCE.MATCH_START == subresult.start() and SEQUENCE.MATCH_END == subresult.end():
				return subresults

		if capture or (capture is None and self.name() is not None):
			# capture this rule (if capture not specified (None) then capture if name is given)

			# NOTE: MATCH_END can be < MATCH_START
			return [ParseqResult(sequence=SEQUENCE, rule=self, span=[SEQUENCE.MATCH_START,SEQUENCE.MATCH_END], subs=subresults)]
		
		# no capture for self, but return subresults (still a successful match)
		return subresults
	ENV.ParseqRule___return_results__ = ParseqRule___return_results__

	def ParseqRule___perform_submatch_actual__(RULE, SEQUENCE):
		# used for skip/ignore parsing

		START = SEQUENCE.position()
		ENV.snap_out('call submatch', SEQUENCE.position(), SEQUENCE[SEQUENCE.position()-1:SEQUENCE.position()+1], RULE)
		RULE.__match__(SEQUENCE) # subresults implicitly dumped
		#out(START, SEQUENCE.MATCH_END)
		# NOTE: if rule is non-advancing then it is considered a fail since we are at same position as before
		if SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL and max(SEQUENCE.MATCH_START, SEQUENCE.MATCH_END) - min(SEQUENCE.MATCH_START, SEQUENCE.MATCH_END) != 0:
			assert SEQUENCE.MATCH_START != PARSEQ_MATCH_FAIL, 'start set to fail on pre/post-parse success'
			SEQUENCE.set(position=SEQUENCE.MATCH_END) # play it safe
			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return True
		SEQUENCE.set(position=START)
		return False
	ENV.ParseqRule___perform_submatch_actual__= ParseqRule___perform_submatch_actual__


	def ParseqRule___perform_submatch__(RULE, SEQUENCE):

		assert not SEQUENCE.subparse_in_progress, 'skip/ignore with own skip/ignore is not allowed'
		SEQUENCE.subparse_in_progress = True

		_return = ParseqRule___perform_submatch_actual__(RULE, SEQUENCE)

		SEQUENCE.subparse_in_progress = False
		return _return
	ENV.ParseqRule___perform_submatch__ = ParseqRule___perform_submatch__


	def ParseqRule___perform_match_actual__(self, SEQUENCE, first_match_is_success):

		SEQUENCE.DEBUGGER.match_enter(SEQUENCE, self)

		# first_match_is_success == rule is OR logic (only one matches to succeed),
		# otherwise it is AND logic (all items must match to succeed)

		# TODO
		"""
		ignore = kwargs.get('ignore',None)
			-> then when matching it make sure ignore rule is not passed into the submatch... (so it doesn't recurse)
		TODO the problem with this approach is it will essentially capture what is ignored as part of the rule match... (whitespace will now be included inbetween words...)
			we could possibly alleviate this by forcing 'fake' subresults...  split the match into subgroupings...?
			or do it by pre-parsing?  so we can advance past the ignore -- make both pre and post ignore options?

		NOTE: why both skip and ignore?
		let's say we have a rule that matches something like two newlines ITEM('\n\n') and if it fails we just want to ignore any whitespace at all ANY('\n','\t',' ', ...)
		if the whitespace rule is skipped (pre-parsed), then our rule will never have a chance to match (all newlines will be discarded before '\n\n' is checked for...)
		but if it is parsed after (ignore) then our rule gets a chance to match before discarding the unused whitespace...

		"""

		#if ENV.__PARSEQ_DEBUG_PRIVATE__['DEBUG_LEVEL'] > -1:
		#	snap_out('match rule', self)

		SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
		START = SEQUENCE.position()

		if not SEQUENCE.subparse_in_progress and SEQUENCE.rule_settings:
			rule_settings = SEQUENCE.rule_settings
			skip = rule_settings.get('skip')
			ignore = rule_settings.get('ignore')
		else:
			skip = ignore = None

		# NOTE: if ignore (or skip) are 0 span (non-capturing) then it is considered a fail since
		# it is still at the same start position as last time...
		# TODO skip and ignore from sequence
		#skip = kwargs.get('skip') # skip is pre-parse
		#ignore = kwargs.get('ignore') # ignore is post-parse
		#sub_kwargs = None
		#if skip or ignore:
		#	# pre/post parses cannot themselves pre/post parse, so we remove the arguments from their match call
		#	sub_kwargs = {k:v for k,v in kwargs.items() if k not in ('skip', 'ignore')}

		if skip and first_match_is_success:
			# if OR rule then we only skip once before attempting matching rules,
			# otherwise if AND we skip before matching each rule
			if ParseqRule___perform_submatch__(skip, SEQUENCE):#, sub_kwargs):
				START = SEQUENCE.position()

		results = []

		match_count = 0 # need to find the first match to update START to SEQUENCE.MATCH_START

		match_start = SEQUENCE.position()

		item_idx = 0
		items = self.items()
		len_items = len(items)
		while item_idx < len_items:

			if skip and not first_match_is_success:
				# if AND we pre-scan before each item...
				if ParseqRule___perform_submatch__(skip, SEQUENCE) and match_count == 0:
					# if skip before first item we advance start of overall rule
					match_start = START = SEQUENCE.position()

			#SEQUENCE.DEBUGGER.match_enter(SEQUENCE, items[item_idx])
			subresults = items[item_idx].__match__(SEQUENCE)
			#SEQUENCE.DEBUGGER.match_exit(SEQUENCE, items[item_idx], success=SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL)

			item_idx += 1

			if SEQUENCE.MATCH_END == PARSEQ_MATCH_FAIL:
				# match failed

				#SEQUENCE.set(position=match_start)

				if subresults:
					SEQUENCE.DEBUGGER.warning("subresults received on fail")

				if first_match_is_success:
					# OR can fail as long as one item matches

					if item_idx == len_items and ignore and ParseqRule___perform_submatch__(ignore, SEQUENCE):
						# TODO does sequence position need to be set back to previous start before submatch?
						item_idx = 0 # begin match again
						match_start = START = SEQUENCE.position()
					else:
						SEQUENCE.set(position = START)
					continue

				elif ignore:
					SEQUENCE.set(position=match_start)
					if ParseqRule___perform_submatch__(ignore, SEQUENCE):
						match_start = SEQUENCE.position()
						#snap_out('success ignore', item_idx, SEQUENCE.position())
						item_idx -= 1 # try previous match again
						continue

				break

			SEQUENCE.set(position = SEQUENCE.MATCH_END)
			if match_count == 0:
				# introduced with layers, in which "__match__" can search, so the start can change (otherwise it previously didn't...)
				# XXX actually: start can be different if outer rule is non-capturing and capturing inner rule has different start point...
				START = SEQUENCE.MATCH_START
				match_count += 1 # just so it isn't 0 anymore...

			match_start = SEQUENCE.MATCH_END

			if subresults:
				results.extend(subresults)

			if first_match_is_success:
				break

			# continue

		#SEQUENCE.decr_depth()

		SEQUENCE.DEBUGGER.match_exit(SEQUENCE, self, success=SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL)

		if SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL:

			#snap_out("match success", [(r,r.value()) for r in results])
			SEQUENCE.MATCH_START = START
			return ParseqRule___return_results__(self, SEQUENCE, results)

		# fail (already set)
		return None
	ENV.ParseqRule___perform_match_actual__ = ParseqRule___perform_match_actual__


	def ParseqRule___perform_match__(self, SEQUENCE, first_match_is_success):

		self.push_settings(SEQUENCE)
		_return = ParseqRule___perform_match_actual__(self, SEQUENCE, first_match_is_success)
		self.pop_settings(SEQUENCE)
		return _return
	ENV.ParseqRule___perform_match__ = ParseqRule___perform_match__


	def ParseqRule___search__(self, SEQUENCE, SKIP_NONCAPTURING, KEEP_SEARCHING):

		# this is so we can use the user level search api internally (without forcing the return of a single result...)

		SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL

		ORIGINAL_START = SEQUENCE.position()
		while 1:

			#print('>>> reset match')
			SEQUENCE.DEBUGGER.reset()

			START = SEQUENCE.position() # NOTE: on success SEQUENCE.position() will be same as SEQUENCE.MATCH_END

			subresults = self.__match__(SEQUENCE)

			if SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL:

				#snap_out('success', SEQUENCE.position(), [SEQUENCE.MATCH_START, SEQUENCE.MATCH_END], ORIGINAL_START, START, subresults)

				SEQUENCE.set(position=SEQUENCE.MATCH_END)

				if not subresults and SKIP_NONCAPTURING:
					if SEQUENCE.position() == START:
						if not SEQUENCE.__advance__():
							break
							#if SEQUENCE.position() == START:
								# allows one out of bounds match
							#	SEQUENCE.set(position=START+SEQUENCE.step())
							#else:
							#	break
					#snap_out('skip noncapturing', START)
					continue

				if SEQUENCE.MATCH_START == SEQUENCE.MATCH_END: # non-advancing rule (like NOT())

					if not SEQUENCE.__advance__():
						# normally we would just stop here, but we want to allow one match
						# out of bounds (so we can have results at the very end...)
						# we determine EOF by the advance clamping position, resulting in MATCH_END being beyond
						# position, so ParseqSequences need to set their position properly for this to work!

						#snap_out('no advance', START, SEQUENCE.position(), [SEQUENCE.MATCH_START, SEQUENCE.MATCH_END], SEQUENCE.length())

						if SEQUENCE.position() == START:
							# allows one (non-advancing) out of bounds match
							SEQUENCE.set(position=START+SEQUENCE.step())
							#snap_out('continue', SEQUENCE.position())
						else:
							#snap_out('fail', SEQUENCE.position())
							SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
							return None

					#if 0:#not SEQUENCE.__advance__() and SEQUENCE.MATCH_START == START:
					#	SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL # force failure so caller doesn't continue...
					#	snap_warning("force fail", SEQUENCE.position())
					#	return None

				return subresults
			else:
				if subresults:
					SEQUENCE.DEBUGGER.warning("subresults with no match")

				SEQUENCE.set(position=START)#+SEQUENCE.step())

			if KEEP_SEARCHING:

				if SEQUENCE.position() == START:
					# if we are in same position, force advance to next position (this can be a NOT() staying put but matching successfully...)
					if not SEQUENCE.__advance__():
						break
						#if SEQUENCE.position() == START:
							# allows one out of bounds match
						#	SEQUENCE.set(position=START+SEQUENCE.step())
							# TODO update START?
						#else:
						#	break
				#out('resume', START)
				continue

			break

		SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
		#snap_warning('set position back to', ORIGINAL_START)
		SEQUENCE.set(position = ORIGINAL_START)
		return None
	ENV.ParseqRule___search__ = ParseqRule___search__


	def ParseqRule_search(self, SEQUENCE, SKIP_NONCAPTURING, KEEP_SEARCHING):
		# this is the user-level call
		# subresults are contained in one toplevel result if there is more than one subresult

		subresults = ParseqRule___search__(self, SEQUENCE, SKIP_NONCAPTURING, KEEP_SEARCHING)
		if SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL:

			#out("subresults", subresults, SEQUENCE.MATCH_START, SEQUENCE.MATCH_END)

			if subresults and len(subresults) == 1:
				return subresults[0]

			# otherwise subresults are 0 or > 1, which require wrapping in a dummy ParseqResult to return to user
			# (return value indicates search success or failure at user level, for simplicity)
			return ParseqResult(sequence=SEQUENCE, rule=self, span=[SEQUENCE.MATCH_START, SEQUENCE.MATCH_END], subs=subresults)

		return None
	ENV.ParseqRule_search = ParseqRule_search
				
		




	class ParseqRule(object):

		# TODO __slots__

		def __match__(self, SEQUENCE):
			raise NotImplementedError(self, '__match__')

		def items(self):
			return self._items_

		def name(self):
			return self._name_

		def capture(self):
			return self._capture_

		def suppress(self):
			return self._suppress_

		def settings(self):
			# these are settings that can effect children, and are stored on the sequence in a push/pop fashion during the parse
			# local settings that only effect this rule are not included...
			return self._settings_

		def push_settings(self, SEQUENCE):

			# this is used by the parser as a means to keep track of active settings, since the sequence is always visible
			# and parse settings will always apply to either a rule or the sequence itself

			SEQUENCE.depth += 1
			SEQUENCE.rootpath.append(self) # TODO use linked list for this instead?

			rule_settings = SEQUENCE.rule_settings

			settings = self.settings()
			if settings:
				# save the return settings
				SEQUENCE.saved_rule_settings.append({k:rule_settings.get(k,None) for k in settings.keys()})
				# set the settings to current
				rule_settings.update(settings)
			else:
				SEQUENCE.saved_rule_settings.append(None)

		def pop_settings(self, SEQUENCE):

			# this info can be useful for debugging feedback
			SEQUENCE.depth -= 1
			SEQUENCE.rootpath.pop()

			undo_set = SEQUENCE.saved_rule_settings.pop()
			if undo_set:
				SEQUENCE.rule_settings.update(undo_set)

		def set(self, **kwargs):
			
			for attr,value in kwargs.items():
				if attr == 'name':
					self._name_ = value
				elif attr == 'items':
					self._items_ = list(value)
					for idx,item in enumerate(self._items_):
						# convert any text into ParseqITEM instances instead

						if not isinstance(item, (str,bytes)):
							assert isinstance(item, ParseqRule), 'not a rule? {}'.format(item)
							continue

						#snap_out("new item", repr(item))
						self._items_[idx] = ParseqITEM(value=item, name=item, capture=False)

				elif attr == 'item':
					if value:
						self.set(items = [value])
					else:
						raise ValueError("null item?")

				elif attr == 'capture':
					# None to disable, otherwise bool value will apply to (only) self
					self._capture_ = value

				elif attr == 'suppress':
					self._suppress_ = bool(value)

				elif attr in ('capture_all', 'simplify', 'skip', 'ignore'):
					# NOTE: to explicitly prevent skip/ignore of a parent the subrule must be set
					# explicitly to non-null value; use an empty ANY() to prevent a successful match

					settings = self._settings_ or {}
					if value is None:
						try: del settings[attr]
						except: pass
					else:
						settings[attr] = value
					if not settings:
						settings = None
					self._settings_ = settings

				else:
					raise NameError('unknown setting', attr)

		# NOTE: this is user API ("__MATCH__" is internal API), call these with snap_event(self, "MATCH", "sequence", SEQUENCE, ...)
		def match(self, SEQUENCE):
			# user api: attempt to match at current position of sequence (already set)
			# if non-capturing, wrap in dummy result and returns that (must return result on success)
			return ParseqRule_search(self, SEQUENCE, False, False)

		def match_with_result(self, SEQUENCE):
			# same as MATCH but if non-capturing result is returned it will try again at the next position until match fails or capturing result is returned
			return ParseqRule_search(self, SEQUENCE, True, False)

		def find(self, SEQUENCE):
			# user api: find first match, skipping over all non-matches (iterates "MATCH" until success)
			return ParseqRule_search(self, SEQUENCE, False, True)

		def search(self, SEQUENCE):
			return self.find(SEQUENCE)

		def find_with_result(self, SEQUENCE):
			# similar to MATCH_WITH_RESULT; will keep searching until a result that is capturing is found
			return ParseqRule_search(self, SEQUENCE, True, True)

		def search_with_result(self, SEQUENCE):
			return self.find_with_result(SEQUENCE)

		# TODO make this find_subrule() and make it work just like ParseqResult find does...
		# TODO also make walk for rules...
		def get_namedXXX(self, *PATH):
			# path is a list of names in find order (each name is found in the previous named items)

			items = self.items()

			if len(PATH) < 1 or not items:
				return None

			seen = []

			# this is a breadth-first search per-term, continuing with children if there are more
			# so once we find the term, clear the queue

			# we are queueing up with current path, until we match the term, in which case we clear the queue and queue up the next subitems and next subterm (unless no more subterms then it is a success)

			queue = [(item, PATH[0], PATH[1:]) for item in items]
			while queue:

				item,this_term,next_terms = queue.pop(0)

				if snap_binary_search(seen, id(item), lambda x: id(x), False) > -1:
					continue
				seen.insert(snap_binary_search(seen, id(item), lambda x: id(x), True), item)

				subitems = item.items()
				if subitems:
					queue.extend([(t,this_term,next_terms) for t in subitems])

				item_name = item.name()
				#out(item_name, this_term, type(item).__qualname__, repr(getattr(item, '_value_', 'no value')))
				if item_name:
					if item_name != this_term:
						# this just means we don't queue it's subitems?
						continue
						#return None # XXX incorrect, we can keep attempting to match...
					else:
						if len(next_terms) < 1:
							# found
							return item
						else:
							del queue[:]
							subitems = item.items()
							if subitems:
								queue.extend([(t,next_terms[0],next_terms[1:]) for t in subitems])

			return None

		def find_subrule(self, *NAMES, index=None, **kwargs):

			if index is not None:
				if index < 0:
					try: return list(self.finditer_rules(*NAMES, **kwargs))[index]
					except: return None
				else:
					idx = 0
					for result in self.finditer_rules(*NAMES, **kwargs):
						if idx == index:
							return result
						idx += 1
			else:
				for result in self.finditer_rules(*NAMES, **kwargs):
					return result

		def finditer_rules(self, *NAMES, **kwargs):

			#if not (NAMES or kwargs):
			#	return None

			recurse = kwargs.get('recurse',True)

			_type = kwargs.get('_type', None)

			search_mode = kwargs.get('search_mode', kwargs.get('mode', 'DFS')) # or 'BFS'
			assert search_mode in ('DFS','BFS'), 'invalid search mode: {}'.format(repr(search_mode))

			SEEN = [self]
			QUEUE = list(self.items())
			while QUEUE:

				rule = QUEUE.pop(0)

				seen_idx = snap_binary_search(SEEN, id(rule), lambda x: id(x), True)
				if seen_idx < len(SEEN) and id(SEEN[seen_idx]) == id(rule):
					continue
				SEEN.insert(seen_idx, rule)

				next_subs = rule.items() # NOTE: not copied!
				if recurse:

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

					yield rule


		def swap_rules(self, swapdict=None):

			assert isinstance(swapdict, dict), 'invalid dict'

			def swap(ITEMS):
				return [swapdict.get(id(r),r) for r in ITEMS]

			return self.filter_for(swap)

			"""
			SEEN = []
			QUEUE = [self]
			while QUEUE:
				rule = QUEUE.pop(0)

				seen_idx = snap_binary_search(SEEN, id(rule), lambda x: id(x), True)
				if seen_idx < len(SEEN) and id(SEEN[seen_idx]) == id(rule):
					continue
				SEEN.insert(seen_idx, rule)

				items = rule.items()
				if items:
					swapped_items = [swapdict.get(id(r),r) for r in items]
					rule.set(items=swapped_items)

				QUEUE = items + QUEUE # walk the original items!
			"""

		def filter_for(self, CALLBACK):

			# this can be used to swap strings for bytes or bytes for strings, for example...

			assert CALLBACK is not None, 'must provide callback to filter the rules'
			#if CALLBACK is None:
			#	CALLBACK = lambda x:x

			SEEN = set()
			QUEUE = [self]
			while QUEUE:
				rule = QUEUE.pop(0)
				if id(rule) in SEEN:
					continue
				SEEN.add(id(rule))

				items = rule.items()
				if items:
					swapped_items = CALLBACK(items) # this allows removal
					rule.set(items=swapped_items)

				QUEUE = items + QUEUE # walks original items...


		def __repr__(self):

			type_name = type(self).__qualname__.replace('Parseq','').split('.')[-1]

			extras = []

			name = self.name()
			if name:
				extras.append(repr(name))

			capture = self.capture()
			if capture is not None:
				extras.append('capture={}'.format(capture))
			elif name:
				extras.append('capture=(True)')

			suppress = self.suppress()
			if suppress:
				extras.append('suppress={}'.format(suppress))

			if extras:
				extras = " " + " ".join(extras)
			else:
				extras = ""

			return '<{} {}{}>'.format(type_name, hex(id(self)), extras)

		def __repr_tree__(self, **SETTINGS):
			
			indent = SETTINGS.get('indent', '>')

			output = []		

			SEEN = []
			QUEUE = [(0,self)]
			while QUEUE:
				depth,rule = QUEUE.pop(0)
				idx = snap_binary_search(SEEN, id(rule), lambda x: id(x), True)
				if idx < len(SEEN) and id(SEEN[idx]) == id(rule):
					output.append('{} ...'.format(indent * depth))
					continue
				SEEN.insert(idx, rule)
				output.append('{} {}'.format(indent * depth, repr(rule)))
				QUEUE = [(depth+1, sub) for sub in rule.items()] + QUEUE

			return '\n'.join(output)

		def print_tree(self, **SETTINGS):
			print(self.__repr_tree__(**SETTINGS))

		def __init__(self, *ITEMS, **kwargs):

			if ITEMS:
				assert 'items' not in kwargs, 'items already in kwargs?'
				kwargs['items'] = ITEMS

			self._settings_ = None # settings which will impact children during match will go in here
			self._name_ = None
			self._items_ = []
			self._capture_ = None # unused by default
			self._suppress_ = False

			self.set(**{k:v for k,v in kwargs.items() if k in ('name', 'items', 'item', 'capture', 'suppress', 'capture_all', 'simplify', 'skip', 'ignore')})
	ENV.ParseqRule = ParseqRule



	class ParseqITEM(ParseqRule):

		def __match__(self, SEQUENCE):

			# doing this a little different to support items that can have multiple chars... (while sequence still iterates one char at a time -- or whatever the step is...)

			START = SEQUENCE.position()

			# TODO this just needs to be value == SEQ_ITEM!  then advance by len()
			# XXX that would work if sequence could return the full value, but that might not be the case,
			# item (and sequence) value can consist of multiple bytes or chars
			# -- maybe accum the full amount first, and then compare?

			value = self.value()

			if value:

				success = True # until proven otherwise

				len_value = len(value)

				# TODO make it a user option whether to parse backwards in reverse order or not?

				# NOTE: value[idx:idx+1] is because bytes[idx] returns an int which then won't compare!  need str and bytes to work the same!

				if SEQUENCE.step() < 0: # TODO just make this if self.force_forward() and SEQUENCE.step() < 0:
					# NOTE: if step is backward we are still comparing the item in forward orientation...
					idx = len_value
					while idx > 0:
						idx -= 1
						SEQ_ITEM = SEQUENCE.__advance__()
						#snap_out('backward', SEQUENCE.step(), len_value, repr(value), repr(SEQ_ITEM))
						if not SEQ_ITEM or value[idx:idx+1] != SEQ_ITEM:
							success = False
							break
				else:
					idx = 0
					while idx < len_value:
						SEQ_ITEM = SEQUENCE.__advance__()
						#snap_out('advance', SEQUENCE.step(), len_value, repr(value), repr(SEQ_ITEM))
						if not SEQ_ITEM or value[idx:idx+1] != SEQ_ITEM:
							# TODO when using bytes, value[idx] is an int, SEQ_ITEM is... something else?
							#print('fail', SEQ_ITEM, value[idx:idx+1], type(value[idx]), type(SEQ_ITEM))
							success = False
							break
						idx += 1

				if success:
					SEQUENCE.MATCH_START = START
					SEQUENCE.MATCH_END = SEQUENCE.position()
					return ParseqRule___return_results__(self, SEQUENCE, None)

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return None

		def __compare__(self, ITEM):

			if ITEM:

				if isinstance(ITEM, (bytes,str)):
					ITEM_value = ITEM
				elif isinstance(ITEM, ParseqITEM): # TODO what about ParseqLayerITEM?  this will evaluate to True for that...
					ITEM_value = ITEM.value()
				else:
					#raise TypeError('not a comparable item type!', repr(ITEM))
					if id(self) < id(ITEM): return -1
					elif id(self) > id(ITEM): return 1
					return 0
				value = self.value()

				if ITEM_value and value:
					#print('compare', ITEM_value, value, type(ITEM_value), type(value))

					if value < ITEM_value: return -1
					elif value > ITEM_value: return 1
					return 0

			return -1


		# python and snap names...
		def __less_than__(self, ITEM):
			return self.__compare__(ITEM) < 0

		def __lt__(self, ITEM):
			return self.__less_than__(ITEM)

		def __less_equal__(self, ITEM):
			return self.__compare__(ITEM) <= 0

		def __le__(self, ITEM):
			return self.__less_equal__(ITEM)

		def __greater_than__(self, ITEM):
			return self.__compare__(ITEM) > 0

		def __gt__(self, ITEM):
			return self.__greater_than__(ITEM)

		def __greater_equal__(self, ITEM):
			return self.__compare__(ITEM) >= 0

		def __ge__(self, ITEM):
			return self.__greater_equal__(ITEM)

		def __equal__(self, ITEM):
			return self.__compare__(ITEM) == 0

		def __eq__(self, ITEM):
			return self.__equal__(ITEM)

			
		def value(self):
			return self._value_

		def set(self, **kwargs):

			for k,v in kwargs.items():

				if k == 'value':
					self._value_ = v

				else: ParseqRule.set(self, **{k:v})

		def __init__(self, *args, **kwargs):
			ParseqRule.__init__(self, *args, **kwargs)

			if args:
				assert 'value' not in kwargs and len(args) == 1 and isinstance(args[0], (str,bytes)), 'incorrect args for ParseqITEM'
				kwargs['value'] = args[0]

			self._value_ = None

			self.set(**{k:v for k,v in kwargs.items() if k in ('value,')})
	ENV.ParseqITEM = ParseqITEM



	class ParseqAND(ParseqRule):

		def __match__(self, SEQUENCE):
			return ParseqRule___perform_match__(self, SEQUENCE, False)
	ENV.ParseqAND = ParseqAND



	class ParseqREPEAT(ParseqRule):

		def __match__(self, SEQUENCE):

			START = SEQUENCE.position()
			LAST_END = START
			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL

			results = []

			count = 0
			while self._range_[1] < 0 or count < self._range_[1]:

				subresults = ParseqRule___perform_match__(self, SEQUENCE, False)
				if SEQUENCE.MATCH_END == PARSEQ_MATCH_FAIL:
					if subresults:
						SEQUENCE.DEBUGGER.warning("subresults returned on fail")
					break

				if subresults:
					# NOTE: subresults are for self, we don't want to return self in subresults when we're matching repeatedly!
					# So we have to check if self is in results because it won't be if self isn't capturing!
					if len(subresults) == 1 and subresults[0].rule() == self:
						subresults = subresults[0].subs()
					results.extend(subresults)

				SEQUENCE.set(position = SEQUENCE.MATCH_END)

				if count == 0:
					START = SEQUENCE.MATCH_START
				count += 1

				if LAST_END == SEQUENCE.MATCH_END:
					if not SEQUENCE.__advance__():
						break
					LAST_END = SEQUENCE.position()
				else:
					LAST_END = SEQUENCE.MATCH_END

			if count >= self._range_[0] and (self._range_[1] < 0 or count <= self._range_[1]):
				# success

				SEQUENCE.MATCH_START = START
				SEQUENCE.MATCH_END = LAST_END # will be START if didn't match

				if 0:#count == 0 and count == self._range_[0]:
					# success but nothing there; no capture and no advance (an optional lookahead)
					#snap_out('REPEAT success but nothing?', results, START, LAST_END)
					return

				# now capture self (unless told otherwise)
				return ParseqRule___return_results__(self, SEQUENCE, results)

			# unsuccessful match
			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return


		def range(self):
			return self._range_

		def min(self):
			return self._range_[0]

		def max(self):
			return self._range_[1]

		def set(self, **kwargs):

			for k,v in kwargs.items():

				if k == 'min':
					self._range_[0] = v
				elif k == 'max':
					self._range_[1] = v
				elif k == 'range':
					assert v and len(v) == 2, 'incorrect number of elements for range'
					self._range_[:] = v[:]

				else: ParseqRule.set(self, **{k:v})

		def __init__(self, *args, **kwargs):
			ParseqRule.__init__(self, *args, **kwargs)

			self._range_ = [2,-1] # defaults to "2 or more up to <infinity>", since once is not conceptually a "repeat"

			self.set(**{k:v for k,v in kwargs.items() if k in ('range', 'min', 'max')})
	ENV.ParseqREPEAT = ParseqREPEAT
					

	class ParseqOR(ParseqRule):

		def __match__(self, SEQUENCE):
			return ParseqRule___perform_match__(self, SEQUENCE, True)
	ENV.ParseqOR = ParseqOR

	class ParseqNOT(ParseqRule):

		def __match__(self, SEQUENCE):

			# inverts truth of submatch; non-capturing, non-advancing AND (or negative lookahead)
		
			START = SEQUENCE.position()

			subresults = ParseqRule___perform_match__(self, SEQUENCE, False)

			if SEQUENCE.MATCH_END == PARSEQ_MATCH_FAIL:
				# unmatched = success
				SEQUENCE.MATCH_START = START
				SEQUENCE.MATCH_END = START # non-advance; start is same position (higher logic will advance in some contexts)
				# no capturing subresults
				return ParseqRule___return_results__(self, SEQUENCE, None)
			else:
				# matched = fail
				SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL;

			#out('set back to', START)
			#SEQUENCE.set(position = START) # never advances
			return
	ENV.ParseqNOT = ParseqNOT



	class ParseqANY(ParseqRule):

		def __match__(self, SEQUENCE):
			# this is an OR but with ParseqITEM subclasses only, so they can be pre-sorted and searched more efficiently

			START = SEQUENCE.position()

			items = self.items()
			SEQ_ITEM = SEQUENCE.__advance__()
			if SEQ_ITEM and items:
				LAST_END = SEQUENCE.position()
				return_item = None
				#if isinstance(SEQ_ITEM.value(), (str,bytes)) and isinstance(items[0].value(), (str,bytes)):
				if isinstance(SEQ_ITEM, (str,bytes)) and isinstance(items[0].value(), (str,bytes)):
					dummy = ParseqITEM(value=SEQ_ITEM)#.value())

					# TODO this could likely be sped up by doing the binary search internally, and just continuing on when failed?
					# write it specially to compare the last (current item) and the length?

					# TODO
					"""
					get seq_item that is length of longest self.item
					do binary search and run to end (can we lambda compare considering length and order?)
					try for longest and if fail then we have the insertion point next to the other candidates...?  (if they are sorted by string content...)
					"""

					# we have to match longest first and then check the shorter ones (longest is the match to return)
					# this is pretty hacky right now, but should work
					longest = max([len(item.value()) for item in items])
					while len(dummy.value()) < longest:
						SEQ_ITEM = SEQUENCE.__advance__()
						if not SEQ_ITEM:
							break # NOTE: match is still possible!
						dummy.set(value=dummy.value() + SEQ_ITEM)#.value())
						LAST_END = SEQUENCE.position()

					while dummy._value_ and len(dummy._value_) > 0:
						idx = snap_binary_search(items, dummy, lambda x: x, False)
						if idx > -1:
							return_item = items[idx]
							break
						dummy._value_ = dummy._value_[:-1]
						LAST_END -= 1

					# XXX this won't find '1' or '123' if '12' is not in sequence!  we need to match against longest first!
					"""
					idx = 0
					while 1:
						idx = binary_search(items[idx:], dummy, lambda x: x, False)
						if idx < 0:
							break
						return_item = items[idx]
						LAST_END = SEQUENCE.position()
						SEQ_ITEM = SEQUENCE.__advance__()
						if not SEQ_ITEM:
							break
						dummy.set(value=dummy.value() + SEQ_ITEM.value())
					"""
				else:				
					idx = snap_binary_search(items, SEQ_ITEM, lambda x: x.value(), False)
					if idx > -1:
						# success!
						return_item = items[idx]

				if return_item:
					# success
					SEQUENCE.MATCH_START = START
					SEQUENCE.MATCH_END = LAST_END
					# NOTE: simulates item being it's own match... (since item __match__ wasn't called...)
					return ParseqRule___return_results__(self, SEQUENCE, ParseqRule___return_results__(return_item, SEQUENCE, None))

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return

		def set(self, **kwargs):

			for k,v in kwargs.items():

				if k == 'items':

					user_items = v

					for item in user_items:
						if not isinstance(item, (ParseqITEM,str,bytes)):
							raise TypeError("non-items are not allowed in ANY/NOTANY items!")

					ParseqRule.set(self, items=v)
					if self._items_:
						self._items_[:] = sorted(self._items_)

				else: ParseqRule.set(self, **{k:v})
	ENV.ParseqANY = ParseqANY


	class ParseqNOTANY(ParseqANY):

		def __match__(self, SEQUENCE):
		
			# NOTE: this is different than NOT(ANY()) which would be non-capturing; this is capturing! (ie. an item match not a rule match; if the sequence item is not any of these items, capture it)

			# non-capturing by default, but advancing since it is an item!

			START = SEQUENCE.position()

			subresults = ParseqANY.__match__(self, SEQUENCE)
			if SEQUENCE.MATCH_END == PARSEQ_MATCH_FAIL:
				# unmatched = success, advance one item

				if subresults:
					warning("subresults in NOTANY when failed to match!")

				SEQUENCE.set(position = START)
				if SEQUENCE.__advance__():
					SEQUENCE.MATCH_START = START
					SEQUENCE.MATCH_END = SEQUENCE.position()
					return ParseqRule___return_results__(self, SEQUENCE, None)


			# matched = fail; no advance is also fail
			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return
	ENV.ParseqNOTANY = ParseqNOTANY




	class ParseqAHEAD(ParseqRule):

		def __match__(self, SEQUENCE):

			START = SEQUENCE.position()

			subresults = ParseqRule___perform_match__(self, SEQUENCE, False)
			SEQUENCE.set(position = START) # always back to start
			if SEQUENCE.MATCH_END != PARSEQ_MATCH_FAIL:
				# success but no advance or capture
				SEQUENCE.MATCH_START = START
				SEQUENCE.MATCH_END = START
				return ParseqRule___return_results__(self, SEQUENCE, None)

			# fail (already set)
			return
	ENV.ParseqAHEAD = ParseqAHEAD


	class ParseqBEHIND(ParseqRule):

		def __match__(self, SEQUENCE):
			# starts matching rules in same forwards order but going backwards
			# so to match "abcx" you would use AND(BEHIND("c", "b", "a"), "x");

			SEQUENCE.reverse()
			subresults = ParseqAHEAD.__match__(self, SEQUENCE)
			SEQUENCE.reverse()
		
			return subresults
	ENV.ParseqBEHIND = ParseqBEHIND



	class ParseqOPTIONAL(ParseqREPEAT):

		def __match__(self, SEQUENCE):
			results = ParseqREPEAT.__match__(self, SEQUENCE)
			# only capture the OPTIONAL if it is explicitly set to capture, or it spans > 0
			if not (self.capture() or self.suppress()) and results:
				s = results[0].start()
				e = results[-1].end()
				if max(s,e) - min(s,e) == 0:
					#print('non-capturing option')
					return None
			return results

		def set(self, **kwargs):
		
			for k,v in kwargs.items():
				if k in ('min', 'max', 'range'):
					raise ValueError("ParseqOPTIONAL forbids set(\"{}\") as it is fixed at range(0,1)".format(k))

				else: ParseqREPEAT.set(self, **{k:v})

		def __init__(self, *args, **kwargs):
			ParseqREPEAT.__init__(self, *args, **kwargs)

			self._range_[:] = [0,1]
	ENV.ParseqOPTIONAL = ParseqOPTIONAL


	# NOTE replaced ParseqSTART and ParseqEND with the more generic:
	class ParseqPOSITION(ParseqRule):

		# this returns true if sequence is at self.position(), false otherwise

		def __match__(self, SEQUENCE):

			length = SEQUENCE.length()
			pos = SEQUENCE.position()

			success = False

			position = self.position()
			if position < 0:
				# from the end
				if pos <= length and length + position == pos:
					success = True
			else:
				if pos == position:
					success = True

			if success:
				SEQUENCE.MATCH_START = SEQUENCE.MATCH_END = SEQUENCE.position()
				return ParseqRule___return_results__(self, SEQUENCE, None)

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return

		def position(self):
			return self._position_

		def set(self, **kwargs):

			for k,v in kwargs.items():
				if k == 'position':
					self._position_ = int(v)

				else: ParseqRule.set(self, **{k:v})

		def __init__(self, *args, **kwargs):
			ParseqRule.__init__(self, *args, **kwargs)

			self._position_ = 0

			self.set(**{k:v for k,v in kwargs.items() if k in ('position',)})
	ENV.ParseqPOSITION = ParseqPOSITION



	class ParseqRANGE(ParseqRule):

		# for listing items in a range of values (without having to make an item for each!)  like a-z, A-Z, 0-9, etc...

		def __match__(self, SEQUENCE):

			# TODO sequence needs to report item, maybe sequence stores active item in node it passes back?  so items could be in a tree...  and the sequence could walk the tree and present it as flat...  would be useful for encoding...?
			
			START = SEQUENCE.position()

			SEQ_ITEM = SEQUENCE.__advance__()
			items = self.items()
			if SEQ_ITEM and items and len(items) == 2:
				
				min_item = items[0]
				max_item = items[1]

				#if SEQ_ITEM.__compare__(min_item) >= 0 and SEQ_ITEM.__compare__(max_item) <= 0:
				if SEQ_ITEM >= min_item and SEQ_ITEM <= max_item:
					# success

					SEQUENCE.MATCH_START = START
					SEQUENCE.MATCH_END = SEQUENCE.position()
					return ParseqRule___return_results__(self, SEQUENCE, None)

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return


		def set(self, **kwargs):

			for k,v in kwargs.items():

				if k == 'items':
					
					assert v and len(v) == 2, 'invalid range items, must be 2!'
					for item in v:
						assert isinstance(item, (ParseqITEM,str,bytes)), 'range items must be items!'

					ParseqRule.set(self, items=v)

				else:
					ParseqRule.set(self, **{k:v})
	ENV.ParseqRANGE = ParseqRANGE



	class ParseqUNDEFINED(ParseqRule):

		# TODO user can either pass in definitions to use (for any name) or undefined items can be set to 1 item to use for the definition

		def __match__(self, SEQUENCE):
			items = self._items_
			if items:
				return items[0].__match__(SEQUENCE)

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return None

		#def name(self):
		#	return None # TODO or return as passthrough to subitem?  make this act invisible?

		def capture(self):
			return False

		def suppress(self):
			return False

		def set(self, **kwargs):

			for k,v in kwargs.items():

				if k == 'item':
					assert isinstance(v, ParseqRule), 'non-rule may not be used in UNDEFINED definition'
					self.set(items=[v])

				elif k == 'items':
					if v:
						assert len(v) == 1 and not isinstance(v[0], ParseqUNDEFINED), 'only one (non-UNDEFINED) item may be used as the definition of an UNDEFINED rule'
						self._items_ = list(v)
					else:
						self._items_ = []
				elif k == 'define':
					self.set(item=v)

				elif k in ('capture','suppress'):
					warning("unsupported setting: '{}'".format(k))

				else:
					ParseqRule.set(self, **{k:v})

		def __init__(self, *args, **kwargs):
			ParseqRule.__init__(self, *args, **kwargs)
	ENV.ParseqUNDEFINED = ParseqUNDEFINED



	class ParseqRECALL(ParseqRule):

		def __trim_results(self, DEPTH):

			# removes any results >= DEPTH unless no results left?  keeps last results assigned to -1 depth
			# TODO should optional result be saved separately?  or maybe set it's depth to -1?  so we know it is invalid?
			# XXX don't set to -1, just remove, if depth is < then it can't match again until primary match occurs
			results = self._results_ or []
			length = original_length = len(results)
			while length > 0:
				if length == 1:
					# last item?
					if results[0] < DEPTH:
						results[0] = -1
					break
				else:
					if results[-1] <= DEPTH:
						# keep
						break
					# otherwise remove and nullify
				length -= 1

			if length < original_length:
				self._results_ = results[:length]
			
			return None

		def __init__(self, *args, **kwargs):
			ParseqRule.__init__(self, *args, **kwargs)

			self._use_depth_ = True
			self._results_ = []
	ENV.ParseqRECALL = ParseqRECALL


	"""
	any ParseqRECALL_event(SnapObject* self, any EVENT, SnapObject* MSG){
		// XXX maybe just expect to implement this behaviour at a higher level?  it would be easier to check the result of the search...

		// TODO untested...	

		if (EVENT == (any)"__MATCH__"){

			SnapObject SEQUENCE = (SnapObject)snap_getattr(MSG, "sequence");
			ParseqSequence_info_t* info = (ParseqSequence_info_t*)snap_event_noargs(&SEQUENCE, "info");
			if (!info){
				snap_error("no sequence info in %s", SNAP_FUNCTION_NAME);
				return NULL;
			}

			if (snap_event_noargs(self, "is_primary") == (any)"TRUE"){
				// normal match, span stored under current depth

				//snap_int START = info->POS;

				// first attempt to sub-match and make sure it is successful
				SnapList subresults = __ParseqRule_perform_match(self, MSG, 0);
				
				if (info->MATCH_END != PARSEQ_MATCH_FAIL){
					// success

					SnapList _results_ = (SnapList)snap_getattr_at(self, "_results_", IDX_ParseqRECALL__results_);

					snap_int entry[3] = {info->DEPTH, info->MATCH_START, info->MATCH_END};

					if (snap_event_noargs(self, "use_depth") == (any)"TRUE"){

						_ParseqRECALL_trim_results(&_results_, info->DEPTH);
						if (SnapList_length(&_results_) > 0 && (
							*(int*)_results_->data[SnapList_length(&_results_)-1] == info->DEPTH ||
							*(int*)_results_->data[SnapList_length(&_results_)-1] == -1)){
							// assign (existing -1 assign will be overwritten)
							snap_memcpy(_results_->data[SnapList_length(&_results_)-1], entry, 3 * sizeof (int));
						}
						else {
							// append
							int* e = (int*)snap_malloc(3 * sizeof (int));
							if (!e){
								snap_error("%s unable to allocate entry!", SNAP_FUNCTION_NAME);
							}
							snap_memcpy(e, entry, 3 * sizeof (int));
							SnapList_append(&_results_, e);
						}
						snap_event(&SEQUENCE, "LISTEN", *self); // for depth change events
					}
					else {
						// just set results to this match
						if (SnapList_length(&_results_) < 1){
							// append
							int* e = (int*)snap_malloc(3 * sizeof (int));
							if (!e){
								snap_error("%s unable to allocate entry!", SNAP_FUNCTION_NAME);
							}
							snap_memcpy(e, entry, 3 * sizeof (int));
							SnapList_append(&_results_, e);
						}
						else {
							// assign (assume only one entry)
							if (SnapList_length(&_results_) > 1){
								int length = SnapList_length(&_results_);
								while (length > 1){
									snap_free(_results_->data[length-1]);
									_results_->data[length-1] = NULL;
									length--;
								}
								SnapList_realloc(&_results_, 1);
							}
							snap_memcpy(_results_->data[SnapList_length(&_results_)-1], entry, 3 * sizeof (int));
						}
					}

					return (any)__ParseqRule_return_results(self, MSG, &subresults, info->MATCH_START, info->MATCH_END);
				}
				#ifdef SNAP_DEBUGGING_PARSEQ
				else {
					if (subresults){
						snap_warning("%s subresults on match fail!", SNAP_FUNCTION_NAME);
					}
				}
				#endif
			}

			else {
				// secondary, compare to referring recall rule
				SnapList items = (SnapList)snap_event_noargs(self, "items");
				SnapObject primary = (SnapList_length(&items) == 1) ? (SnapObject)items->data[0] : NULL;
				SnapList primary_results = (SnapList)snap_getattr_at(&primary, "_results_", IDX_ParseqRECALL__results_);
				int* entry = (SnapList_length(&primary_results) > 0) ? (int*)primary_results->data[SnapList_length(&primary_results)-1] : NULL;

				if (entry){

					info->MATCH_END = PARSEQ_MATCH_FAIL;

					snap_int START = info->POS;

					snap_int primary_range[2] = {entry[1], entry[2]};
					snap_int primary_step = (primary_range[0] < primary_range[1]) ? info->STEP : info->STEP * -1;
					snap_int primary_pos = (primary_range[0] < primary_range[1]) ? primary_range[0] : primary_range[1];

					snap_int size = primary_range[2] - primary_range[1];
					if (size < 0)
						size *= -1;

					snap_int secondary_range[2] = {START, START + (info->STEP > 0) ? size : size * -1};
					snap_int secondary_step = info->STEP;
					snap_int secondary_pos = (secondary_range[0] < secondary_range[1]) ? secondary_range[0] : secondary_range[1];

					if (size != 0 && primary_step != 0 && secondary_step != 0){

						snap_int item_size;
						any get_value;

						SnapObject primary_item = SnapObject_create(SNAP_ENV, ParseqITEM_event, "size", NULL, "value", NULL);
						SnapObject item;

						while (1){

							info->STEP = primary_step;
							info->POS = primary_pos;

							item = (SnapObject)snap_event_noargs(&SEQUENCE, "__ADVANCE__");
							if (!item)
								break;

							snap_copyattr_at(&item, "_size_", &item_size, sizeof (snap_int), IDX_ParseqITEM__size_);
							get_value = snap_getattr_at(&item, "_value_", IDX_ParseqITEM__value_);

							snap_assignattr_at(&primary_item, "_size_", &item_size, sizeof (snap_int), IDX_ParseqITEM__size_);
							snap_assignattr_at(&primary_item, "_value_", get_value, item_size, IDX_ParseqITEM__value_);

							info->STEP = secondary_step;
							info->POS = secondary_pos;

							item = (SnapObject)snap_event_noargs(&SEQUENCE, "__ADVANCE__");
							if (!item)
								break;

							if (snap_event(&primary_item, "COMPARE_ITEM", item) != (any)"0")
								break;

							primary_pos += item_size * ((primary_step > 0) ? 1 : -1);
							secondary_pos += item_size * ((secondary_step > 0) ? 1 : -1);

							if (
								(primary_step > 0 && primary_pos >= primary_range[1]) ||
								(primary_step < 0 && primary_pos <= primary_range[0])
								){

								if (
									(primary_step > 0 && primary_pos == primary_range[1]) ||
									(primary_step < 0 && primary_pos == primary_range[0])
									){
									info->MATCH_END = secondary_pos;
								}
								break;
							}
						}

						snap_assignattr_at(&primary_item, "_value_", NULL, 0, IDX_ParseqITEM__value_);
						snap_event_noargs(&primary_item, "DELETE");

						if (info->MATCH_END != PARSEQ_MATCH_FAIL){
							// TODO info->MATCH_START?
							return (any)__ParseqRule_return_results(self, MSG, NULL, START, info->MATCH_END);
						}
					}				
				}
				#ifdef SNAP_DEBUGGING_PARSEQ
				else {
					snap_warning("secondary recall has no primary recall!");
				}
				#endif
			}

			info->MATCH_END = PARSEQ_MATCH_FAIL;
			return NULL;
		}

		if_ID

			if (EVENT == (any)"CHANGED"){
				int* depth = (int*)snap_getattr(MSG, "depth");
				if (depth){

					SnapList _results_ = (SnapList)snap_getattr_at(self, "_results_", IDX_ParseqRECALL__results_);
					_ParseqRECALL_trim_results(&_results_, *depth);

					if (SnapList_length(&_results_) < 1 || *(int*)_results_->data[0] == -1){
						// ignore SEQUENCE (ID is sequence)
						#ifdef SNAP_DEBUGGING_PARSEQ
						if (!snap_event((SnapObject*)&ID, "ISINSTANCE", ParseqSequence_event)){
							snap_warning("%s \"%s\" \"depth\" ID is not ParseqSequence_event type!", SNAP_FUNCTION_NAME, (char*)EVENT);
						}
						#endif
						snap_event((SnapObject*)&ID, "IGNORE", *self);
					}
				}

				#if 0
				else {
					SnapList items = (SnapList)snap_getattr_at(self, "_items_", IDX_ParseqRule__items_);
					if (SnapList_length(&items) == 1 && items->data[0] == ID && snap_getattr_at((SnapObject*)&ID, "is_primary", IDX_ParseqRECALL_is_primary) == (any)"TRUE"){
						// TODO changed
					}
				}
				#endif

				// TODO if primary item changed, update secondary/primary status of self?
			}

			else if (EVENT == (any)"__GC__"){

			}

			return ParseqRule_event(self, EVENT, MSG);
		}

		else if (EVENT == (any)"use_depth" || EVENT == (any)"uses_depth")
			return snap_bool(snap_getattr_at(self, "use_depth", IDX_ParseqRECALL_use_depth));

		else if (EVENT == (any)"is_primary"){
			SnapList items = (SnapList)snap_event_noargs(self, "items");
			return (SnapList_length(&items) == 1 && snap_event((SnapObject*)&items->data[0], "ISINSTANCE", ParseqRECALL_event)) ?
				(any)"FALSE" : (any)"TRUE";
		}


		else if (EVENT == (any)"SET"){

			for_attr_in_SnapObject(MSG)

				if (attr == (any)"use_depth"){
					snap_setattr_at(self, "use_depth", snap_bool(value), IDX_ParseqRECALL_use_depth);
				}
				
				else snap_event_redirect(ParseqRule_event, self, EVENT, attr, value);
			}
			return NULL;
		}

		else if (EVENT == (any)"INIT"){
			ParseqRule_event(self, EVENT, MSG);

			IDX_RESERVE(ParseqRECALL);
			IDX_UPDATE(ParseqRECALL);

			if (snap_getattr_at(self, "use_depth", IDX_ParseqRECALL_use_depth) == NULL){
				snap_setattr_at(self, "use_depth", "FALSE", IDX_ParseqRECALL_use_depth);
			}

			SNAPLIST(args, "use_depth");
			for_attr_in_SnapObject(MSG)
				if (SnapList_find(&args, attr) > -1){
					snap_event(self, "SET", attr, value);
				}
			}

			return NULL;
		}

		else if (EVENT == (any)"DELETE"){

			snap_delattrs(self, "use_depth");

			SnapList results = (SnapList)snap_getattr_at(self, "_results_", IDX_ParseqRECALL__results_);
			snap_delattr(self, "_results_");
			{for_item_in_SnapList(&results)
				snap_free(item);
			}}
			SnapList_delete(&results);

		}

		else_if_isinstance(ParseqRECALL_event)

		return ParseqRule_event(self, EVENT, MSG);
	}

	"""

	# this is just so unique errors can be created by subclassing and we can say if isinstance(result.rule(), ParseqERROR):
	class ParseqERROR(ParseqNOTANY):

		def set(self, **SETTINGS):
			for attr,value in SETTINGS.items():
				if attr in ('item', 'items'):
					raise NameError("ParseqERROR.set({}) not allowed".format(repr(attr)))
				else:
					ParseqNOTANY.set(self, **{attr:value})
			return None

		def __init__(self):
			ParseqNOTANY.__init__(self)
	ENV.ParseqERROR = ParseqERROR

	# NOTE: these mostly don't do anything right now, but I'm just leaving them here
	ITEM = ParseqITEM
	REPEAT = ParseqREPEAT
	AND = ParseqAND
	OR = ParseqOR
	NOT = ParseqNOT
	ANY = ParseqANY
	NOTANY = ParseqNOTANY
	AHEAD = ParseqAHEAD
	BEHIND = ParseqBEHIND
	OPTIONAL = ParseqOPTIONAL
	POSITION = ParseqPOSITION
	RANGE = ParseqRANGE
	# TODO RECALL?
	UNDEFINED = ParseqUNDEFINED
	ENV.PARSEQ_ERROR = NOTANY(name='ERROR', capture=True)

	def parseq_finditer(SEARCH_FUNCTION, SEQUENCE):
		while 1:
			result = SEARCH_FUNCTION(SEQUENCE)
			if not result:
				break
			# NOTE: result can still be error match...
			yield result



def main(ENV):

	snap_out = ENV.snap_out
	snap_test_out = ENV.snap_test_out
	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error

	ParseqSequence = ENV.ParseqSequence

	ParseqITEM = ENV.ParseqITEM
	ParseqREPEAT = ENV.ParseqREPEAT
	ParseqAND = ENV.ParseqAND
	ParseqOR = ENV.ParseqOR
	ParseqNOT = ENV.ParseqNOT
	ParseqANY = ENV.ParseqANY
	ParseqNOTANY = ENV.ParseqNOTANY
	ParseqAHEAD = ENV.ParseqAHEAD
	ParseqBEHIND = ENV.ParseqBEHIND
	ParseqOPTIONAL = ENV.ParseqOPTIONAL
	ParseqPOSITION = ENV.ParseqPOSITION
	ParseqRANGE = ENV.ParseqRANGE
	ParseqUNDEFINED = ENV.ParseqUNDEFINED
	ERROR = ENV.PARSEQ_ERROR

	def ParseqRule_verify_and_discard_result(result, EXPECT_START, EXPECT_END):

		status = 0

		if result:
			span = result.span()
			if span[0] > -1 and span[1] > -1 and span[0] == EXPECT_START and span[1] == EXPECT_END:
				status = 1
		else:
			if EXPECT_START < 0 and EXPECT_END < 0:
				status = 1
			
			#snap_out("no result")

		if not status:
			snap_error(result, EXPECT_START, EXPECT_END)

		return status


	def ParseqRule_search_test(rule_handler, REVERSE, TEXT, EXPECT_START, EXPECT_END, *TEXT_ITEMS):

		if rule_handler == ParseqITEM:
			assert len(TEXT_ITEMS) == 1, 'item can only accept one arg'
			rule = rule_handler(value=TEXT_ITEMS[0])
		else:
			rule = rule_handler(items=[ParseqITEM(value=item) for item in TEXT_ITEMS])

		SEQ = ParseqSequence(source=TEXT)

		if REVERSE:
			SEQ.reverse()
			SEQ.rewind()
	
		return ParseqRule_verify_and_discard_result(rule.search(SEQ), EXPECT_START, EXPECT_END)


	TESTS = [

		"ITEM", # TODO!

		"AND",
		"OR",
		"NOT",
		"REPEAT",
		"ANY",
		"NOTANY",
		"AHEAD",
		"BEHIND",

		"RECALL", # XXX not implemented

		"RANGE",

		# TODO START, END, ...

		"SKIP_IGNORE",

		#"NON-TEXT",
		]

	for testname in TESTS:

		print(testname)

		if testname == "ITEM":

			item = ParseqITEM(value="abc")
			SEQ = ParseqSequence(source="abcabc")
			result = item.match(SEQ)
			snap_test_out(result and result.span() == [0,3])
			snap_test_out(ParseqRule_search_test(ParseqITEM, 0, "abcabc", 0,3, "abc"))

			# ITEM will match backward as well...
			SEQ.reverse()
			result = item.match(SEQ)
			snap_out(result)
			snap_test_out(result and result.span() == [0,3])

			
			

		elif testname == "AND":

			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "aaa", -1, -1, "b"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "abc123ab", 0, 3, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "afc123ab", -1, -1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "aaa", 0, 3, "a","a","a"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "aaa", 0, 2, "a","a"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "baa", 1, 3, "a","a"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "bbbbaa", 4, 6, "a","a"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, None, -1, -1, "a"))

			# on linux type ctrl+shift+u then type the code for the character you want to make
			# smiley is 263A
			# NOTE: this test made sense in c, but in python using string means len("☺") will just be 1!
			snap_test_out(ParseqRule_search_test(ParseqAND, 0, "abc☺123", 3, 3 + len("☺"), "☺"))

			snap_test_out(ParseqRule_search_test(ParseqAND, 1, "321cba", 0, 6, "a","b","c","1","2","3"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 1, "321cba555", 0, 6, "a","b","c","1","2","3"))
			snap_test_out(ParseqRule_search_test(ParseqAND, 1, None, -1, -1, "x"))


		elif testname == "OR":

			snap_test_out(ParseqRule_search_test(ParseqOR, 0, "abc123ab", 0, 1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqOR, 0, "abc123ab", 1, 2, "b","c"))
			snap_test_out(ParseqRule_search_test(ParseqOR, 0, "abc123ab", 2, 3, "c"))

			snap_test_out(ParseqRule_search_test(ParseqOR, 0, "abc☺123", 3, 3 + len("☺"), "☺","z"))

			snap_test_out(ParseqRule_search_test(ParseqOR, 1, "abc123ab", 7, 8, "c","a","b"))
			snap_test_out(ParseqRule_search_test(ParseqOR, 1, "abc123ab", 5, 6, "c","3","o"))



			a = ParseqITEM(value="a")
			b = ParseqITEM(value='b')
			c = ParseqITEM(value='c')

			rule_a = ParseqAND(a,b)
			rule_b = ParseqAND(b,c,b)
			grammar = ParseqOR(rule_a, rule_b)

			SEQ = ParseqSequence(source="2acbcbba3")

			snap_test_out(ParseqRule_verify_and_discard_result(grammar.search(SEQ), 3, 6))

			SEQ.reverse()
			SEQ.rewind()

			snap_test_out(ParseqRule_verify_and_discard_result(grammar.search(SEQ), 6, 8))


		elif testname == "NOT":

			snap_test_out(ParseqRule_search_test(ParseqNOT, 0, "aaab", 3, 3, "a"))
			snap_test_out(ParseqRule_search_test(ParseqNOT, 0, "aaab", 0, 0, "b"))
			snap_test_out(ParseqRule_search_test(ParseqNOT, 1, "aaab", 4, 4, "c"))
			snap_test_out(ParseqRule_search_test(ParseqNOT, 1, "abbb", 2, 2, "b","b")) # when going backwards start idx is out of bounds!

			a = ParseqITEM(value='a')
			b = ParseqITEM(value='b')
			c = ParseqITEM(value='c')

			not_abc = ParseqNOT(a,b,c)

			SEQ = ParseqSequence(source="abca*c")

			snap_test_out(ParseqRule_verify_and_discard_result(not_abc.search(SEQ), 1, 1))

			source = 'abcd'
			anything = ParseqNOT() # matches anything without capturing but sequence should still advance!
			SEQ.set(source=source)
			snap_test_out(SEQ.position() == 0)
			for i in range(len(source)):
				result = anything.match(SEQ)
				snap_test_out(result and result.span() == [i,i])
			snap_test_out(SEQ.position() == SEQ.length())

		elif testname == 'REPEAT':

			snap_test_out(ParseqRule_search_test(ParseqREPEAT, 0, "aaab", 0, 3, "a"))
			# default min is 2 for repeat, so must occur twice to match
			snap_test_out(ParseqRule_search_test(ParseqREPEAT, 0, "aabbababa", -1, -1, "a","a"))
			snap_test_out(ParseqRule_search_test(ParseqREPEAT, 0, "aaaaababa", 0, 4, "a","a"))

			a = ParseqITEM(value='a')

			opt_range = [0, 1]

			optional = ParseqREPEAT(a,a, range=opt_range)

			SEQ = ParseqSequence(source="bc123")
			snap_test_out(ParseqRule_verify_and_discard_result(optional.search(SEQ), 0, 0))

			SEQ = ParseqSequence(source="aabc123")
			snap_test_out(ParseqRule_verify_and_discard_result(optional.search(SEQ), 0, 2))

			fixed_range = [3, 3]
			fixed = ParseqREPEAT(a,a, range=fixed_range)
			SEQ = ParseqSequence(source="aaaabc12aaaaaa3")
			snap_test_out(ParseqRule_verify_and_discard_result(fixed.search(SEQ), 8, 14))



			SEQ= ParseqSequence(source='......next..1..2..3..next...abcdefnext...extra')
			n=ParseqITEM(value='n')
			e=ParseqITEM(value='e')
			x=ParseqITEM(value='x')
			t=ParseqITEM(value='t')

			# greedy test:
			# '.*' = ParseqREPEAT(ParseqNOTANY(), min=0)
			result = ParseqREPEAT(ParseqNOTANY(), min=0).match(SEQ)
			snap_test_out(result and result.span() == [0,len(SEQ.source())])

			# '.*next' = REPEAT(REPEAT(NOT('n','e','x','t'), NOTANY(), min=0), 'n','e','x','t', min=0, max=-1)
			SEQ.rewind()
			result = ParseqREPEAT(ParseqREPEAT(ParseqNOT(n,e,x,t), ParseqNOTANY(), min=0), n,e,x,t, min=0, max=-1).match(SEQ)
			snap_test_out(result and result.span() == [0,38])

			# non-greedy test:
			# '.*?' = REPEAT(NOT(NOTANY()), min=0) # would match emptiness... [0:0] -- this is what it does in re on python!
			SEQ.rewind()
			result = ParseqREPEAT(ParseqNOT(ParseqNOTANY()), min=0).match(SEQ)
			snap_test_out(result and result.span() == [0,0])
			# '.*?next' = REPEAT(REPEAT(NOT('n','e','x','t'), NOTANY(), min=0), 'n','e','x','t', min=0, max=1)
			SEQ.rewind()
			result = ParseqREPEAT(ParseqREPEAT(ParseqNOT(n,e,x,t), ParseqNOTANY(), min=0), n,e,x,t, min=0, max=1).match(SEQ)
			snap_test_out(result and result.span() == [0,10])

		elif testname == "ANY":

			snap_test_out(ParseqRule_search_test(ParseqANY, 0, "1", -1, -1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqANY, 0, "a", 0, 1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqANY, 0, "123aaab", 3, 4, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqANY, 0, "123345", -1, -1, "a","b","c"))

			snap_test_out(ParseqRule_search_test(ParseqANY, 1, "a", 0,1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqANY, 1, "123aaab", 2,3, "1","2","3"))
			snap_test_out(ParseqRule_search_test(ParseqANY, 1, "12345", 0,1, "1","a","b"))

			SEQ = ParseqSequence(source="abc123abc456")
			result = ParseqANY('1','123').search(SEQ)
			print(result)
			snap_test_out(result and result.span() == [3,6])
	
		elif testname == "NOTANY":

			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 0, "a", -1, -1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 0, "1", 0, 1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 0, "123aaab", 0, 1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 0, "abcbca", -1, -1, "a","b","c"))

			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 1, "1", 0,1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 1, "1234123ab", 6,7, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqNOTANY, 1, "a12344123", 8,9, "a","b","c"))


		elif testname == 'AHEAD':

			snap_test_out(ParseqRule_search_test(ParseqAHEAD, 0, "abc", 0, 0, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqAHEAD, 0, "123abc", 3, 3, "a","b","c"))

			snap_test_out(ParseqRule_search_test(ParseqAHEAD, 1, "cba", 3, 3, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqAHEAD, 1, "1ba", -1, -1, "a","b","c"))
			snap_test_out(ParseqRule_search_test(ParseqAHEAD, 1, "cba123", 3, 3, "a","b","c"))

		elif testname == 'BEHIND':

			snap_test_out(ParseqRule_search_test(ParseqBEHIND, 0, "cba123", 3, 3, "a","b","c"))

			snap_test_out(ParseqRule_search_test(ParseqBEHIND, 1, "123abc", 3, 3, "a","b","c"))


		elif testname == 'RECALL':
			pass # TODO?

		elif testname == 'RANGE':

			snap_test_out(ParseqRule_search_test(ParseqRANGE, 0, "11ab23", 2,3, "a","c"))
			snap_test_out(ParseqRule_search_test(ParseqRANGE, 0, "1123", -1,-1, "a","c"))

			snap_test_out(ParseqRule_search_test(ParseqRANGE, 1, "1123", 2,3, "1","2"))
			snap_test_out(ParseqRule_search_test(ParseqRANGE, 1, "1123", -1,-1, "a","z"))

		# TODO OPTIONAL and POSITION


		elif testname == 'SKIP_IGNORE':

			SEQ = ParseqSequence(source='   a    b  c   ')
			result = ParseqAND('a','b','c', skip=ParseqREPEAT(ParseqANY(' '),min=1)).match(SEQ)
			snap_out(result)
			snap_test_out(result and result.span() == [3,12])

			SEQ = ParseqSequence(source='   \n\n\t\t   \n\n\t\t   \n  \t')
			idx = 0
			while 1:
				answers = [[3,5],[10,12]]
				result = ParseqAND('\n\n', ignore=ParseqANY(' ','\t','\n')).match(SEQ)
				if not result: break
				snap_out(result, repr(result.value()))
				snap_test_out(answers[idx] == result.span())
				idx += 1
			snap_test_out(idx == 2)


		
		"""
		else if (item == (any)"NON-TEXT"){

			// NOTE: even more complex behaviour could be implemented using custom item classes to check
			// object attributes or that values are within a range... etc...

			int nums[] = {1, 2, 3, 4, 4, 5, 6};
			snap_int array_size = sizeof (nums);
			snap_int num_size = sizeof (int);

			SnapObject one = SnapObject_create(NULL, ParseqITEM, "value", &nums[0], "size", &num_size);
			SnapObject two = SnapObject_create(NULL, ParseqITEM, "value", &nums[1], "size", &num_size);
			SnapObject four = SnapObject_create(NULL, ParseqITEM, "value", &nums[3], "size", &num_size);
			SnapObject six = SnapObject_create(NULL, ParseqITEM, "value", &nums[6], "size", &num_size);

			SNAPLIST(two_fours_items, four, four);
			SnapObject two_fours = SnapObject_create(NULL, ParseqAND, "items", two_fours_items);

			SNAPLIST(two_one_items, two, one);
			SnapObject two_one = SnapObject_create(NULL, ParseqAND, "items", two_one_items);

			SNAPLIST(six_items, six);
			SnapObject six_grammar = SnapObject_create(NULL, ParseqOR, "items", six_items);

			SNAPLIST(grammar_items, two_fours, two_one);
			SnapObject grammar = SnapObject_create(NULL, ParseqOR, "items", grammar_items);

			// TODO init SnapBytesIO and assign the data and size to it...
			SnapObject source = SnapObject_create(NULL, SnapBytesIO, "data", nums, "size", &array_size);
			SnapObject SEQ = SnapObject_create(NULL, ParseqSequence, "source", source, "step", &num_size);

			test_out(ParseqRule_verify_and_discard_result((SnapObject)snap_event(&six_grammar, "SEARCH", "sequence", SEQ), 6 * num_size, 7 * num_size));

			snap_int* POS = (snap_int*)snap_event(&SEQ, "position");
			*POS = 0;

			test_out(ParseqRule_verify_and_discard_result((SnapObject)snap_event(&grammar, "SEARCH", "sequence", SEQ), 3 * num_size, 5 * num_size));

			snap_event(&SEQ, "REVERSE"); snap_event(&SEQ, "REWIND");

			test_out(ParseqRule_verify_and_discard_result((SnapObject)snap_event(&two_one, "SEARCH", "sequence", SEQ), 2 * num_size, 0));

			snap_event(&six_grammar, "DELETE");
			snap_event(&SEQ, "DELETE");
			snap_event(&grammar, "DELETE"); // decrefs and deletes all subrules as well

		}
		"""

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

