
from PyQt5.QtGui import *
from PyQt5.QtCore import * # Qt

import SNAP_KEYMAP
from similarity import similarity

FOUND = []

missed = []

def match_by_keyval(VALUE):
	for entry in SNAP_KEYMAP.SNAP_KEYMAP:
		if VALUE in [k[0] for k in entry.get('keys',[])]:
			return entry

def match_by_name(NAME):
	for entry in SNAP_KEYMAP.SNAP_KEYMAP:
		if NAME == entry['scan'][1].upper():
			return entry

# TODO longest overlapping string (any position)?
#	-- start by finding same single characters?  then compare from there?
#	-- find the leftmost character in common, then compare largest sequence from there, and keep on advancing
# algo: for idx in a, compare a+ to each start point in b and score the longest run

def string_distance(A, B):
	'' # TODO sort each string, then remove uncommon characters, then score based on same letter and same position as normalized value? 1.0 means they're identical, 0.0 means no letters in common
	# sort both and then start 'pairing' them up by removing if they both contain the symbol
	# score 1 for each symbol that is the same, and 1 for each symbol in the same location, and 1 if the previous symbol is also previous in other string (what does that mean without fixed position?)

	# TODO if we use the other algorithm and then process layers from bottom up, keeping track of which aren't duplicates?  and then overwriting with longer sequences and removing ones that are overlapped by them?
	# do the scoring such that 50% would be max if all the letters are the same but not in the same places?  and 100% if they are in same places.  give .5 for same letter but different place? with .25 bonus if previous is same?  so just .25 bonus to each in the longer runs?  or .5?  so 1.0 to each in a sequence from position 2?

	# TODO use the find_all_matches algorithm, start from the longest matches, remove duplicates and score .75 to each and 1.0 if they are in same position?  then go to each sublayer and score non-overlapping as .5?  and then total that out of 1.0 (/length of base (longest))

	# TODO case sensitive optional

	# TODO remove duplicates and overlapping
	#	-- just keep the leftmost one and then remove anything that overlaps it?  assume first match would have favor?
	# same symbol in same position = 1.0
	# otherwise .5 for same letter, and then sequence gets .75 for each starting at second position
	# how to score when strings are different lengths?  can't be 1.0 unless same length...  each additional character scores a 0.0?

	# start with longest matches
	#	-- from left to right, remove overlapping, and remove once letters aren't available for use anymore (only letters found in original sequence)
	#	-- 1.0 if same letter and position, otherwise .5 for same letter, and .75 for index 2+ (or weight by how far they are from the origin of the sequence? TODO do this by keeping track of the index that it matched at in the other string and taking the difference?)
	#	-- continue down through shorter sequences, and remove overlapping (if they share the start index then just remove)
	#	add 0.0 * difference to the total weighting and then normalize (or just non-matching chars are 0.0 in base)

	# just start iterating from the top down, add if there is not another within the abs(diff) (and if symbols aren't used up)
	# then we score after
	def iter():
		for result in reversed(results):
			for match in result[1]:
				yield match

	# TODO binary search and insert since this is indexed data... (binary search for closest index and if it's > width then we're clear to add -- if symbols are available)

def find_all_matches(A, B):

	# TODO return idx,match, ... for each pattern

	# TODO just make this string_distance(A,B, **SETTINGS) and return dict with all info, and do the simplification if desired

	BASE = (A if len(A) > len(B) else B).upper()
	SOURCE = (B if len(A) > len(B) else A).upper()

	width = 1

	results = []

	viable_indices = range(len(BASE)) # start with all as viable, this becomes the previous indices at each pass
	while 1:

		# take all possible slices (viable indices will reduce upon each iteration)
		candidates = [(idx, BASE[idx:idx+width]) for idx in viable_indices]
		#print('candidates', width, candidates)
		# then remove all the slices that have no overlap with the other string
		# NOTE: we do if len(c[1]) == width because the slice can keep on capturing empty strings at the end, so we remove them
		valid = [c for c in candidates if len(c[1]) == width and c[1] in SOURCE]
		if not valid:
			# if none matched then no longer ones will match either, we're done
			break
		# remove all the indices that didn't match
		viable_indices = [i[0] for i in valid]

		results.append((width, valid))

		if width == len(BASE):
			break
		width += 1

	return results # TODO also return BASE?

# TODO remove 'overlapping'; kind of merge all the layers together in the results that don't occupy the same symbols...  give priority to longer runs...  so start with the top ones, and then remove the overlapping littler ones...
#	-- process the longest, and then add in the shorter ones that don't overlap, keep going down...
# TODO also make it optional to exclude extra sequences that would mean duplication of symbols (if there is only one 'a' in A then don't count more than one 'a')

for name in dir(Qt):
	if 'key' not in name.lower():
		continue

	value = getattr(Qt, name)
	if not isinstance(value, int):
		continue
	
	#print(name, value)

	entry = match_by_keyval(value)
	if entry is not None:
		FOUND.append(entry)
		continue

	check_name = name.upper().replace('KEY_', '')
	entry = match_by_name(check_name)
	if entry is not None:
		FOUND.append(entry)
		continue

	#print('miss', name, value)
	missed.append((name,value))

	# TODO lookup value in any key with entries beyond scancode...  if that fails then attempt to match by name?

for entry in SNAP_KEYMAP.SNAP_KEYMAP:
	if entry in FOUND:
		continue

	entry_name = entry['scan'][1]

	scores = []

	for name,value in missed:
		score = similarity(entry_name, name)
		if score > 0:
			scores.append((name,score))

	print(entry_name, list(sorted(scores, key=lambda x: x[1]))[-3:])


for name,value in missed:
	''#print('miss', name, value)

for entry in FOUND:
	''#print('found', entry)

