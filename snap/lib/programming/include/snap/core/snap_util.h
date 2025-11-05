
#ifndef __SNAP_UTIL_H__
#define __SNAP_UTIL_H__


int snap_outward_index(int IDX, int OFFSET, int LENGTH){
	/*
	calculates the index in an array outward from an offset point (wraps with modulo (%))
	aka. "middle-out"
	IDX is normal index (0 would be "first" and LENGTH-1 would be "last" -- but it wraps)
	OFFSET is start position from 0, as an index (so 2 to start at the 3rd entry)
	LENGTH of the array (the array is not visible to the algorithm)
	*/
	return (
		OFFSET + 
		/* floor division results in doubling of same number like 001122334455... */
		/* and +1 prevents second initial 0 (0112233...) */
		(((IDX+1) / 2) *
		/* direction makes 0,1,-1,2,-2,3,-3,... */
		(-1 + (2 * (IDX % 2)))) /* direction (-1 or 1) */
		)
		% LENGTH;
}


int snap_binary_search(const void* DATA, const void* ITEM_P, size_t ITEM_SIZE, int L, int R,
	int (*COMPARE_CALLBACK)(const void*, const void*, void*), int RUN_TO_END, void* PTR){

	/* NOTE: ITEM_P needs to be the same type of pointer as in the array
		so an int would be &int
		a SnapNode in a SnapList needs to be &SnapNode
			-- the SnapList_sorted_binary_search api will pass the address of the item (so that it is inuitive from the user perspective, where item is the item they are searching for)

		this is so the same compare can be used for searching and sorting
	*/

	const char* data = (const char*)DATA;

	if (!data){
		if (RUN_TO_END){
			return 0;
		}
		return -1;
	}

	int cmp,center;

	while (R >= L){
		
		/* center = L + (R - L) / 2; */
		center = (L + R) / 2;

		cmp = COMPARE_CALLBACK((const void*)(data + (ITEM_SIZE * center)), ITEM_P, PTR);

		if (cmp > 0){
			R = center - 1;
		}
		else if (cmp < 0){
			L = center + 1;
		}
		else {
			if (RUN_TO_END){
				R = center - 1; /* found a match, but that might not be only one? */
				continue;
			}
			return center;
		}
	}

	if (RUN_TO_END){
		return L; /* if run to end this is next index (closest miss / best insertion point) */
	}
	return -1;
	
}


int snap_bytes_rotate(char* START, int SIZE, int COUNT){
	/*
	NOTE: the bytes remain contiguous, so we don't actually need to know how big an 'item' is
	also NOTE: this will therefore not work on variadic data (like unicode strings...)
	TODO variadic could probably be done by checking the end of the rotation is aligned...  as long as the start byte is still a start byte the whole string should be valid... (so you could use this on variable data as long as you knew the length from the start to the byte you want as the new start...?
	ie. as long as the COUNT specifies a valid start byte, it should be fine...
	*/
	if (SIZE < 1 || !START)
		return 1;

	COUNT *= 1; /* so negative moves to the 'left' */

	if (COUNT < 0){
		COUNT = SIZE - ((COUNT * -1) % SIZE);
	}
	else {
		COUNT %= SIZE;
	}

	if (COUNT == 0) /* after modulo, already in rotated position */
		return 0;

	int CHANNEL = 0,
		idx = 0, /* always start at 0 */
		next_idx,
		i = 1; /* skip the last one because we assign it manually after... */
	/*any tmp = (*self)->data[idx]; // if all goes well tmp will only be used once...  at worst: once per channel*/
	char tmp = START[0];
	while (i++ < SIZE){

		next_idx = (idx + COUNT) % SIZE;

		/*snap_out("[%d] -> [%d]", next_idx, idx);*/

		if (next_idx == CHANNEL){
			/* back to where we started prematurely (evenly divisible)... fudge one forward and continue on...
			snap_out("collision %d", CHANNEL);*/
			START[idx] = tmp;
			next_idx = ++CHANNEL;
			tmp = START[next_idx];
		}
		else {
			START[idx] = START[next_idx];
		}

		idx = next_idx;
	}

	START[idx] = tmp;

	return 0;
}


#endif /* __SNAP_UTIL_H__ */
