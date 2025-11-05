

def binary_search(LIST, ITEM):
	# run to end version (nearest)
	#return snap_binary_search_core(LONG_LIST_OF_IDX, SHORT_IDX, compare=lambda x,y,p: x-y, run_to_end=True)
	L = 0
	R = len(LIST)-1

	while R >= L:
		C = (L + R) // 2

		list_item = LIST[C]

		compare = list_item - ITEM
		if compare > 0:
			R = C - 1
		elif compare < 0:
			L = C + 1
		else:
			R = C - 1
			continue

	return L

def similarity(A,B, **SETTINGS):
	"""returns a normalized value indicating the similarity of the two elements (how close they are)
	0.0 means completely different (no items in common) and 1.0 means exactly the same (all items identical)
	if both elements are not iterable (no length) then they are compared directly with eachother (A == B)
	"""

	try:
		len_A = len(A)
	except:
		len_A = None

	try:
		len_B = len(B)
	except:
		len_B = None

	if len_A is None or len_B is None:
		if len_A or len_B:
			return 0.0 # miss (can't compare; one is iterable and the other is not - like a str and int)
		else:
			# both are not iterables so compare them directly (might be two ints for example...)
			#return 0.0 if A != B else 1.0
			return float(A == B)

	LONG = A if len_A > len_B else B
	SHORT = B if len_A > len_B else A

	CASE_SENSITIVE = SETTINGS.get('case_sensitive', False)
	if 'ignore_case' in SETTINGS:
		CASE_SENSITIVE = not SETTINGS['ignore_case']

		if not CASE_SENSITIVE:
			if isinstance(LONG, str):
				LONG = LONG.upper()
			if isinstance(SHORT, str):
				SHORT = SHORT.upper()

	len_LONG = len(LONG)
	len_SHORT = len(SHORT)

	lookup = {}
	idx = 0
	while idx < len_SHORT:
		symbol = SHORT[idx]
		lookup[symbol] = lookup.get(symbol, []) + [idx]
		idx += 1

	FACTOR = 1.0 / len_LONG # so we don't have to divide by length each time; more efficient

	SUM = 0.0

	idx = 0
	while idx < len_LONG:

		symbol = LONG[idx]

		L = lookup.get(symbol)
		if L:
			# if L > 0 then there is always a 'closest'!
			found = binary_search(L, idx)
			try:
				closest = L[found]
			except:
				closest = L[-1]
			SUM += abs(idx-closest) * FACTOR
		else:
			# symbol not used, penalty of full length miss (1.0)
			SUM += 1.0 # miss by full length or 100%

		idx += 1

	return 1 - (SUM * FACTOR) # normalized (and inverted so 0.0 means no match and 1.0 means exact match)

# TODO: I think this is actually the more relevant algorithm because it would give the high score for having characters in common, no matter where they are located...
def string_distance(A, B, **SETTINGS):

	LONG = A if len(A) > len(B) else B
	SHORT = B if len(A) > len(B) else A

	if not SETTINGS.get('case_sensitive', False):
		LONG = LONG.upper()
		SHORT = SHORT.upper()

	width = 1

	results = []

	viable_indices = range(len(LONG)) # start with all as viable, this becomes the previous indices at each pass
	while 1:

		# take all possible slices (viable indices will reduce upon each iteration)
		candidates = [(idx, LONG[idx:idx+width]) for idx in viable_indices]
		#print('candidates', width, candidates)
		# then remove all the slices that have no overlap with the other string
		# NOTE: we do if len(c[1]) == width because the slice can keep on capturing empty strings at the end, so we remove them
		valid = [c for c in candidates if len(c[1]) == width and c[1] in SHORT]
		if not valid:
			# if none matched then no longer ones will match either, we're done
			break
		# remove all the indices that didn't match
		viable_indices = [i[0] for i in valid]

		results.append((width, valid))

		if width == len(LONG):
			break
		width += 1


	SYMBOL_COUNTS = Counter(SHORT)

	def iter():
		for result in reversed(results):
			width = result[0]
			for match in result[1]:
				yield width,match

	def can_add():
		'if nearest index >= length and symbols arent used up then yes'
		# index: diff = abs(a-b) if diff < length and diff != 0 (not the same start position as an existing one!)

	for s in iter():
		print(s)


	# TODO then score: 0.0 if not found (different string lengths or symbol unused), 1.0 if same symbol in same place, otherwise multiply by distance from original index in SHORT?  so the closest the long matches are to expected position the stronger the score, from .5 - 1.0?

	return {
		'string_order':[LONG, SHORT],
		'matches':results,
		'score':-1., # TODO
		}

if __name__ == '__main__':

	print(similarity('dog', 'doggy'))
	print(similarity('dog', 'dog'))
	print(similarity('Dog', 'dog'))
	print(similarity('Dog', 'dog', ignore_case=True))
	print(similarity('dodo', 'doddoddodododo'))
	print(similarity('d', 1))
	print(similarity([1,2,3], (1,2,2,3,1,2,3,4,5)))
	print(similarity(2,2))


