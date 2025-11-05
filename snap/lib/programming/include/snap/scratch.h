
SnapObject_t* MyClass_class(SnapObject_t* ENV, SnapObject_t* self, const char* ATTR, SnapObject_t* MSG){

	if ((void*)ATTR == (void*)"__type__"){
		// TODO return from ENV
	}
	return NULL;
}

SnapObject_t* MyClass_type(SnapObject_t* ENV, SnapObject_t* self, const char* ATTR, SnapObject_t* MSG){

	if ((void*)ATTR == (void*)"__call__"){
		// TODO return new class instance, pass MSG
		return __new(ENV, MyClass_class, MSG); // XXX redirect to __new__? self->__type__(ENV, self, "__new__", MSG);
	}

	else if ((void*)ATTR == (void*)"__new__"){
		// TODO check in dict, otherwise just create new normally?
	}

	else if ((void*)ATTR == (void*)"__getattribute__"){

		// get from dict
		// TODO make dict actual SnapObject_t* dict with interface!

		// TODO first try __getattribute__ lookup and if there is one, call that (user one), otherwise do a dict lookup for the attribute

		// then try __getattr__ if not found

		// of there is a __get__ handler call it and return the result
	}

	return __RAISE(ENV, "AttributeError", NULL);
}
