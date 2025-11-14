
#ifndef __SNAP_MATH_H__
#define __SNAP_MATH_H__


#include <math.h> /* TODO fmin and fmax -ansi compat? */
#include <float.h>


/* both defined as 64bits / 8 bytes: */
#define snap_int_t long int
#define snap_float_t double
/* XXX renaming to try to make it easier to type:
 expect these to always be the 'largest' (64bit) int and float respectively
#define snap_int long int
#define snap_float double
*/



#ifndef __SNAP_MATH_PI
	#ifdef M_PI
		#define __SNAP_MATH_PI M_PI
	#else
		#define __SNAP_MATH_PI 3.14159265358979323846
	#endif
#endif

#define __SNAP_DOUBLE_MIN DBL_MIN /*0.000000000001*/
#define __SNAP_DOUBLE_MAX DBL_MAX

#define __snap_fuzzy_is_null(NUM) ((NUM >= -__SNAP_DOUBLE_MIN && NUM <= __SNAP_DOUBLE_MIN) ? 1:0)
/*int snap_fuzzy_is_null(double NUM){
	return (NUM >= -SNAP_DOUBLE_MIN && NUM <= SNAP_DOUBLE_MIN);
}

int snap_fuzzy_is_equal(double A, double B){
	//return fabs(A - B) <= SNAP_DOUBLE_MIN;
	return snap_fuzzy_is_null(A-B);
}*/
#define __snap_fuzzy_is_equal(A, B) __snap_fuzzy_is_null(A-B)

#define snap_double_modulo fmod
#define snap_double_mod snap_double_modulo


#if defined __STRICT_ANSI__
	#define fmin(x,y) (x < y) ? x : y
	#define fmax(x,y) (x > y) ? x : y

	/* XXX TODO 
	#warning "__STRICT_ANSI__ >> lstat is stat and realpath is passthrough!"
	#define lstat stat
	#define realpath(x, buf)
	*/

#endif



/* https://dustri.org/b/min-and-max-macro-considered-harmful.html
technically this is "wrong" and "bad" because SNAP_MIN(a++, b++) will evaluate each arg twice, but I think that using MIN/MAX that way is "wrong" and "bad", if you don't use fancy statements in your MIN/MAX comparison then all is well
by using SNAP_MIN and SNAP_MAX you agree to the following: "I will not use fancy statements in my calls" */
#define SNAP_MIN(A, B) ((A < B) ? A : B)
#define SNAP_MAX(A, B) ((A > B) ? A : B)
#define SNAP_ABS(NUM) ((NUM < 0) ? NUM * -1 : NUM)


#endif /* __SNAP_MATH_H__ */
