
#ifndef __snap_api_H__
#define __snap_api_H__

#include "snap/snap_core.h"
#include "snap_args.h"
#include "snap_msg.h"


int __ERRORED(SnapObject_t* ENV){
	/* if ENV.raise: return 1; */
	return 0;
}
/* TODO if _ERRORED(x) _RETURN(NULL) */
#define _ERRORED() __ERRORED(ENV)

SnapObject_t* __RAISE(SnapObject_t* ENV, const char* EXCEPTION_TYPE, const char* MESSAGE){
	/*
	if (EXCEPTION_TYPE == NULL){
		 // critical error 
	}
	else {
		 // initialize EXCEPTION_TYPE from ENV, and register it in ENV with _str(MESSAGE))
	}
	*/
	return NULL; /* always, error is registered in ENV, we just make it possible to say return __RAISE(...) */
}
#define _RAISE(EXCEPTION, MESSAGE) return __RAISE(ENV, EXCEPTION, MESSAGE)

SnapObject_t* __RETURN(SnapObject_t* ENV, SnapObject_t* OBJ){
	/* TODO on return check ENV gc for unassigned objects and delete them all*/
	_INCREF(OBJ); /* keep it alive, receiver is responsible for dereferencing it XXX put this into a pending area on ENV instead?*/
	_DECREF(ENV);
	return OBJ;
}
#define _RETURN(OBJ) return __RETURN(ENV, OBJ)

SnapObject_t* __INCREF(SnapObject_t* ENV, SnapObject_t* OBJ){
	/*TODO incref the OBJ*/
	if (!OBJ){
		/* TODO warn*/
	}
	return OBJ;
}
#define _INCREF(OBJ) __INCREF(ENV, OBJ)

SnapObject_t* __DECREF(SnapObject_t* ENV, SnapObject_t* OBJ){
	/*TODO decref, possibly delete, if delete return NULL*/
	return OBJ;
}
#define _DECREF(OBJ) __DECREF(ENV, OBJ)


SnapObject_t* __call(SnapObject_t* ENV, SnapObject_t* INSTANCE, SnapObject_t* MSG){

	/*
	if (ERRORED){
		handle
	}

	SnapObject_t* call_method = _getattr(INSTANCE, _str("__call__"))
	if (call_method == NULL){
		RAISE?
	}

	verify is function/method type and call the __bytes__ directly?

	# TODO we have a loop here, when do we resolve __call__ into c_func_t?  or should "__call__" in dict always point to c_func_t*?

	SnapObject_t* callable = INSTANCE->__type__(ENV, INSTANCE, "__getattribute__", _msg_a(_a1(_str("__call__"))));
	if (callable){
		return callable->__type__(ENV, callable, "__call__", MSG);
	}

	dump ENV->__unclaimed__ (do this in return/raise?)

	*/
	return NULL;

#define _call(INSTANCE, MSG) __call(ENV, INSTANCE, MSG)


SnapObject_t* _LOCAL_ENV(SnapObject_t* PARENT_ENV){

	SnapObject_t* LOCAL_ENV = NULL; /* TODO New(PARENT_ENV, SnapEnv_class);*/
	/* create new ENV with parent_env assigned */

	return __INCREF(PARENT_ENV, LOCAL_ENV);
}



SnapObject_t* __getattr(SnapObject_t* ENV, SnapObject_t* OBJ, const char* ATTR){
	/*
	# TODO no refcounting, this just accesses the string element from the dict and returns it or raise
	#	-- __getattribute__ method would just call this for dict access

	if (OBJ == NULL){
		_RAISE("AttributeError", "NULL object in __getattr");
	}
	if (ATTR == NULL){
		_RAISE("AttributeError", "NULL attribute in __getattr");
	}

	TODO just call "__getattribute__" of OBJ

	TODO verify ATTR is string instance... -- lowlevel isinstance, just access the string type directly?

	binary search dict for string, return value if found or raise KeyError

	call __get__ if it implements one and return that...

	*/
	return NULL;
}
#define _getattr(OBJ, ATTR) __getattr(ENV, OBJ, ATTR)

/* TODO _set()? */


/* XXX just create isinstance function in ENV, access it via _call(_get(ENV, _str("isinstance")), ...)
SnapObject_t* __isinstance(SnapObject_t* ENV, SnapObject_t* MSG){
	TEST can be single type, or list/tuple of types
	return NULL;
}
*/



void __DISCARD(SnapObject_t* ENV, SnapObject_t* OBJ){
	if (!OBJ){
		return;
	}
	/* TODO decref OBJ from ENV (this catches any output from expressions with output)
	 --refcount

	TODO should GC use the listener system, connect GC to child nodes?
	*/
}
#define _DISCARD(OBJ) __DISCARD(ENV, OBJ)

/* LITERALS: str, bytes, int, float, complex, bool, NULL
list, dict, set, function, method, ... */

SnapObject_t* __str(SnapObject_t* ENV, const char* STRING){
	/* make, register for ENV.GC, and return new SnapObject_t string*/
	/* copy the string to self.__data__ of newly created SnapString class...*/
	if (_ERRORED()){
		return NULL;
	}
	/*
	int idx = _findattr(ENV, "str");
	if (idx < 0){
		_RAISE(NULL, "\"str\" not found in ENV; cannot create _str(\"%s\")", STRING);
	}
	SnapObject_t* StrType = (*ENV)->__data__[idx+1];
	SnapObject_t* UserStr = SnapObject_t_new(ENV, StrType->__data__['__func__'], MSG);
	(*UserStr)->__data__['__data__'] = strcopy(STRING)
	get the "str" class from ENV and initialize it using a copy of STRING
	_INCREF(UserStr);
	_RETURN(UserStr);
	*/
	return NULL;
}
#define _str(STRING) __str(ENV, STRING)

/*
SnapObject_t* _cstr(SnapObject_t* ENV, const char* STRING){
	return as SnapCodeString() instance
	TODO instances of CStr register the strings with ENV?  so they are each given a unique code as well...  so do search for string, if not there then register it and give it a code (len(strings)+1)


	return NULL;
}
*/

SnapObject_t* __bytes(SnapObject_t* ENV, char* BYTES, int SIZE){
	return NULL;
}
#define _bytes(BYTES, SIZE) __bytes(ENV, BYTES, SIZE)

char* _as_bytes(SnapObject_t* ENV, SnapObject_t* OBJ, int* SIZE_FEEDBACK){
	/*XXX deprecated? this would require accessing the __bytes__ data of a bytes instance...*/
	return NULL;
}
#define _as_bytes(OBJ) __as_bytes(ENV, OBJ)


SnapObject_t* __int(SnapObject_t* ENV, int VALUE){
	/*TODO message with value*/
	SnapObject_t* new_int = NULL; /* _call(_get(ENV, _str("int")), NULL);*/ /*TODO msg for value*/
	if (new_int == NULL){
		_RAISE(NULL, "unable to create new int");
	}
	/*(*new_int)->__data__ = */
	_RETURN(new_int);
}
#define _int(VALUE) __int(ENV, VALUE)

int __as_int(SnapObject_t* ENV, SnapObject_t* INT){
	/*TODO verify is int type?*/
	return *(int*)(*INT)->__bytes__;
}
#define _as_int(INT) __as_int(ENV, INT)

SnapObject_t* __bool(SnapObject_t* ENV, int INT){
	/* TODO get from ENV, or create new SnapBool if missing, assigned constants...*/
	return NULL;
}
#define _bool(INT) __bool(ENV, INT)

int __as_bool(SnapObject_t* ENV, SnapObject_t* OBJ){
	/*TODO bool test of __data__ or call it?*/
	return 0;
}
#define _as_bool(OBJ) __as_bool(ENV, OBJ)



/* VARIABLES: */
SnapObject_t* __iter(SnapObject_t* ENV, SnapObject_t* ITERABLE){
	/*TODO
	if already is iterator instance: return
	otherwise look for __iter__ method and return the call of it
	or raise not iterable error
	*/
	return NULL;
}
#define _iter(ITERABLE) __iter(ENV, ITERABLE)

/* EXPRESSIONS: */

SnapObject_t* __unary_op(SnapObject_t* ENV, const char* OP, SnapObject_t* OBJECT){

	if ((void*)OP == (void*)"+"){
		/* TODO pos */
	}
	else if ((void*)OP == (void*)"-"){
		/* TODO neg */
	}
	else if ((void*)OP == (void*)"~"){
		/* TODO binary inversion (1 / 0 switch) */
	}
	else if ((void*)OP == (void*)"not"){
		/* TODO logical inversion, truth */
	}
	else {
		/* TODO raise */
	}
	/*
	TODO return ENV['True'] or ENV['False']
	*/
	return NULL;
}
#define _unary_op(OP, OBJECT) __unary_op(ENV, OP, OBJECT)

SnapObject_t* __binary_op(SnapObject_t* ENV, SnapObject_t* OBJECT_A, const char* OP, SnapObject_t* OBJECT_B){
	/*
	TODO return ENV['True'] or ENV['False']
	*/
	return NULL;
}
#define _binary_op(OBJECT_A, OP, OBJECT_B) __binary_op(ENV, OBJECT_A, OP, OBJECT_B)

SnapObject_t* __bool_op(SnapObject_t* ENV, const char* OP, SnapObject_t* ARGS){
	/*
	TODO return SnapObject_t* or int?
	*/
	return NULL; /*_get(ENV, _str("False"));*/
}
#define _bool_op(OP, ARGS) __bool_op(ENV, OP, ARGS)

/* SUBSCRIPTING: */

/* COMPREHENSIONS: */

/* STATEMENTS: */

void __assign(SnapObject_t* ENV, SnapObject_t* TARGETS, SnapObject_t* VALUE){

}
#define _assign(TARGETS, VALUE) __assign(ENV, TARGETS, VALUE)

void __augassign(SnapObject_t* ENV, SnapObject_t* TARGET, SnapObject_t* OP, SnapObject_t* VALUE){
	/*
	_call(_get(TARGET, OP), _msg(VALUE)) TODO
	*/
}
#define _augassign(TARGET, OP, VALUE) __augassign(ENV, TARGET, OP, VALUE)

/* IMPORTS:*/

void __import(SnapObject_t* ENV, const char* NAME){
	/* TODO*/
	return;
}
#define _import(NAME) __import(ENV, NAME)

void __import_from(SnapObject_t* ENV, const char* NAME, const char* FROM){
	/* TODO*/
	return;
}
#define _import_from(NAME, FROM) __import_from(ENV, NAME, FROM)

void __import_from_as(SnapObject_t* ENV, const char* NAME, const char* FROM, const char* AS){
	/* TODO*/
	return;
}
#define _import_from_as(NAME, FROM, AS) __import_from_as(ENV, NAME, FROM, AS)

/* CONTROL FLOW: */

/* PATTERN MATCHING: TODO v3.8+ */

/* TYPE ANNOTATIONS: TODO v3.8+ */

/* TYPE PARAMETERS: TODO v3.8+ */

/* FUNCTION AND CLASS DEFINITIONS: */
void __funcdef(SnapObject_t* ENV, const char* NAME, SnapObject_t* (*CALLABLE)(SnapObject_t*, SnapObject_t*)){
	/* TODO make new SnapFunction instance, and assign it the callable and put it into the ENV*/

}
#define _funcdef(NAME, CALLABLE) __funcdef(ENV, NAME, CALLABLE)

void __lambdef(SnapObject_t* ENV, const char* NAME, SnapObject_t* (*CALLABLE)(SnapObject_t*, SnapObject_t*)){

}
#define _lambdef(NAME, CALLABLE) __lambdef(ENV, NAME, CALLABLE)

void __classdef(SnapObject_t* ENV, const char* NAME, SnapObject_t* (*CALLABLE)(SnapObject_t*, SnapObject_t*, SnapObject_t*)){
	/*
	*/
}
#define _classdef(NAME, CALLABLE) __classdef(ENV, NAME, CALLABLE)

/* shorthand for TYPES: */
#define _dict(MSG) _call(_getattr(ENV, _str("dict")), MSG)
#define _list(MSG) _call(_getattr(ENV, _str("list")), MSG)
#define _tuple(MSG) _call(_getattr(ENV, _str("tuple")), MSG)
#define _set(MSG) _call(_getattr(ENV, _str("set")), MSG)

#endif /* __snap_api_H__ */
