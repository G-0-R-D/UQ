
#ifndef __SNAP_SYS_H__
#define __SNAP_SYS_H__

#include <stdlib.h>
#include <stdio.h>
#include <string.h> /* for memcpy */
#include <stdint.h>
#include <limits.h>

#include <unistd.h>

/*
#include <fcntl.h>

#include <pthread.h> /* posix */
#include <semaphore.h>
/*#include <stdatomic.h>*/
#include <sys/wait.h>

/* https://www.youtube.com/watch?v=83M5-NPDeWs */
#include <signal.h>
/* rename kill to more logical name */
/* TODO use newer sigaction? */
#define snap_signal_send kill

#include <dirent.h>

/*///////////// MATH /////////////////////*/

#include <math.h> /* TODO fmin and fmax -ansi compat? */
#include <float.h>

/* TODO snap_string_to_double, etc... */
/* http://www.cplusplus.com/reference/cstdlib/atof/ */

#define __SNAP_MACRO_PRE_EVAL(X) (X) /* gives each entry chance to evaluate before casting, for phrases like "data", data+1 -> (any)(data+1) */


#define __SNAP_MALLOC malloc
#define __SNAP_FREE(X) free((void*)__SNAP_MACRO_PRE_EVAL(X))
#define __SNAP_MEMSET(X, INT, SIZE) memset((void*)__SNAP_MACRO_PRE_EVAL(X), INT, SIZE)
#define __SNAP_MEMCPY(A, B, SIZE) memcpy((void*)__SNAP_MACRO_PRE_EVAL(A), (const void*)__SNAP_MACRO_PRE_EVAL(B), SIZE)
#define __SNAP_MEMCMP(A, B, SIZE) memcmp((const void*)__SNAP_MACRO_PRE_EVAL(A), (const void*)__SNAP_MACRO_PRE_EVAL(B), SIZE)
#define __SNAP_REALLOC(A, SIZE) realloc((void*)__SNAP_MACRO_PRE_EVAL(A), SIZE)

/* https://code.woboq.org/userspace/glibc/stdlib/qsort.c.html */
#define __SNAP_SWAP(A, B, SIZE){\
	size_t __size = (SIZE);\
	char *__a = (A), *__b = (B);\
	char __tmp;\
	while (__size-- > 0){\
		__tmp = *__a;\
		*__a++ = *__b;\
		*__b++ = __tmp;\
	}\
}
/* copy memory block from A to B */
#define __SNAP_COPY(A, B, SIZE){\
	size_t __size = (SIZE);\
	char *__a = (A), *__b = (B);\
	while (__size-- > 0){\
		*__b++ = *__a++;\
	}\
}



#endif /* __SNAP_SYS_H__ */
