
#ifndef __SNAP_DEBUG_H__
#define __SNAP_DEBUG_H__

#include "snap_sys.h"

/* TODO print functions, and where to put the execution stack */

#ifndef SNAP_STDOUT
	#define SNAP_STDOUT stderr
#endif
#define SNAP_STDERR SNAP_STDOUT // TODO distinguish STDOUT and STDERR

/* TODO apparently printing "%s", (char*)NULL is a problem:
 https://riptutorial.com/c/example/13658/passing-a-null-pointer-to-printf--s-conversion
 so may need to scan for all unescaped (%%) %, and then if %s, replace with "(null)" string in the list instead of what was provided by caller...

 https://stackoverflow.com/questions/15305310/predefined-macros-for-function-name-func
NOTE: simulating function calls for python api compat...  but they aren't calls!
XXX the compiler can do the text replace, but these need to be turned into SnapStrings! */
#define SNAP_FILENAME() __FILE__
#define SNAP_FUNCNAME() __func__
#define SNAP_LINE() __LINE__

/* TODO logging to file option */
#ifndef SNAP_SILENT /* TODO SNAP_OPT_SILENT */

	#define __SNAP_OUT(STR, ...){\
		fprintf(SNAP_STDOUT, "\033[92m[%d] %s|%s() >> \033[0m", SNAP_LINE(), SNAP_FILENAME(), SNAP_FUNCNAME());\
		fprintf(SNAP_STDOUT, STR, ##__VA_ARGS__);\
		fprintf(SNAP_STDOUT, "\n");\
		fflush(SNAP_STDOUT);\
	}


	#define __SNAP_WARNING(STR, ...){\
		fprintf(SNAP_STDOUT, "\033[93m[%d] %s|%s() >> \033[0m", SNAP_LINE(), SNAP_FILENAME(), SNAP_FUNCNAME());\
		fprintf(SNAP_STDOUT, STR, ##__VA_ARGS__);\
		fprintf(SNAP_STDOUT, "\n");\
		fflush(SNAP_STDOUT);\
	}

	#define __SNAP_ERROR(STR, ...){\
		fprintf(SNAP_STDOUT, "\033[91m[%d] %s|%s() >> \033[0m", SNAP_LINE(), SNAP_FILENAME(), SNAP_FUNCNAME());\
		fprintf(SNAP_STDOUT, STR, ##__VA_ARGS__);\
		fprintf(SNAP_STDOUT, "\n");\
		fflush(SNAP_STDOUT);\
	}

	#define __SNAP_PRINT(STR, ...){\
		fprintf(SNAP_STDOUT, STR, ##__VA_ARGS__);\
		fprintf(SNAP_STDOUT, "\n");\
		fflush(SNAP_STDOUT);\
	}

	#define __SNAP_RAWPRINT(STR, ...){\
		fprintf(SNAP_STDOUT, STR, ##__VA_ARGS__);\
	}

#else

	#define __SNAP_OUT(...)
	#define __SNAP_WARNING(...)
	#define __SNAP_ERROR(...)
	#define __SNAP_PRINT(...)
	#define __SNAP_RAWPRINT(...)

#endif

/*#define snap_raw_out snap_rawprint*/
/*#define snap_raw_print snap_rawprint*/


#ifdef SNAP_DEBUG
	#define __SNAP_DEBUG(STR, ...){\
		fprintf(SNAP_STDOUT, "\033[94m[%d] %s|%s() >> \033[0m", __SNAP_LINE(), __SNAP_FILENAME(), __SNAP_FUNCNAME());\
		fprintf(SNAP_STDOUT, STR, ##__VA_ARGS__);\
		fprintf(SNAP_STDOUT, "\n");\
		fflush(SNAP_STDOUT);\
	}
#else
	#define __SNAP_DEBUG(...)
#endif

/* used for assertion style testing, see SnapList_run_test()*/
/* TODO #ifndef SNAP_TEST_OUT_ERROR_ONLY (and only print test out on fail)*/
/* maybe also halt on fail option?*/
#define __SNAP_TEST_OUT(TEST)({\
	int success = 0;\
	if (TEST){\
		__SNAP_OUT("\n\t[\033[92mTEST OK\033[0m] %s", #TEST);\
		success = 1;\
	}\
	else {\
		__SNAP_ERROR("\n\t[\033[91mTEST FAIL\033[0m] %s", #TEST);\
	}\
	/*snap_out("[%s] %s", (TEST) ? "\033[92mOK\033[0m":"\033[91mFAIL\033[0m", #TEST)*/\
	success;\
})



/* TODO __SNAP_RAISE */



#endif /* __SNAP_DEBUG_H__ */
