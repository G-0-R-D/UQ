
#from snap.lib.parsing.parseq import ParseqRules as ParseqRulesModule

def build(ENV):

	#ENV.__import_and_build__('snap.lib.core.parsing.parseq.ParseqRules')

	PARSEQ_MATCH_FAIL = ENV.PARSEQ_MATCH_FAIL
	#PARSEQ_TYPE_LAYER = ENV.PARSEQ_TYPE_LAYER

	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error
	snap_out = ENV.snap_out

	ParseqITEM = ENV.ParseqITEM

	ParseqRule = ENV.ParseqRule
	ParseqRule___return_results__ = ENV.ParseqRule___return_results__
	ParseqRule___search__ = ENV.ParseqRule___search__
	ParseqResult = ENV.ParseqResult

	ParseqRule_search = ENV.ParseqRule_search
	snap_binary_search = ENV.snap_binary_search

	ParseqOR = ENV.ParseqOR
	ParseqSequence = ENV.ParseqSequence

	class ParseqLayerITEM(ParseqITEM):

		def __match__(self, SEQUENCE):

			START = SEQUENCE.position()

			name = self.name()

			SEQ_ITEM = SEQUENCE.__advance__() # sequence must be of ParseqResults
			if name and isinstance(SEQ_ITEM, ParseqResult):
				try:
					if SEQ_ITEM.rule().name() == name:
						if name == 'name':
							''#out('name', START, SEQUENCE.position(), SEQ_ITEM.value())
						# success
						#out('success', START, SEQUENCE.position())
						SEQUENCE.MATCH_START = START
						SEQUENCE.MATCH_END = SEQUENCE.position()
						# NOTE: SEQ_ITEM is ParseqResult from sublayer, and self.capture() is False, so the subresult will be returned...
						subs = ParseqRule___return_results__(self, SEQUENCE, [SEQ_ITEM])
						if name == 'name':
							''#out('name subs returned', subs)
						return subs
				except Exception as e:
					print(repr(e))
					pass

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return

		# TODO __compare__() which will compare self name against other name... and then it can be added to ANY()...

		def capture(self):
			return False

		def set(self, **kwargs):
			for k,v in kwargs.items():
				if k == 'item' or k == 'items':
					snap_warning(k, 'blocked')

				elif k == 'value':
					raise TypeError('value cannot be set', self)

				else:
					ParseqRule.set(self, **{k:v})



		def __compare__(self, ITEM):

			item_name = None
			self_name = self.name()
			if isinstance(ITEM, ParseqResult):
				try:
					item_name = ITEM.rule().name()
				except:
					pass
			elif isinstance(ITEM, ParseqLayerITEM):
				item_name = ITEM.name()
			else:
				if id(self) < id(ITEM): return -1
				elif id(self) > id(ITEM): return 1
				return 0

			if not item_name:
				if self_name:
					return 1
				return 0
			if not self_name:
				return 0 # not self or item name at this point

			if self_name < item_name: return -1
			elif self_name > item_name: return 1
			else: return 0
			
		def value(self):
			return None

		def __init__(self, *args, **kwargs):
			ParseqITEM.__init__(self, **kwargs)
			# TODO accepts a result name to identify?  if result name is the same, then it is a match
			# so all this has is a name and a match that matches a result from the source sequence and checks against own name

			assert not args, 'no args allowed; use name to identify (matches against subresult name)'

	ENV.ParseqLayerITEM = ParseqLayerITEM








	class ParseqLayer(ParseqOR, ParseqSequence):
		# layering done in separate passes, for better efficiency, but slightly more overhead

		#_type_code_ = PARSEQ_TYPE_LAYER

		def __advance__(self):

			# NOTE: this will only be used if self is used as a sequence... otherwise the match calls would bypass this and use self as an OR rule on the sublayer...

			# always will be the results for the subsequence/source...
			# parse from the start, bookmark every so often (mark first of every 100 results?)

			# TODO we need bookmarks, and loaded page with offset, then we call self.search_with_result() against self.source()?
			# if self.position() is in loaded range, then return it, otherwise search_with_result self against source until results are in range
			# so we don't need to know length! we just try matching when out of range until it fails...?

			# TODO how to handle non-capturing rules?  they result in double-occupied cache slots...
			#	-- can check if result span is 0...

			step = self.step()
			assert abs(step) == 1, 'invalid step {} != 1'.format(step)
			#source = self.source()
			#length = self.length() # XXX length can't be knowable until entire sequence is parsed...
			#if not source or length < 1 or step == 0:
			#	return

			position = self.position()
			if position < 0:
				position = 0
				self.set(position=position)
			#if position > length: position = length

			start_pos = position
			end_pos = position + step
			if end_pos < 0:
				return None

			select_idx = start_pos if step > 0 else start_pos + step

			position = subposition = 0

			offset = self._offset_ # offset is the start of the cache (so it should map to self.position() 1:1)
			cache = self._cache_
			cache_size = max(1,1000)

			if not cache or len(cache) != cache_size:
				if not cache:
					self._cache_ = cache = [None] * cache_size
				elif len(cache) < cache_size:
					self._cache_ = cache = cache + [None] * (cache_size - len(cache))
				elif len(cache) > cache_size:
					self._cache_ = cache = cache[:cache_size]

			local_pos = select_idx - offset
			if local_pos > -1 and local_pos < cache_size and cache[local_pos] != None:
				# if in range and loaded return from cache
				self.set(position=end_pos)
				return cache[local_pos]

			bookmarks = self._bookmarks_ # bookmarks are tuples of (local,sublayer) positional coordinates
			bookmark_frequency = max(1,100) # TODO bookmark frequency, for now use 100?

			# find bookmark before position, and if there is one we start parsing from there
			bookmark_before = (select_idx // bookmark_frequency) - 1 # - 1 because we don't record 0, it is implicitly the first bookmark...
			if bookmarks and bookmark_before > -1:
				if bookmark_before < len(bookmarks):
					position,subposition = bookmarks[bookmark_before]
				else:
					# last bookmark is closest we can get
					position,subposition = bookmarks[-1]

			# see if there is a usable result for a closer pseudo-bookmark in the cache (before shift dumps anything)
			# this should be okay because results can't be obtained without bookmarks as well... the bookmark should already exist if this is valid...
			if offset <= select_idx and offset + cache_size > select_idx:
				# cache is viably in range to have an entry that could be used to get closer to the target position
				#idx = cache_size - (select_idx - offset) - 1 # ignore elements listed after end_pos

				# TODO bookmark should have already been set, but we could check where the next bookmark should be...
				idx = select_idx
				while idx >= offset:
					if cache[idx-offset]:
						position = idx+1
						if position > select_idx:
							snap_error('warning: position > select_idx', position, select_idx)
						subposition = cache[idx-offset].end()
						if cache[idx-offset].start() == cache[idx-offset].end():
							#snap_warning('nonadvancing')
							subposition += 1
						#snap_out("advance to cache", position, subposition, cache[idx-offset])
						#if bookmarks:
						#	print('last bookmark on advance', bookmarks[-1])
						break
					idx -= 1

			# if end_pos is outside cache range, then shift the cache so end_pos is now in the middle
			# (unless that would be out of bounds, then clamp to the edge)
			if select_idx < offset or select_idx >= offset + cache_size:
				# margin = make sure cache does not exceed boundaries (we only know start boundary though...)

				shift = select_idx - (offset + (cache_size // 2))
				shift *= -1

				# TODO this is wrong apparently, FIXME
				# clamp (don't know length so can't clamp to end)
				#if offset + shift < 0:
				#	shift -= offset + shift

				# if offset + cache_size + shift > length:
					# shift -= offset + cache_size + shift

				shift_step = abs(shift)
				if shift_step < cache_size:

					# shift is in-bounds of cache, so we need to move them individually

					if shift < 0:

						idx = 0
						while idx < cache_size:
							next = idx + shift_step
							if next < cache_size:
								cache[idx] = cache[next]
							else:
								cache[idx] = None						
							idx += 1

					elif shift > 0:

						idx = cache_size - 1
						while idx > -1:
							next = idx - shift_step
							if next > -1:
								cache[idx] = cache[next]
							else:
								cache[idx] = None
							idx -= 1

					# else shift == 0, no action (might have been clamped)

				else:
					# the shift is larger than the cache, so nothing will remain (just flush it)
					cache[:] = [None] * cache_size

				offset += shift * -1
				self._offset_ = offset

			# then start parsing from position/subposition until we reach end_pos
			# (NOTE: we might be getting results before start of cache and they would need to be dumped!)
			sequence = self.sequence()
			if not sequence:
				return None

			self.set(position=position) # not really used here, but probably good practice
			sequence.set(position=subposition)

			#out('started', [position, subposition], 'target', [start_pos,end_pos], select_idx)#, self.source().length())
			#if bookmarks:
			#	print('last bookmark', len(bookmarks), bookmarks[-1])

			while position <= select_idx:

				subresults = ParseqRule___search__(self, sequence, True, True)
				if not subresults:
					break

				#out('match', [sequence.MATCH_START,sequence.MATCH_END], 'pos', position, 'select', select_idx, subresults)

				#out('sequence', sequence.MATCH_START, sequence.MATCH_END, sequence.position(), start_pos, end_pos)
				#out('subresults', sequence.MATCH_END == PARSEQ_MATCH_FAIL, len(subresults), position, select_idx, subresults)

				# if there are multiple subresults, we have to force a cache miss
				# to reload subresults from proper start position...
				# also using this for when result is non-advancing, since it prevents
				# infinite loop at the end (in the easiest way I can think of to do it...) FIXME?
				# TODO why does start_pos keep advancing if non-advancing result is cached?

				# NOTE: we can't cache multi subresults because they always need to begin before the first one!
				# if we cache them the cache may attempt to resume in the middle, so we force a cache miss if there
				# is more than one subresult
				# ALSO: if result is non-advancing then it will be cached but the non-advance status is checked when resuming
				# and next position is forced, otherwise it will spin out in a loop!  this way we can still use the cache
				# in the situtation, so we don't have to force a cache miss which could be less efficient...

				use_cache = len(subresults) < 2 #and sequence.MATCH_START != sequence.MATCH_END

				result_idx = 0
				while result_idx < len(subresults):

					result = subresults[result_idx]

					check_position = position + result_idx

					#out('check position', check_position, 'subposition', sequence.position(), result.span())
					#out(len(subresults), result)

					if check_position < offset or check_position >= offset + cache_size:
						pass # dump result out of cache range
					else:
						if use_cache:
							#warning("use cache", check_position, result, cache[check_position-offset-3:check_position-offset])
							cache[check_position-offset] = result
						else:
							cache[check_position-offset] = None # force cache miss (forces load from last start position)

					if check_position % bookmark_frequency == 0 and check_position > 0:
						
						# - 1 because we don't record first bookmark (it is always 0)
						idx = (check_position // bookmark_frequency) - 1

						# NOTE: use sequence.MATCH_START because we need to know where the match started!
						# the result may only contain a subresult that was set to capturing, but to capture
						# it we will need to go back to the start of the match!
						# NOTE: if multiple subresults are returned then this will force entry at start position
						# for the results (and if len(subresults) > bookmark_frequency, that can result in the same
						# start entered multiple times in bookmarks, but that's okay)

						bm = [position, sequence.MATCH_START]

						if idx < len(bookmarks):
							if bookmarks[idx] != bm:
								snap_warning("\n\texisting bookmark differs", [position, idx], select_idx, offset, bookmarks[idx], bm, result, result.span())
							#bookmarks[idx] = bm # shouldn't need to do this
						else:
							if bookmarks and len(bookmarks) - idx != 0:
								snap_warning("\n\tincorrect bookmark append?", idx, len(bookmarks))
							bookmarks.append(bm)

					if check_position == select_idx:
						#out('reached end', start_pos, check_position, 'select_idx', select_idx, 'end', end_pos, result, subposition)
						self.set(position=end_pos)
						if cache[select_idx - offset] and cache[select_idx - offset] != result:
							snap_warning('returned incorrect result?', select_idx, result, cache[select_idx - offset])
						return result

					result_idx += 1

				position += result_idx

			# clamps to last valid position (not start_pos)
			self.set(position=position)
			return None

		def __match__(self, SEQUENCE): 

			sequence = self.sequence()
			if sequence:
				return ParseqOR.__match__(self, sequence)

			SEQUENCE.MATCH_END = PARSEQ_MATCH_FAIL
			return None


		def __getitem__(self, KEY):
			#out(KEY, dir(KEY))
			
			if isinstance(KEY, (slice,int)):
				if isinstance(KEY, slice):
					start = KEY.start
					end = KEY.stop
					step = KEY.step or 1
				else:
					start = KEY
					end = KEY + 1
					step = 1

				begin = min(start,end)
				finish = max(start,end)

				original_pos = self.position()
				original_step = self.step()

				self.set(position=begin, step=abs(step))

				subs = [self.__advance__() for i in range(finish-begin)]

				#out('subs', subs, start, end, step)
				
				self.set(position=original_pos, step=original_step)

				if not subs:
					return None
				elif len(subs) == 1:
					return subs[0]
				else:
					if step != 1:
						return subs[::step]
					return subs

			elif isinstance(KEY, (list, tuple)):
				if all([isinstance(K,slice) for K in KEY]):
					return [self.__getitem__(K) for K in KEY]
				raise NotImplementedError(KEY)
			else:
				raise KeyError(KEY)

		# XXX TODO update this to new api
		def __incoming__(self, SOURCE, EVENT, *args, **kwargs):
			#out(EVENT, args, kwargs.keys())
			if EVENT == 'CHANGED':# and SOURCE == self.sublayer():
				#out('got sublayer changed')
				self.clear()
				#emit(self, "CHANGED", *args, **kwargs)
				parent = self.parent()
				if parent:
					parent.__incoming__(self, "CHANGED", **kwargs) # TODO parent.changed(self)?  or update()? refresh()?




		#def item(self, rule, span, subs): # XXX deprecated, results are locally cached
		#	if not self._item_:
		#		self._item_ = ParseqResult()
		#	#self._item_.set(value=value)
		#	self._item_.set(rule=rule, sequence=self.source(), span=span, subs=subs)
		#	return self._item_

		def parent(self):
			return self._parent_

		def sublayer(self):
			return self._sublayer_

		def sequence(self):
			#out('get sequence()', self.sublayer(), self.source(), self.sublayer() or self.source())
			return self.sublayer() or self.source()


		def set(self, **kwargs):
			for k,v in kwargs.items():
				if k == 'sublayer':
					if self._sublayer_:
						if self._sublayer_ == v:
							continue
						self._sublayer_.clear()
						self._sublayer_._parent_ = None
						#self._sublayer_.ignore(self)
						self._sublayer_ = None
					if v:
						assert isinstance(v, ParseqLayer), 'sublayer must be ParseqLayer instance'
					self._sublayer_ = v
					if v:
						#warning('try listen', self._sublayer_)
						#self._sublayer_.listen(self)
						#emit(self._sublayer_, "CHANGED")
						self._sublayer_.__incoming__(None, "CHANGED")
					else:
						parent = self.parent()
						if parent:
							parent.__incoming__(None, "CHANGED")

				elif k == 'sequence' or k == 'source':
					snap_warning('this is not how this is intended to function, pass the', k, 'in with the search using toplevel layer...')
				elif k in ('position', 'step'):
					ParseqSequence.set(self, **{k:v})
				else:
					ParseqOR.set(self, **{k:v})



		def _prep_for_search(self, SEQUENCE):
			# assigns sequence to source if it is changed, then emits changed to clear cached info in all parent layers
			#stack = []
			sublayer = self
			while 1:
				next_sublayer = sublayer.sublayer()
				#out("sublayer,next", sublayer, next_sublayer, sublayer==next_sublayer)
				if next_sublayer:
					#stack.append(sublayer)
					sublayer = next_sublayer
				else:
					if sublayer._source_ != SEQUENCE:
						sublayer._source_ = SEQUENCE
						# TODO just call sublayer.__incoming__(None, "CHANGED", sequence=SEQUENCE)
						sublayer.clear()
						# TODO use __incoming__ directly, assign parent on sublayer when sublayer is assigned, error if already has different parent
						sublayer.__incoming__(None, "CHANGED", sequence=SEQUENCE)
						#out("changed", self, sublayer)
						#raise NotImplementedError('avoid emit and listeners; use parent/child references')
						#emit(sublayer, "CHANGED", sequence=SEQUENCE) # and the emit will be forwarded up the chain...
					break

			#out('prepped', self.source(), self.sublayer(), self.sequence())
			
			

		def clear(self, *args, **kwargs):
			self._offset_ = 0
			del self._cache_[:]
			del self._bookmarks_[:] # invalid when source sequence changes


		# NOTE: this is user API
		def match(self, SEQUENCE):
			# user api: attempt to match at current position of sequence (already set)
			# if non-capturing, wrap in dummy result and returns that (must return result on success)
			self._prep_for_search(SEQUENCE)
			return ParseqRule_search(self, self.sequence(), False, False)

		def match_with_result(self, SEQUENCE):
			# same as MATCH but if non-capturing result is returned it will try again at the next position until match fails or capturing result is returned
			self._prep_for_search(SEQUENCE)
			return ParseqRule_search(self, self.sequence(), True, False)

		def find(self, SEQUENCE):
			# user api: find first match, skipping over all non-matches (iterates "MATCH" until success)
			self._prep_for_search(SEQUENCE)
			return ParseqRule_search(self, self.sequence(), False, True)

		def search(self, SEQUENCE):
			return self.find(SEQUENCE)

		def find_with_result(self, SEQUENCE):
			# similar to MATCH_WITH_RESULT; will keep searching until a result that is capturing is found
			self._prep_for_search(SEQUENCE)
			return ParseqRule_search(self, self.sequence(), True, True)
			#out('start', self, args, kwargs) # TODO set sequence to self.sequence()?

		def search_with_result(self, SEQUENCE):
			return self.find_with_result(SEQUENCE)


		def capture(self):
			return False

		def name(self):
			return None

		def itemize(self, **SETTINGS):
			# return dict of all named (and capturing) rules as LayerITEM, so owning layer can connect in
			# (LayerITEM matches based on names, so rule must be named and be the one returned (toplevel with name that is capturing))

			ALL = SETTINGS.get('all', False) # force all named to be included, whether they will be in the results or not

			items = {}
			SEEN = []
			QUEUE = [self]
			while QUEUE:

				rule = QUEUE.pop(0)

				idx = snap_binary_search(SEEN, id(rule), lambda x: id(x), True)
				if idx < len(SEEN) and id(SEEN[idx]) == id(rule):
					continue
				SEEN.insert(idx, rule)

				name = rule.name()
				capturing = rule.capture()

				# TODO update this to consider simplify and capture_all?

				if name and (ALL or (capturing is None or capturing)): # if capturing is None then the fact it is named makes it capture
					# named and capturing, so this will be what is in the results for the layer...
					assert name not in items, 'duplicate name: {}'.format(name)
					items[name] = ParseqLayerITEM(name=name)
					continue

				if (ALL or not rule.suppress()):
					# only if not capturing and not suppressed, we check children
					QUEUE = QUEUE + rule.items()

			return items


		def length(self):
			#raise Exception()
			last_known_pos = 0
			if self._bookmarks_:
				last_known_pos = self._bookmarks_[-1][0]
			if self._cache_:
				idx = len(self._cache_)-1
				while idx > -1:
					if self._cache_[idx] and self._cache_[idx].end() > last_known_pos:
						last_known_pos = self._cache_[idx].end()
						break
					idx -= 1

			original_position = self.position()
			original_step = self.step()
			self.set(position=original_position, step=abs(original_step))
			while self.__advance__():
				#print('advance', self.position())
				pass
			length = self.position()
			self.set(position=original_position, step=original_step)
			#print('return length', length)
			return length

		def __init__(self, *args, **kwargs):
			self._sublayer_ = None # XXX FIXME?  catch sublayer from args and then set locally?
			ParseqOR.__init__(self, *args, **kwargs)
			ParseqSequence.__init__(self, **kwargs)

			self._parent_ = None
			self._bookmarks_ = [] # {self.position():sublayer.position()} mark starting positions every 100 or so?  (parsing has to start at the beginning and move forward)
			self._cache_ = []
			self._offset_ = 0 # start of cache (in self.position() coordinates)

			# assign sequence as source, use advance?

			# set items triggers reconnect, connect LayerITEM by name?

			# put the layers together, assigning sublayer, sequence gets assigned to bottom layer? XXX pass sequence into matching call, it gets set to sublayer, and then we return the toplevel results (which can then return the source from the sequence?)

			self.set(**{k:v for k,v in kwargs.items() if k in ('sublayer',)})



	ENV.ParseqLayer = ParseqLayer


def main(ENV):

	if 1:
		SEQ = ENV.ParseqSequence(source="abc1x23def4x56gxhi789")
		layer1 = ENV.ParseqLayer(ENV.ParseqAND('x', name='x'))
		layer2 = ENV.ParseqLayer(ENV.ParseqLayerITEM(name='x'), sublayer=layer1)
		idx = 0
		while idx < 3:
			answer = [[4,5],[11,12],[15,16]][idx]
			idx += 1
			result = layer2.search_with_result(SEQ)
			if not result:
				break
			ENV.snap_test_out(result.span() == answer)
			ENV.snap_out(result)


	SEQ = ENV.ParseqSequence(source='once upon a time the big brown fox jumped over the lazy fox at the mall as the day dawned.')
	layer1 = ENV.ParseqLayer(ENV.ParseqAND('the', name='the'))
	layer2 = ENV.ParseqLayer(ENV.ParseqLayerITEM(name='the'), sublayer=layer1)

	#print(layer2.search_with_result(SEQ))

	#results = [layer1.search_with_result(SEQ) for i in range((SEQ.source().count('the')))]
	#print(results)

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

