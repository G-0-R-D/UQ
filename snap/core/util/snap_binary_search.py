
def build(ENV):

	"""
	def __snap_binary_search(DATA, ITEM_P, ITEM_SIZE, L, R,
		COMPARE_CALLBACK, RUN_TO_END, EXTRA):

		\"""
		NOTE: ITEM_P needs to be the same type of pointer as in the array
		so an int would be &int
		a SnapObject in a SnapList needs to be &SnapObject
			-- the SnapList_sorted_binary_search api will pass the address of the item (so that it is inuitive from the user perspective, where item is the item they are searching for)

		this is so the same compare can be used for searching and sorting
		\"""

		if not DATA:
			if RUN_TO_END:
				return 0
			return -1

		cmp = center = 0

		while (R >= L):
			
			#center = L + (R - L) // 2
			center = (L + R) // 2

			cmp = COMPARE_CALLBACK(DATA[center], ITEM_P, EXTRA)

			if (cmp > 0):
				R = center - 1

			elif (cmp < 0):
				L = center + 1

			else:
				if RUN_TO_END:
					R = center - 1 # found a match, but that might not be only one?
					continue
				return center

		if RUN_TO_END:
			return L # if run to end this is next index (closest miss / best insertion point)
		return -1
	"""

	def snap_binary_search_compare_default(LIST_ITEM, COMPARE_ITEM, extra_data):

		# the comparison logic is based on a left to right read
		# ie. as if it was writting LIST_ITEM <> COMPARE_ITEM
		# so LIST_ITEM < COMPARE_ITEM is -1 (LIST_ITEM is 'to the left' of COMPARE_ITEM), etc...
		# but we compare with COMPARE_ITEM first so the COMPARE_ITEM api is used for the comparison call... (__lt__, __gt__)
		
		if COMPARE_ITEM < LIST_ITEM: return 1
		elif COMPARE_ITEM > LIST_ITEM: return -1
		return 0
	ENV.snap_binary_search_compare_default = snap_binary_search_compare_default

	def snap_binary_search_compare_address(LIST_ITEM, COMPARE_ITEM_id, extra_data):
		
		LIST_ITEM_id = id(LIST_ITEM)
		if COMPARE_ITEM_id < LIST_ITEM_id: return 1
		elif COMPARE_ITEM_id > LIST_ITEM_id: return -1
		return 0
	ENV.snap_binary_search_compare_address = snap_binary_search_compare_address
		

	def snap_binary_search_core(LIST, ITEM, L=None, R=None, compare=None, key=None, run_to_end=False, allow_duplicates=False, extra_data=None):

		if L is None:
			L = 0

		if LIST:

			if not compare:
				compare = snap_binary_search_compare_default

			if not key:
				key = lambda x: x # as is

			if R is None:
				R = len(LIST)-1

			while R >= L:
				C = (L + R) // 2

				list_item = key(LIST[C])

				cmp = compare(list_item, ITEM, extra_data)

				if cmp > 0:
					R = C - 1
				elif cmp < 0:
					L = C + 1
				else:
					if allow_duplicates and run_to_end:
						R = C - 1 # found a match, but might not be only one?  this will find the start of the segment...
						continue
					return C

		if run_to_end:
			return L
		return -1

		# access via key, compare with COMPARE_CALLBACK (default to just comparing the items normally)
	ENV.snap_binary_search_core = snap_binary_search_core


	def snap_binary_search(LIST, ITEM, key=None, run_to_end=False):
		return snap_binary_search_core(LIST, ITEM, key=key, run_to_end=run_to_end, allow_duplicates=False)
	ENV.snap_binary_search = snap_binary_search

		# TODO key isn't the same as compare(a,b) in c...  but __compare__(self, other) would be called on item, so item could be wrapped in a dummy to handle the comparisons...

	"""
		l = 0

		if LIST:

			if not key: key = lambda x: x

			r = len(LIST)-1
			while r >= l:
				c = (l + r) // 2
				list_key = key(LIST[c])
				#if list_key > ITEM: r = c - 1 # TODO switch this to be ITEM first, so it's comparison is used...
				#elif list_key < ITEM: l = c + 1

				if ITEM < list_key: r = c - 1
				elif ITEM > list_key: l = c + 1
				else:
					if not run_to_end:
						return c
					r = c - 1

		if run_to_end:
			# run to end means 'find the insertion point'
			# which will be the first (if duplicates) item if present, or the next item if not
			return l
		return -1
	"""

	def snap_binary_insert(LIST, ITEM, key=None):
		idx = snap_binary_search(LIST, ITEM, key=key, run_to_end=True) # ?
		#if not allow_duplicate and idx < len(LIST) and : TODO check if already there by searching to end and seeing if LIST[idx] is == ITEM (with key!)
		#	''
		LIST.insert(idx, ITEM)
		return idx # LIST[idx] == ITEM
	ENV.snap_binary_insert = snap_binary_insert

