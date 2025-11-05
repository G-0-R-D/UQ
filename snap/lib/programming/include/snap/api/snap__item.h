
#ifndef __SNAP__ITEM_H__
#define __SNAP__ITEM_H__

#include "SnapObject.h"
/*TODO attr*/


SnapObject* SnapItem_instance(SnapObject* ENV, SnapObject* INSTANCE, SnapObject* ATTR){
	/*TODO
	item is just a proxy/passthrough to the target (so it is invisible)
	-- incref does self and target refcount...
	*/
	return NULL;
}

SnapObject* SnapItem_type(SnapObject* ENV, SnapObject* INSTANCE, SnapObject* ATTR){
	/*
	if (_as_bool(_compare(ATTR, _str("__init__")))){
		assign any methods if they aren't assigned
	}
	return SnapObject___get__(ENV, INSTANCE, ATTR);
	*/
	return NULL;
}


SnapObject* __item(SnapObject* ENV, SnapObject* BASE, SnapObject* KEY){
	/*TODO
	create SnapItem() instance and return
	SnapObject* ITEM = SnapObject_new(SnapItem_class, _msg(_a2(), NULL, NULL, NULL));
	if (ITEM == NULL){
		_RAISE(NULL, "unable to allocate an _item");
	}
	*/
	return NULL;
}
#define _item(BASE, KEY) __item(ENV, BASE, KEY)

#endif /* __SNAP__ITEM_H__ */
