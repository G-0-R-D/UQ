
# TODO reading/writing to buffer can be done optimally by re-allocating a max buffer, and then keep track of start/end positions...  if end < start it means the read/write wraps around!
#	-- so we can just keep writing after end until we reach start again in which case buffer is processed!

