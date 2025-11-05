
# TODO match tag start / end, or error (OR(OR('<' ..., ERROR), <text>)
# so find tags, and determine their validity separately, ignore comments, everything else is text

# for the DOM, just make a flat list of the tree (dict) nodes/tags, with indent param?  the indent param could even go on the tree nodes!
#	-- maybe maintain a tree and flat view together?  or put the offset info into the tree?  so we know where the nodes are placed starting anywhere?  -- flat list would be useful for binary search though

# TODO do the tag correction in the decoder as an option?  grammar is basically just matching tags, ignoring comments, and capturing everything else as text

