

def build(ENV):

	def snap_outward_index(IDX, OFFSET, LENGTH):
		"""calculates the index in an array outward from an offset point (wraps with modulo (%))
		aka. "middle-out"
		IDX is normal index (0 would be "first" and LENGTH-1 would be "last" -- but it wraps)
		OFFSET is start position from 0, as an index (so 2 to start at the 3rd entry)
		LENGTH of the array (the array is not visible to the algorithm)
		"""
		return (
			OFFSET + 
			# floor division results in doubling of same number like 001122334455...
			# and +1 prevents second initial 0 (0112233...)
			(((IDX+1) / 2) *
			# direction makes 0,1,-1,2,-2,3,-3,...
			(-1 + (2 * (IDX % 2)))) # direction (-1 or 1)
			) % LENGTH
	ENV.snap_outward_index = snap_outward_index

