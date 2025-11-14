

"""
ref: Python2.7/Objects/typeobject.c

	_PyType_Lookup
	fill_classic_mro
		just append current (child) class to mro if not in there, then call on each base (which is added if it isn't in there...)
	mro_implementation
	pmerge
"""

#https://en.wikipedia.org/wiki/C3_linearization
# basically a breadth-first bottom-up front-back search, with no repeats
# referenced from Python2.7/Objects/typeobject.c
		

def fill_mro(MRO, CLS):

	if CLS in MRO:
		return
	else:
		MRO.append(CLS)

	for base in CLS.bases():
		fill_mro(MRO, base)

	return MRO


def pmerge(to_merge):

	result = []

	remain = [0] * len(to_merge)

	empty_containers = 0
	for i in range(len(to_merge)):

		cur_list = to_merge[i]

		if remain[i] >= len(cur_list):
			empty_containers += 1
			continue

		candidate = cur_list[remain[i]]

		# check if candidate occurs in tail of any (remaining) merge lists
		skip = False
		for j in range(len(to_merge)):
			j_lst = to_merge[j]
			if remain[j] < len(j_lst) and candidate in j_lst[j+1:]:
				skip = True
				break # skip, go to next in outer loop

		if skip:
			continue

		result.append(candidate)

		# move past all occurences of the candidate (as a head)
		for j in range(len(to_merge)):
			j_lst = to_merge[j]
			if remain[j] < len(j_list) and j_lst[remain[j]] == candidate:
				remain[j] += 1

	if empty_containers == len(to_merge):
		return result

	raise Exception('unable to resolve mro')
	

def mro_implementation(TYPE):

	to_merge = []

	for base in TYPE.bases():

		if base.__mro__:
			to_merge.append(base.__mro__)
		else:
			to_merge.append(fill_mro([]))

	to_merge.append(TYPE.bases())

	return pmerge(to_merge)




class SnapObject:
	# just thinking out loud...

	def __mro__(self):

		if SnapObject.__mro__ is None:
			# NOTE: this will assign to classvars, so in __class_dict__...
			SnapObject.__mro__ = mro_implementation(SnapObject)

		return SnapObject.__mro__

	def set(self, **SETTINGS):
		for attr,value in SETTINGS.items():
			snap_warning("unhandled set({})".format(repr(attr)))




	def __listen__(self, LISTENER):
		''
		# TODO disallow if type is not allocated? (__size__ < 0)

	def __ignore__(self, LISTENER):
		''

	def __listening__(self, LISTENER):
		''


	def __incref__(self):
		''

	def __decref__(self):
		''




	def __eq__(self, OTHER):
		'compare id default -> use self.__cmp__() == 0'


	# def __getattribute__(self, ATTR): user can implement for pre-lookup behaviour
	# def __getattr__(self, ATTR): user can implement for missed lookup behaviour

	def __setattr__(self, ATTR, VALUE):
		'' # TODO ?  implement binary search assignment...

		snap_raw("""
		// args are unpacked

		if (__SNAP_SETATTR(ENV, self, != VALUE){
			return __SNAP_RAISE(ENV, ARGS, KWARGS, "AssignError", "unable to assign attr");
		}
		""")

		return VALUE; # indicates assign was successful?

		# TODO this is always to self!  (overwrite class attrs by writing onto self)


	#def __bases__(self): XXX this is class method, and will be hard-coded / fixed
	#	return None # no bases on root!  but if there are bases this will return a list of the bases (type instances from env)

	def __class__(self):
		# NOTE: there can only be one type, this is not the superclass!  this is the class implementation / type instance from env
		return SnapObject # class type instance from ENV

	def __id__(self):
		new_int = SnapInt() # TODO encoder will error check this worked correctly...?  inside the __call__ method?
		snap_raw("((snap_int_t)new_int->__bytes__) = (snap_int_t)self; // address of self as int")
		return new_int

	def __isinstance__(self, *TYPES):
		bases = self.__class__().__bases__()
		if bases:
			for b in bases:
				if b in TYPES:
					return True
		return False # subclass would return superclass call
	

	def __str__(self):
		''

	def __repr__(self):
		''

	def __call__(self):
		raise NotImplementedError("__call__")


	def __init__(self):
		''


	def __delete__(self):
		snap_raw("""

		if (!self || self->__size__ < 0){
			return __SNAP_RETURN(ENV, ARGS, KWARGS, NULL);
		}

		SnapObject** bytes = (SnapObject**)self->__bytes__;
		self->__bytes__ = NULL;

		snap_int_t length = self->__size__ / sizeof (SnapObject*);
		self->__size__ = 0;
		while (--length > -1){
			__SNAP_DECREF(bytes[length]);
		}
		if (bytes){
			__SNAP_FREE(bytes);
		}
		""")


