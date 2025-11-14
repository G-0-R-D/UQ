
#ifndef __SNAP_STR_H__
#define __SNAP_STR_H__

#include "snap_sys.h"


#define __SNAP_STRFMT(FMT_STRING, ...)({\
	/*
	https://linux.die.net/man/3/sprintf
	https://www.cplusplus.com/reference/cstdio/snprintf/ 
	https://stackoverflow.com/a/53447875
	https://ideone.com/pt0cOQ
	*/\
	char* string = NULL;\
	int required_length = snprintf(NULL, 0, FMT_STRING, ##__VA_ARGS__);\
	if (required_length < 0){\
		__SNAP_ERROR("unable to format string!");\
	}\
	else if (required_length > 0){\
		string = (char*)__SNAP_MALLOC(required_length + 1);\
		if (!string){\
			__SNAP_ERROR("unable to allocate string buffer!");\
		}\
		else {\
			snprintf(string, required_length + 1, FMT_STRING, ##__VA_ARGS__);\
		}\
	}\
	string;\
}


#endif /* __SNAP_STR_H__ */
