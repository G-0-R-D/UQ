
#ifndef __SNAP_TYPES_H__
#define __SNAP_TYPES_H__

#include "snap_sys.h"

/* ../PROJECTS/snap/build/snap_core/ has latest code, bring it here... TODO*/

/* https://stackoverflow.com/questions/3988041/how-to-define-a-typedef-struct-containing-pointers-to-itself */
typedef struct SnapObject_t SnapObject_t;

/* typedef SnapObject_t* SnapObject; so SnapObject can be NULL XXX use SnapObject_t* to be clear... */


struct SnapObject_t {
	/* TODO we get() the attr and then call it with the message...  using it's __call__ method... if method return BoundMethod() instance... */
	/*SnapObject* (*__type__)(SnapObject* ENV, SnapObject* INSTANCE, const char* ATTR);*/
	/*SnapObject* (*__type__)(SnapObject* ENV, SnapObject* MSG); *//* MSG will contain self and attribute, this is a getattr lookup when called */
		/* basically just does the get logic */

	SnapObject_t* (*__type__)(SnapObject_t* ENV, SnapObject_t* self, const char* ATTR, SnapObject_t* MSG);
		/*
		used to identify the type (id) of the instance, and as an entry-point for a call...
		*/

	int __dict_length__;
		/*
		number of entries in dict (pairs of 2, so *2 for true length and then * sizeof (SnapObject) for byte length
		*/
	
	SnapObject_t* __dict__;
		/*
		SnapObject_t* key:value pairs, in a list
			-- use an actual dict object?  get it from ENV...
		*/

	int __byte_size__;
		/*
		indicates size of __bytes__
		< 0 means data is not owned and are const; no free (use size != 0: abs(size) when reading data)
		*/

	char* __bytes__;
		/*
		where information that is not SnapObject_t* may be stored, can be any type (up to the class to decide, and manage...)
		*/

	int __refcount__;
		/*
		count of number of references (done automagically with code injection)
		TODO how to handle self-references (when self is in own tree)
			-- best idea so far: require user to implement function to pass back any recursive references when applicable
			-- or use weakrefs to assign self into own tree (weakrefs are passthrough so it doesn't change the call api!)
		*/

	/* TODO SnapObject_t* __parents__ -> for recursive garbage collection? */
};

typedef struct snap_c_func_t {
	/* this is the portable way to store a function in a data pointer (can cast back out to another template if desired) */
	SnapObject_t* (*__c_func__)(SnapObject_t* ENV, SnapObject_t* MSG);
} snap_c_func_t;

/*
TODO
typedef struct SnapEnv_data_t {

	SnapObject_t* __stack__;
		- ?

	...?

} SnapEnv_data_t;

*/


#endif /* __SNAP_TYPES_H__ */
