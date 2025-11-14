
SnapObject_t* MyClass_class(SnapObject_t* ENV, SnapObject_t* self, const char* ATTR, SnapObject_t* MSG){

	/*TODO the const char* ATTR should always attempt to get the same attr from dict first, and if it's there then call it in user space, otherwise it can implement it's own behaviour */

	if ((void*)ATTR == (void*)"__type__"){
		// TODO return SnapObject_t* from ENV namespace...
	}
	return NULL;
}

SnapObject_t* MyClass_type(SnapObject_t* ENV, SnapObject_t* self, const char* ATTR, SnapObject_t* MSG){

	if ((void*)ATTR == (void*)"__call__"){
		// TODO return new class instance, pass MSG
		// TODO first attempt to get __call__ from self->__dict__,
		// otherwise call  return self->__type__(ENV, self, "__new__", MSG);
	}

	else if ((void*)ATTR == (void*)"__new__"){
		// TODO check in dict, otherwise just create new normally?
		return __new(ENV, MyClass_class, MSG);
	}

	else if ((void*)ATTR == (void*)"__getattribute__"){

		// get from dict
		// TODO make dict actual SnapObject_t* dict with interface!

		// TODO first try __getattribute__ lookup and if there is one, call that (user one), otherwise do a dict lookup for the attribute

		// then try __getattr__ if not found

		// if there is a __get__ handler call it and return the result
	}

	return __RAISE(ENV, "AttributeError", NULL);
}
