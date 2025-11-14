
#from snap.core.snap_debugging import *
import os, sys, time, fcntl

def build(ENV):

	# https://note.nkmk.me/en/python-sys-float-info-max-min/
	# "in python 3 float has same precision as double in c"
	# -- also int is unlimited
	ENV.SNAP_DOUBLE_MAX = sys.float_info.max
	ENV.SNAP_DOUBLE_MIN = sys.float_info.min

	"""
	#ifndef SNAP_MATH_PI
		#ifdef M_PI
			#define SNAP_MATH_PI M_PI
		#else
			#define SNAP_MATH_PI 3.14159265358979323846
		#endif
	#endif
	"""
	ENV.SNAP_MATH_PI = 3.14159265358979323846 # TODO

	#define snap_fuzzy_is_null(NUM) ((NUM >= -SNAP_DOUBLE_MIN && NUM <= SNAP_DOUBLE_MIN) ? 1:0)
	def snap_fuzzy_is_null(NUM):
		return NUM >= -SNAP_DOUBLE_MIN and NUM <= SNAP_DOUBLE_MIN
	ENV.snap_fuzzy_is_null = snap_fuzzy_is_null

	#int snap_fuzzy_is_equal(double A, double B){
	#	//return fabs(A - B) <= SNAP_DOUBLE_MIN;
	#	return snap_fuzzy_is_null(A-B);
	#}
	def snap_fuzzy_is_equal(A, B):
		return snap_fuzzy_is_null(A-B)
	ENV.snap_fuzzy_is_equal = snap_fuzzy_is_equal

	# TODO
	#define snap_double_modulo fmod
	#define snap_double_mod snap_double_modulo

	#SNAP_MIN = min
	#SNAP_MAX = max
	#SNAP_ABS = abs


	"""
	def SNAP_INIT(self, SETTINGS, *names, **defaults):
		setts = {name:SETTINGS[name] for name in names if name in SETTINGS}
		if defaults:
			setts.update({k:SETTINGS.get(k,v) for k,v in defaults.items()})
		if setts:
			self.__snap_input__("set", SnapMessage(**setts))
	ENV.SNAP_INIT = SNAP_INIT
	"""


	# TIME TODO

	THE_TIME = time.time

	def snap_time_since_epoch():
		# https://stackoverflow.com/questions/2844/how-do-you-format-an-unsigned-long-long-int-using-printf
		# https://stackoverflow.com/questions/10192903/time-in-milliseconds-in-c by zebo zhuang (scroll down)

		# epoch: January 1, 1970 @ 12:00am (UTC)
		return THE_TIME()
	ENV.snap_time_since_epoch = snap_time_since_epoch

	def snap_time():
		return snap_time_since_epoch()# - ENV.__SNAP_MAINLOOP__._start_time_
		"""
		t = PRIVATE['SNAP_START_TIME']
		if t < 0:
			t = PRIVATE['SNAP_START_TIME'] = snap_time_since_epoch()
			#snap_out("set snap app time %lf" % SNAP_START_TIME)

		# this is the time in seconds since application start, rather than an arbitrary date in the 1970's
		#snap_out("epoch time %lf", snap_time_since_epoch());
		return snap_time_since_epoch() - t
		"""
	ENV.snap_time = snap_time

	def snap_sleep(seconds):
		#https://stackoverflow.com/questions/1157209/is-there-an-alternative-sleep-function-in-c-to-milliseconds
		#http://man7.org/linux/man-pages/man2/nanosleep.2.html

		if seconds <= 0.0:
			return

		time.sleep(seconds) # TODO?
		"""
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
		ts.tv_nsec = (long)((seconds- (snap_float_t)ts.tv_sec) * 1000000000.0);
		nanosleep(&ts, NULL); // second argument is remaining time if interrupted...?
	#else
		struct timeval tv;
		tv.tv_sec = (time_t)seconds; // MS / 1000;
		tv.tv_usec = (suseconds_t)((seconds - (snap_float_t)tv.tv_sec) * 1000.0);
		select(0, NULL, NULL, NULL, &tv); // more universally compatible than usleep
		//usleep(seconds);
	#endif
		"""
	ENV.snap_sleep = snap_sleep




	SAVED_FD = [-1, 0] # (FD, FLAGS)
	DEVNULL = [-1]

	# https://stackoverflow.com/questions/5081657/how-do-i-prevent-a-c-shared-library-to-print-on-stdout-in-python
	# https://stackoverflow.com/questions/14846768/in-c-how-do-i-redirect-stdout-fileno-to-dev-null-using-dup2-and-then-redirect
	# https://dzone.com/articles/redirecting-all-kinds-stdout # redirecting c calls from python
	# TODO make this python context manager that also works for c?  then snap encoder can generate it...
	def snap_redirect_out_cancel():
		#print('saved fd', SAVED_FD)
		if SAVED_FD[0] > -1:

			# TODO flush previous FD first?

			os.dup2(SAVED_FD[0], sys.stdout.fileno())
			#snap_out("saved fd %d saved flags %d", __SNAP_SAVED_FD, __SNAP_SAVED_FD_FLAGS);
			#fflush(__SNAP_SAVED_FD);
			os.close(SAVED_FD[0]) # dup() returns another fd that needs closing?
			SAVED_FD[0] = -1

			#snap_out("before %p", SNAP_OUT);
			#SNAP_OUT = fdopen(fileno(SNAP_OUT), "w");
			#snap_out("after %p", SNAP_OUT);
			fcntl.fcntl(sys.stdout.fileno(), fcntl.F_SETFD, SAVED_FD[-1])
			SAVED_FD[-1] = 0
	ENV.snap_redirect_out_cancel = snap_redirect_out_cancel

	def snap_devnull():
		if DEVNULL[0] < 0:
			DEVNULL[0] = os.open("/dev/null", os.O_RDWR)
		return DEVNULL[0]
	ENV.snap_devnull = snap_devnull

	def snap_close_devnull():
		if DEVNULL[0] > -1:
			os.close(DEVNULL[0])
			DEVNULL[0] = -1
			return True
		return False
	ENV.snap_close_devnull = snap_close_devnull

	def snap_redirect_out(FD):
		snap_redirect_out_cancel()

		#fflush(SNAP_OUT);

		SAVED_FD[0] = os.dup(sys.stdout.fileno())
		#print("saved fd os.dup", SAVED_FD);
		SAVED_FD[-1] = fcntl.fcntl(SAVED_FD[0], fcntl.F_GETFD)
		#close(fileno(SNAP_OUT))
		#print("saved fd", SAVED_FD)
		os.dup2(FD, sys.stdout.fileno())
	ENV.snap_redirect_out = snap_redirect_out

	def snap_silence_begin():
		snap_redirect_out(snap_devnull())
	ENV.snap_silence_begin = snap_silence_begin

	def snap_silence_end():
		snap_redirect_out_cancel()
		#snap_close_devnul(); // done in snap_finished()?
	ENV.snap_silence_end = snap_silence_end




	def snap_raw(*args, **kwargs):
		# XXX deprecated, thinking of strings that start with "snapc:..." or something...
		# this is just a way for compatibility with python and snap, this tells the snap compiler to leave the string(s) 'as is' or raw()
		# which allows typing c code directly (if compiling into c), while in python you could branch into using a ctypes api or something else, so the code compiles in both when interfacing with c...
		return
	ENV.snap_raw = snap_raw

	def snap_item_in_list(LIST, ITEM):
		if LIST is None or len(LIST) < 1: return False
		return snap_binary_search_core(
			LIST,
			id(ITEM),
			L=0, R=len(LIST)-1,
			compare=snap_binary_search_compare_address,
			run_to_end=False
			) > -1
	ENV.snap_item_in_list = snap_item_in_list

	# TODO we can make an 'item_in_list(LIST, ITEM)' search for sorted lists, for in tests, using id()
	# with compare_address() callback

	def snap_sort(LIST, L=None, R=None, key=None, compare=None, allow_duplicates=False, extra_data=None):
		# TODO do compare with class wrapping compare callback -- would require wrapping each item...  and duplicating 
		raise NotImplementedError()
	ENV.snap_sort = snap_sort

