
# these are algorithms for lists of items that are used a lot, so here is a generic implementation

# uses id() to disambiguate

def build(ENV):

	def snap_list_set_items(ORIGINAL_ITEMS, NEW_ITEMS, **SETTINGS):

		if not NEW_ITEMS:
			return []

		if ORIGINAL_ITEMS is NEW_ITEMS:
			return ORIGINAL_ITEMS #NEW_ITEMS[:]

		allow_dups = SETTINGS.get('allow_dups', False)
		allow_nulls = SETTINGS.get('allow_nulls', False)

		if allow_dups and allow_nulls:
			return NEW_ITEMS[:]

		elif allow_dups:
			# no nulls
			return [n for n in NEW_ITEMS if n is not None]

		elif allow_nulls:
			# no dups
			seen = set()
			seen_add = seen.add
			def check(i):
				_id = id(i)
				if _id in seen:
					return False
				seen_add(_id)
				return True
			return [n for n in NEW_ITEMS if check(n)]
		else:
			# no dups and no nulls
			seen = set()
			seen_add = seen.add
			def check(i):
				if i is None:
					return False
				_id = id(i)
				if _id in seen:
					return False
				seen_add(_id)
				return True
			return [n for n in NEW_ITEMS if check(n)]

		raise Exception('oops')
	ENV.snap_list_set_items = snap_list_set_items

	def snap_list_insert_items(ORIGINAL_ITEMS, INDEX, INSERT_ITEMS, **SETTINGS):

		# index > len will be at end
		# index < 0 will be from end and < negative len() will be at start / 0

		if not INSERT_ITEMS:
			return ORIGINAL_ITEMS or []

		if not ORIGINAL_ITEMS:
			return INSERT_ITEMS or []

		if INDEX is None:
			INDEX = 0

		if INDEX < 0:
			if abs(INDEX) > len(ORIGINAL_ITEMS):
				INDEX = 0
		elif INDEX >= 0:
			if INDEX > len(ORIGINAL_ITEMS):
				INDEX = len(ORIGINAL_ITEMS)

		allow_dups = SETTINGS.get('allow_dups', False)
		allow_nulls = SETTINGS.get('allow_nulls', False)

		# TODO test make sure negative indices work correctly...
		concat = ORIGINAL_ITEMS[:INDEX] + INSERT_ITEMS + ORIGINAL_ITEMS[INDEX:]

		if allow_dups and allow_nulls:
			return concat
		elif allow_dups:
			# no nulls
			return [n for n in concat if n is not None]
		elif allow_nulls:
			# no dups
			seen = set()
			seen_add = seen.add
			def check(i):
				_id = id(i)
				if _id in seen:
					return False
				seen_add(_id)
				return True
			return [n for n in concat if check(n)]
		else:
			# no dups or nulls
			seen = set()
			seen_add = seen.add
			def check(i):
				if i is None:
					return False
				_id = id(i)
				if _id in seen:
					return False
				seen_add(_id)
				return True
			return [n for n in concat if check(n)]

		raise Exception('oops')
	ENV.snap_list_insert_items = snap_list_insert_items

	def snap_list_add_items(ORIGINAL_ITEMS, INSERT_ITEMS, **SETTINGS):
		return snap_list_insert(ORIGINAL_ITEMS, len(ORIGINAL_ITEMS) if ORIGINAL_ITEMS else 0, INSERT_ITEMS, **SETTINGS)
	ENV.snap_list_add_items = snap_list_add_items

	def snap_list_remove_items(ORIGINAL_ITEMS, REMOVE_ITEMS, **SETTINGS):
		
		if not REMOVE_ITEMS:
			return ORIGINAL_ITEMS or []

		if not ORIGINAL_ITEMS:
			return []

		if id(ORIGINAL_ITEMS) == id(REMOVE_ITEMS):
			return [] # this would mean all are removed

		allow_dups = SETTINGS.get('allow_dups', False)
		allow_nulls = SETTINGS.get('allow_nulls', False)

		remove = set([id(n) for n in REMOVE_ITEMS])

		if allow_dups and allow_nulls:
			return [n for n in ORIGINAL_ITEMS if id(n) not in remove]
		elif allow_dups:
			# no nulls
			return [n for n in ORIGINAL_ITEMS if n is not None and id(n) not in remove]
		elif allow_nulls:
			# no dups
			seen = remove
			seen_add = seen.add
			def check(i):
				_id = id(i)
				if _id in seen:
					return False
				seen_add(_id)
				return True
			return [n for n in ORIGINAL_ITEMS if check(n)]
		else:
			# no dups or nulls
			seen = remove
			seen_add = seen.add
			def check(i):
				if i is None:
					return False
				_id = id(i)
				if _id in seen:
					return False
				seen_add(_id)
				return True
			return [n for n in ORIGINAL_ITEMS if check(n)]

		raise Exception('oops')
	ENV.snap_list_remove_items = snap_list_remove_items

	def snap_list_pop_item(LIST, index=None, **SETTINGS):#allow_dups=False, allow_nulls=False):
		# XXX TODO this needs reconsideration, as it's clumsier than LIST.pop(x)!
		if index is None:
			try:
				item = SETTINGS['item']
			except:
				raise ValueError('nothing defined to pop')

			index = LIST.index(item)

		return LIST.pop(index)
	ENV.snap_list_pop_item = snap_list_pop_item
			
			

	#def SnapObjectList___setitem__(self):
	#	raise NotImplementedError()

	#def SnapObjectList___getitem__(self, LIST, ITEM, allow_dups=False, allow_nulls=False):
	#	raise NotImplementedError()


	def snap_list_rotate(LIST, COUNT):
		"""rotate a SnapList in place, using just one shuffle
		negative is left, positive is right

		NOTE: you can rotate a sub-section of a longer SnapList using something like this:

			SnapList list = SnapNode_create(SnapList_event, "1", "2", "3", "4", "5");

			SNAPLIST(fake);
			fake->length = 3;
			fake->data = list->data + 1;
			// fake == {"2", "3", "4"}

			SnapList_rotate(&fake, -2);

			// list == {"1", "4", "2", "3", "5"}


		think of this as start is always 0, then we figure out the 'stride' or the distance positively from 0 we want to step through

		NOTE: if list is evenly divisible by stride then it will get stuck in a 'channel' without reaching some values, so the index has to be checked and incremented deliberately when that happens...

		"""

		length = len(LIST)
		if length < 2:
			return None # Nothing will happen

		COUNT *= -1 # makes it so negative moves to the 'left'

		if COUNT < 0:
			COUNT = length - ((COUNT * -1) % length)

		else:
			COUNT %= length

		if COUNT == 0: # after modulo count can be 0 (divides evenly and ends up where it started; a no-op)
			return None

		CHANNEL = 0
		idx = 0 # always start at 0
		next_idx = None
		i = 1 # skip the last one because we assign it manually after...

		tmp = LIST[idx] # if all goes well tmp will only be used once...  at worst: once per channel
		while i < length:
			i += 1

			next_idx = (idx + COUNT) % length

			#snap_out("[%d] -> [%d]", next_idx, idx);

			if next_idx == CHANNEL:
				# back to where we started prematurely (evenly divisible)... fudge one forward and continue on...
				#snap_out("collision %d", CHANNEL);
				LIST[idx] = tmp
				next_idx = CHANNEL
				CHANNEL += 1
				tmp = LIST[next_idx]

			else:
				LIST[idx] = LIST[next_idx]

			idx = next_idx

		LIST[idx] = tmp

		return LIST


	ENV.snap_list_rotate = snap_list_rotate

	def snap_list_remove_duplicates(LIST):
		'sort'
		'scan through comparing current to previous, contracting if they are the same'
		# TODO maintain original order?  make new sorted list as tuple pairs of the value and the original index?


