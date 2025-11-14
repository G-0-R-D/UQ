
#ifndef __SnapObject_H__
#define __SnapObject_H__

#include "snap_interface.h"

#define __SnapObject_MAX_SIZE 1024 * 1000 * 1000 // ? TODO
#define __SnapObject_NO_REFCOUNT -1000000

#define __SnapObject_CONST(TYPE, SIZE, BYTES) {\
	.__type__ = __SNAP_MACRO_PRE_EVAL(TYPE),\
	.__refcount__ = __SnapObject_NO_REFCOUNT,\
	.__size__ = (__SNAP_MACRO_PRE_EVAL(SIZE) != NULL) ? (snap_int_t)(__SNAP_MACRO_PRE_EVAL(SIZE) * -1) : 0,\
	.__bytes__ = (char*)__SNAP_MACRO_PRE_EVAL(BYTES),\
	}

/* NOTE: these macros work better in the positive (negative can mislead if OBJECT is NULL!) */
#define __SnapObject_WAS_ALLOCATED(OBJECT) ((OBJECT) != NULL && (OBJECT)->__refcount__ != __SnapObject_NO_REFCOUNT)
#define __SnapObject_BYTES_WERE_ALLOCATED(OBJECT) ((OBJECT) != NULL && (OBJECT)->__size__ > -1)

/* NOTE: this length op assumes bytes are array of SnapObject* (as is the standard), if uncertain: __len__ method should be used...
this is low-level api */
#define __SnapObject_length(OBJECT) ((snap_int_t)((OBJECT) != NULL ? __SNAP_ABS((OBJECT)->__size__) / sizeof (SnapObject*) : 0))


SnapObject* _SnapObject_realloc(SnapObject* ENV, SnapObject* self, int SIZE){
	/* https://stackoverflow.com/questions/21006707/proper-usage-of-realloc

	NOTE: pass -1 to actually delete, setting length to 0 does not delete,
	the idea is that once a list is created it should stick around until explicitly deleted
	if 0 deleted then lists would need to be re-assigned to nodes when reallocated to 0!

	LENGTH < 0 to delete SnapList itself, otherwise it reallocates just the data?
	*/

	if (!self){
		/*__RAISE(ENV, "cannot reallocate NULL! needs &SnapObject address");*/
		return NULL;
	}

	/* count NULL pointers in int list and reorder then remove end? */
	if (SIZE < 0){
		if (*self){
			__SNAP_FREE((*self)->__bytes__);
			__SNAP_FREE(*self);
			*self = NULL;
		}
		return NULL;
	}

	/*
	if (LENGTH > SnapList_MAX_LENGTH){
		snap_error("SnapList_realloc(..., LENGTH) > SnapList_MAX_LENGTH {%d}; too long!\n", SnapList_MAX_LENGTH);
		return (any)"ERROR";
	}*/

	if (!*self){
		*self = (SnapObject)__SNAP_MALLOC(sizeof (SnapObject_t));
		(*self)->__type__ = NULL;
		/*(*self)->__gc__.PREVIOUS = NULL; (*self)->__gc__.LIST = NULL; (*self)->__gc__.NEXT = NULL; */
		(*self)->__refcount__ = 0;
		(*self)->__size__ = 0;
		(*self)->__bytes__ = NULL;
	}

	if (SIZE == 0){
		(*self)->__size__ = 0;
		__SNAP_FREE((*self)->__bytes__);
		(*self)->__bytes__ = NULL;
		return NULL;
	}

	int current_size = (*self)->__size__;
	if (current_size == SIZE){
		/* same size, nothing to do*/
		return NULL;
	}



	if (!(*self)->__size__ < 0){
		return __RAISE(ENV, NULL, "__size__ < 0; attempt to realloc static SnapObject?");
	}
	
	char* tmp_ptr = (char*)__SNAP_REALLOC((*self)->__bytes__, SIZE);/* * sizeof (char));*/
	if (tmp_ptr == NULL){
		return __RAISE(ENV, NULL, "_SnapObject_realloc() failed!");
	}
	else {

		(*self)->__size__ = SIZE;

		/* zero out newly reallocated*/
		#if 0
		int diff = LENGTH-current_length;
		if (diff > 0){
			snap_memset(tmp_ptr + current_length, 0, diff * sizeof (any));
		}
		#else
		while (current_size < SIZE){
			tmp_ptr[current_size++] = '\0';
		}
		#endif

		(*self)->__bytes__ = tmp_ptr;
	}

	return NULL;
}


int _findattr(SnapObject* INSTANCE, const char* ATTR){
	/*this is the raw version, for internal use only... literally just find the ATTR on self and return the value*/
	/*TODO return snap_binary_search(...)*/
	return -1;
}

SnapObject* __SnapObject___get__(SnapObject* ENV, SnapObject* INSTANCE, const char* ATTR){
	/*this is the generalized logic of what should usually happen for (*OBJ)->__type__(ENV, INSTANCE, ATTR)*/
	/*TODO
	https://blog.peterlamut.com/2018/11/04/python-attribute-lookup-explained-in-detail/#fnref-359-1
	https://utcc.utoronto.ca/~cks/space/blog/python/AttributeLookupOrder

	TODO assign functions to type (using SNAP_FUNC() constant below each definition), and then bind them by doing instance check on return to see if it is a function?  python creates BoundMethod on access...

	SnapObject* VALUE = NULL;

	int idx = _findattr(INSTANCE, "__getattribute__");
	if (idx > -1){
		VALUE = _call("__getattribute__", _msg(_str()));
	}
	else {

		idx = _findattr(INSTANCE, ATTR);
		if (idx > 0){
			VALUE = (*INSTANCE)->__bytes__[idx+1];
		}
		else {
		
			idx = _findattr(INSTANCE, "__getattr__");
			if (idx > 0){
				VALUE = _call("__getattr__", _msg(_str(ATTR)));
			}	
		}
	}

	if (idx < 0){
		_RAISE("AttributeError", "no attr");
	}

	TODO if returned element has attr "__get__" then call it and return that...
	*/
	
	return NULL;
}

SnapObject* SnapObject_instance___getattribute__(SnapObject* ENV, SnapObject* INSTANCE, SnapObject* MSG){
	/* XXX this isn't assigned unless overridden...
	just find it in self->__bytes__ as attrs
	*/
	return NULL;
}


/*TODO these are __get__ assigned to instance...*/
SnapObject* SnapObject_instance(SnapObject* ENV, SnapObject* INSTANCE, const char* ATTR){
	if (ATTR == NULL){
		/*
		if there are superclasses call them first in mro() order...

		TODO the BoundMethod binding needs to be done by the type when returning the function...

		_set(INSTANCE, "__attr__", _bound_method(INSTANCE, __attr__cfunc)); TODO include line info with bound method for debug out?
		*/
		return NULL;
	}
	return __SnapObject___get__(ENV, INSTANCE, ATTR);
}

SnapObject* SnapObject_type_func_mro(SnapObject* ENV, SnapObject* INSTANCE, SnapObject* MSG){

	return NULL;
}
SnapObject* SnapObject_type_func____call__(SnapObject* ENV, SnapObject* INSTANCE, SnapObject* MSG){
	
	return NULL;
}

SnapObject* SnapObject_type(SnapObject* ENV, SnapObject* INSTANCE, const char* ATTR){
	if (ATTR == NULL){

		/*TODO init*/
		

		return NULL;
	}
	return __SnapObject___get__(ENV, INSTANCE, ATTR);
}


#endif /* __SnapObject_H__ */
