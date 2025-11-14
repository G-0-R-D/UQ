
class SnapEvent(SnapNode):

	# implement methods for event types to handle (if missing then presumably the event has no effect)
	#	-- returns:
		True: status is now True (event accepted, condition met)
		False: status is now False (event accepted, but condition failed)
		None: no status, this event is not processed (or the handler is not defined on this event)


