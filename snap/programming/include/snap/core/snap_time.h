#ifndef __SNAP_TIME_H__
#define __SNAP_TIME_H__


/*/////////////////// TIME STUFF //////////////////////*/

#include <sys/time.h> /* gettimeofday() */

#ifdef WIN32
	#include <windows.h>
#elif _POSIX_C_SOURCE >= 199309L
	#include <time.h>   // for nanosleep
/*#else
#include <unistd.h> // for usleep? */
#endif

/*
typedef long long int snap_milliseconds_t; // as milliseconds (so seconds is /1000 or * 0.001, one thousandth)
#define snap_millisecs_t snap_milliseconds_t
#define snap_ms_t snap_millisecs_t

/* https://stackoverflow.com/questions/2844/how-do-you-format-an-unsigned-long-long-int-using-printf */
/* https://stackoverflow.com/questions/10192903/time-in-milliseconds-in-c by zebo zhuang (scroll down) */
/*snap_ms_t snap_get_timeXXX(){
#if defined NOTDEFINEDKTHXBYE //_POSIX_TIMERS // high resolution nanoseconds available
	https://stackoverflow.com/questions/6749621/how-to-create-a-high-resolution-timer-in-linux-to-measure-program-performance
	http://www.guyrutenberg.com/2007/09/22/profiling-code-using-clock_gettime/
	struct timespec tv;
	clock_gettime(CLOCK_REALTIME, &tv); // or CLOCK_PROCESS_CPUTTIME_ID ?
	
	return (((snap_ms_t)tv.tv_sec) * 1000) + (tv.tv_nsec / 1000000);
#else
	struct timeval tv;
    gettimeofday(&tv,NULL);
    return (((snap_ms_t)tv.tv_sec) * 1000) + (tv.tv_usec / 1000); // ?
#endif
}
*/

/* https://stackoverflow.com/questions/9772348/get-absolute-value-without-using-abs-function-nor-if-statement */
/*
snap_ms_t snap_millisecs_abs(snap_ms_t value){
	snap_ms_t ret[2] = { value, -value };
    return ret[ value < 0 ];
}

void snap_sleep_millisecs(snap_ms_t MS){

}
#define snap_sleep_ms snap_sleep_millisecs
*/




double __SNAP_START_TIME = -1;

double __SNAP_TIME_SINCE_EPOCH(void){

	/* https://stackoverflow.com/questions/2844/how-do-you-format-an-unsigned-long-long-int-using-printf */
	/* https://stackoverflow.com/questions/10192903/time-in-milliseconds-in-c by zebo zhuang (scroll down) */

	/* epoch: January 1, 1970 @ 12:00am (UTC) */
#if defined _POSIX_TIMERS /* high resolution nanoseconds available*/
	/*https://stackoverflow.com/questions/6749621/how-to-create-a-high-resolution-timer-in-linux-to-measure-program-performance*/
	/*http://www.guyrutenberg.com/2007/09/22/profiling-code-using-clock_gettime/*/
	struct timespec tv;
	clock_gettime(CLOCK_REALTIME, &tv); // or CLOCK_PROCESS_CPUTTIME_ID ?
	/*snap_out("\n\tsec %lf\n\tnsec %lf %.15lf", (double)tv.tv_sec, (double)tv.tv_nsec, (double)tv.tv_nsec / 1000000000.0);*/
	return (double)tv.tv_sec + ((double)tv.tv_nsec / 1000000000.0);
#else
	struct timeval tv;
    gettimeofday(&tv, NULL);
	/*snap_out("\n\tsec %lf\n\tusec %lf %lf", (double)tv.tv_sec, (double)tv.tv_usec, (double)tv.tv_usec / 1000.0);*/
    return (double)tv.tv_sec + ((double)tv.tv_usec / 1000.0);
#endif
}

double __SNAP_TIME(void){
	if (__SNAP_START_TIME < 0){
		__SNAP_START_TIME = __SNAP_TIME_SINCE_EPOCH();
		/*snap_out("set snap app time %lf", SNAP_START_TIME);*/
	}
	/* this is the time in seconds since application start, rather than an arbitrary date in the 1970's*/
	/*snap_out("epoch time %lf", snap_time_since_epoch());*/
	return __SNAP_TIME_SINCE_EPOCH() - __SNAP_START_TIME;
}


void __SNAP_SLEEP(double seconds){
	/*https://stackoverflow.com/questions/1157209/is-there-an-alternative-sleep-function-in-c-to-milliseconds*/
	/*http://man7.org/linux/man-pages/man2/nanosleep.2.html*/

	if (seconds <= 0.0)
		return;

		/*
	struct timespec {
	   time_t tv_sec;	//seconds
	   long   tv_nsec;	//nanoseconds
	};
	*/
#ifdef WIN32
	Sleep(seconds);
#elif _POSIX_C_SOURCE >= 199309L
	struct timespec ts;
	ts.tv_sec = (time_t)seconds;
	ts.tv_nsec = (long)((seconds- (double)ts.tv_sec) * 1000000000.0);
	nanosleep(&ts, NULL); /* second argument is remaining time if interrupted...?*/
#else
	struct timeval tv;
	tv.tv_sec = (time_t)seconds; /* MS / 1000;*/
	tv.tv_usec = (suseconds_t)((seconds - (double)tv.tv_sec) * 1000.0);
	select(0, NULL, NULL, NULL, &tv); /* more universally compatible than usleep*/
	/*usleep(seconds);*/
#endif
}


#endif /* __SNAP_TIME_H__ */
