
def build(ENV):

	SnapMessage = ENV.SnapMessage
	snap_time = ENV.snap_time

	# these are for generating events, which are internal because they don't implicitly emit through the entire 'tree'
	
	def snap_device_forward_event(self, MSG):
		# this is an internal call, bypassing the listener system

		#category,device = MSG.unpack('category', None, 'device', None)

		# XXX don't assume an emit is a time change for an input, inputs might require more complex timing,
		# and emitting doesn't necessarily even imply that the input itself was modified
		# this is for sending an event after configuration of the input is complete

		#double* time = (double*)snap_getattr_at(MSG, "time", 12);
		# make sure input time is set same as event (mostly for groups, but just always do it)
		#snap_assignattr_at(self, "time", &time, sizeof (double), IDX_SnapDeviceNode_time);

		#msg = SnapMessage(*MSG.args, **MSG.kwargs)
		MSG.source = self
		MSG.channel = "device_event"


		#msg.kwargs['input'] = self
		self.device_event.__send__(MSG)

		parents = self['parents']
		if parents:
			for parent in parents:
				# device and category will be parents...
				snap_device_forward_event(parent, MSG)

		"""
		# send to groups TODO if groups, send to them and they will forward through device, otherwise just forward to device here...
		groups = self['memberships']
		if groups:
			for group in groups:
				snap_device_forward_event(group, msg)
		else:
			# no more parents, emit through the device and category
			if device is not None:
				#msg.kwargs['input'] = device # ? no, it device isn't an input.
				device.device_event.__send__(msg)

			if category is not None:
				category.device_event.__send__(msg)
		"""

	ENV.snap_device_forward_event = snap_device_forward_event


	def snap_device_event(self, MSG):

		# MSG must have action and source, others are optional...

		MSG.source = self
		MSG.channel = 'device_event'

		return snap_device_forward_event(self, MSG)

		#assert MSG.kwargs and 'source' in MSG.kwargs and 'action' in MSG.kwargs, 'invalid message format'
		#assert isinstance(MSG.kwargs['source'], ENV.SnapDeviceNode) and isinstance(MSG.kwargs['action'], str), 'source must be SnapDeviceNode({}) and action must be string

		#assert MSG.kwargs and 'source' in MSG.kwargs and 'action' in MSG.kwargs, 'invalid message format'

		# XXX TODO category, device, time, ... can all be obtained from the input!  just send action and source! (and then msg.source gets updated to each parent)

		#action = MSG.kwargs.get('action')
		#assert isinstance(action, str), 'action must be specified as a string'

		#device = self['device']
		#assert device is not None, 'no device for snap_device_event'

		#category = device['category']

		#if device is None or category is None:
		#	''#raise TypeError('device or category missing:', device, category)

		#submsg = SnapMessage(
		#	action=action, # "MOTION" | "PRESS" | "RELEASE" (or "DRAG" defined by gui) (NOTE: EVENT will always be "DEVICE", this is MSG entry!)
		#	category=category,
		#	device=device,
		#	input=self, # will be re-assigned in parent emits to be self as well, original input(s) can be obtained from "sources"
		#	source=self,
		#	time=self['time'] or snap_time()
		#	)

		#if MSG.kwargs:
		#	if [k for k in MSG.kwargs.keys() if k in submsg.kwargs]:
		#		''#snap_debug('event entry overwritten', ACTION, [k for k in EXTRAS.keys() if k in submsg])
		#	# gui events might add local position in active graphic coordinates, for example...
		#	submsg.kwargs.update(MSG.kwargs) # TODO should user values be allowed to overwrite?

		return snap_device_forward_event(self, MSG)

	ENV.snap_device_event = snap_device_event

	# XXX not aggregating anymore...  just emit events for each single input (listen to group for changes to all children)
	def snap_device_aggregate_eventXXX(self, INPUT_LIST, ACTION, **EXTRAS):

		# this is for inputs that emit together, like x and y axis of a joystick...

		# emit event to each input, then propagate it through each parent (once per unique parent)

		if not INPUT_LIST:
			ENV.snap_debug('no inputs for aggregate event', repr(ACTION))
			return None

		time = snap_time()

		submsg = SnapMessage(
			action=ACTION,
			category=None,
			device=None,
			input=None, # set to self on each emit
			sources=INPUTS, # originators will always be available here in each emit
			time=time, # or where else to get it?  inputs will still have individual times that can be checked (in sources...)
			)

		if EXTRAS:
			if [k for k in EXTRAS.keys() if k in submsg.kwargs]:
				ENV.snap_debug('event entry overwritten', ACTION, [k for k in EXTRAS.keys() if k in submsg.kwargs])
			submsg.kwargs.update(EXTRAS)

		device = None
		category = None

		# accumulate all the unique parents into a new list to emit to
		unique_groups = []#set()

		for input in INPUT_LIST:

			# emit event for input (only)
			device = input['device']
			if device is not None:
				category = device['category']
			else:
				category = None

			if not (input and category and device):
				ENV.snap_warning("missing input({}) device({}) or category({}) on input".format(item, device, category))
				# remove this input from sources?  would require duplicating sources...
				continue

			submsg.kwargs['category'] = category
			submsg.kwargs['device'] = device
			submsg.kwargs['input'] = input

			# without propagation
			input.device_event.__send__(submsg)

			groups = input['memberships']
			if groups:
				for group in groups:
					if group not in unique_groups:
						unique_groups.append(group)

		for group in unique_groups: # XXX TODO just get list of groups from input node, then emit through each group...
			# emit through each parent and upward

			device = input['device']
			if device is not None:
				category = device['category']
			else:
				category = None

			if not (parent and category and device):
				ENV.snap_warning("missing input({}) device({}) or category({}) on input".format(item, device, category))
				continue

			submsg.kwargs['category'] = category
			submsg.kwargs['device'] = device
			submsg.kwargs['input'] = parent

			# with propagation
			snap_device_forward_event(group, submsg)

	#ENV.snap_device_aggregate_event = snap_device_aggregate_event

