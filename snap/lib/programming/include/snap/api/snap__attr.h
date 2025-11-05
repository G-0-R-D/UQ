
#ifndef __SNAP__ATTR_H__
#define __SNAP__ATTR_H__

#include "SnapObject_t.h"

/*TODO attr*/


SnapObject_t* SnapAttr_instance(SnapObject_t* ENV, SnapObject_t* INSTANCE, SnapObject_t* ATTR){
	/*TODO
	item is just a proxy/passthrough to the target (so it is invisible)
	-- incref does self and target refcount...
	*/
	return NULL;
}

SnapObject_t* SnapAttr_type(SnapObject_t* ENV, SnapObject_t* INSTANCE, SnapObject_t* ATTR){
	/*
	if (_as_bool(_compare(ATTR, _str("__init__")))){
		assign any methods if they aren't assigned
	}
	return SnapObject___get__(ENV, INSTANCE, ATTR);
	*/
	return NULL;
}


SnapObject_t* __attr(SnapObject_t* ENV, SnapObject_t* BASE, SnapObject_t* KEY){
	/*TODO
	create SnapItem() instance and return
	SnapObject_t* ITEM = SnapObject_t_new(SnapItem_class, _msg(_a2(), NULL, NULL, NULL));
	if (ITEM == NULL){
		_RAISE(NULL, "unable to allocate an _attr");
	}
	*/
	return NULL;
}
#define _attr(BASE, KEY) __attr(ENV, BASE, KEY)

#endif /* __SNAP__ATTR_H__ */

