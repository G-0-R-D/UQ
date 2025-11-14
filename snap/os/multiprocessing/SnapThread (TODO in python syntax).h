

// https://www.tutorialspoint.com/multithreading-in-c

// http://man7.org/linux/man-pages/man3/pthread_create.3.html
// https://linux.die.net/man/7/pthreads
// https://linux.die.net/man/3/pthread_mutex_lock

// https://www.youtube.com/watch?v=_n2hE2gyPxU
// https://www.youtube.com/playlist?list=PL9IEJIKnBJjFZxuqyJ9JqVYmuFZHr7CFM
// https://www.youtube.com/watch?v=6Y0NF85cUvk // thread safe via lock, or via memory that is only accessed by one thread...


// XXX TODO the thinking around this is wrong, threads are not subclasses - that just makes a mess!  since data cannot be easily shared between threads...
// threads should be thought of as giving a unique piece of data to the thread (function) to edit, or getting a new piece of data from the thread when complete...
// SnapNodes should simply not be deleted inside a thread (atleast not garbage collected)...   maybe do a thread instance check in SnapNode main, but it just shouldn't be done...
// also I think the rendering engines are usually mainthread only, so don't assign or change graphics inside threads...?
	// maybe just assume that you shouldn't edit the data while it is in the render queue, and only edit it from one thread at a time...
	// https://www.cairographics.org/threaded_animation_with_cairo/
// -- so this should be pretty much what it already was, a start function that takes a callback and void* to data to operate on...
// -- we can make a threadpool
// TODO SnapTimers and global SNAP_ENV() should be threadsafe too?

// TODO queue engine commands from other threads for the 'rendering thread' to process...

#ifndef __SNAP_THREAD_H__
#define __SNAP_THREAD_H__

#include <pthread.h> // posix thread api
//#include <stdatomic.h>
#include <semaphore.h>

// TODO mutex and condition


// the basic rule to keep in mind: you cannot interact with data on both sides of the 'fence' either the data is only touched by one thread or the other, or a mutex prevents the data from being edited at the same time...

#include "snap/SnapNode.h"

#if defined SNAP_DEBUG && (defined SNAP_DEBUG_THREAD || defined SNAP_DEBUG_THREADS)
	#define snap_debug_thread(...) snap_debug
#else
	#define snap_debug_thread(...)
#endif


#define snap_thread_t pthread_t

// https://linux.die.net/man/3/pthread_self
#define snap_thread_id pthread_self

#define snap_threads_equal pthread_equal

pthread_t* __SNAP_MAIN_THREAD__ = NULL; // trying to do this portably is a little tricky since apparently this can be a number, struct, etc...  so allocate when used, deallocate on last thread close...

int snap_thread_is_main(void){
	if (!__SNAP_MAIN_THREAD__ || snap_threads_equal(*__SNAP_MAIN_THREAD__, snap_thread_id())){
		return 1;
	}
	return 0;
}

// TODO make like SnapNode_create, except ENV is ENV_event handler?  the one to initialize the environment for the thread...?
int snap_thread_create(snap_thread_t* THREAD, SnapList ARGS){

	if (!__SNAP_MAIN_THREAD__){
		// as long as threads are created only through this api it will work...
		// a method to know whether we are 'in the main thread' (ie. the thread that started the application -- the first one)
		__SNAP_MAIN_THREAD__ = snap_malloc(sizeof (snap_thread_t));
		if (!__SNAP_MAIN_THREAD__){
			snap_error("unable to allocate main thread!");
			return 0;
		}
		*__SNAP_MAIN_THREAD__ = snap_thread_id();
	}

	// TODO now create

}

int snap_thread_cancel(){
}

// NOTE: best way to implement a threaded process is as an object with 'method' to start the thread and local variables assigned to self.  use a queue for command input or result output (use a "NEXT" that obtains a lock and then yields the next result)


// TODO would it be possible to use the event system to run the thread?  users of the thread would use a unique EVENT?  with lock passed in?
// that way users can join and leave threads more readily, allowing single running threads to be shared easier and more dynamically...  while the threads and api for them are managed by this module?

// OR is subclassing less opaque?


/*
pthread_t pthread_create(
	pthread_t *thread, const pthread_attr_t *attr, void *(*start_routine) (void *), void *arg);
pthread_cancel(pthread_t thread);

pthread_t thread = pthread_self();  // call to find out which thread we are in
int bool = pthread_equal(pthread_t t1, pthread_t t2); // to check ID's are the same (size can change so == is not portable)
*/

static void* __SnapThread_callback(void* thread_args){

	any* data = ((VoidList)thread_args)->data;

	if (pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL) != 0){
		snap_warning("thread unable to enable cancel state!");
	}
	//pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
	pthread_setcanceltype(PTHREAD_CANCEL_DEFERRED, NULL);
	
	return _snap_event((SnapNode*)data[0], data[1], (SnapNode*)data[2]);
}


pthread_t snap_start_thread(SnapNode* self, any EVENT, SnapNode* MSG){
	// recommend using "PROCESS" for event name, but it can be whatever

	if (!(self && *self)){
		snap_error("cannot start thread on NULL!");
		return (any)"ERROR";
	}

	pthread_t thread;

	// https://linux.die.net/man/3/pthread_attr_init
	pthread_attr_t attr;
	pthread_attr_init(&attr);
	// https://stackoverflow.com/questions/22427007/difference-between-pthread-exit-pthread-join-and-pthread-detach
	// so join is to obtain return from thread, detach destroys the thread immediately (what we want)
	pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);

	// TODO use atomic int to signal when to stop?  passed in MSG

	// TODO add thread to args? XXX can always get thread with SnapThread_this_thread();
	SNAPLIST(thread_args, self, EVENT, MSG);
	if (pthread_create(&thread, &attr, __SnapThread_callback, (void*)thread_args) != 0){
		snap_error("unable to create thread!");

		pthread_attr_destroy(&attr);
		return NULL;//(any)"ERROR";
	}

	pthread_attr_destroy(&attr);

	return thread;
}

any snap_stop_thread(pthread_t THREAD){
	// threads should just return to stop but sometimes they might get stuck, so this is meant to stop them immediately

	// pthread_setcancelstate(PTHREAD_CANCEL_ENABLE/DISABLE, NULL) to block this
	if (pthread_cancel(THREAD) != 0){
		snap_error("cancel thread error!");
		return (any)"ERROR";
	}
	return NULL;
}

#define SnapThread_this_thread pthread_self

#define SnapThread_threads_equal pthread_equal



any SnapThread_event(SnapNode* self, any EVENT, SnapNode* MSG){

	if_ID
		return SnapNode_event(self, EVENT, MSG);
	}


	else if (EVENT == (any)"LOCK_ACQUIRE"){

		// https://computing.llnl.gov/tutorials/pthreads/

		// https://stackoverflow.com/questions/12507937/multiple-threads-and-mutexes
		// "you do not need a mutex for each thread. You need a mutex for the critical area."

		// https://linux.die.net/man/3/pthread_mutex_lock TODO if locked by another thread it returns busy error?

		// TODO make a global lock and a local lock?  global lock to lock queue add?

		// XXX TODO threads do not lock themselves, locks are a separate thing,
		// enforce that threads are managed by an object and callback into the object with an event so an object can manage a bunch of threads that share one lock, or use a global lock, or whatever

		pthread_t t = pthread_self();

		pthread_t* existing = (pthread_t*)snap_getattr(self, "__LOCK__");
		if (!existing){
			// assign
		}
		else {
			if (pthread_equal(*existing, t)){
				// increment counter
				return NULL;
			}
			else {
				// wait (add to queue?)
			}

		}

		// TODO use an internal counter and only lock the mutex on the first call?

		// queue the calls?

		//int pthread_mutex_init(pthread_mutex_t *restrict mutex, const pthread_mutexattr_t *restrict attr);
		//int pthread_mutex_lock(pthread_mutex_t *mutex);
		// incr lock int?
		return NULL;
	}

	else if (EVENT == (any)"LOCK_RELEASE"){
		//int pthread_mutex_unlock(pthread_mutex_t *mutex);
		//int pthread_mutex_destroy(pthread_mutex_t *mutex);
		return NULL;
	}

	if (EVENT == (any)"START"){

		// TODO does __running__ need to be atomic?  it will always be changed on one side and checked on the other, never changed from both sides at same time...
		if (snap_getattr(self, "__running__") == (any)"TRUE"){
			snap_warning("thread already running!");
			return NULL;
		}

		snap_assignattr(self, "thread", NULL, sizeof (pthread_t));

		int pthread_idx = SnapNode_find(self, "thread");
		if (pthread_idx < 0){
			snap_error("unable to assign thread!");
			return (any)"ERROR";
		}

		// https://linux.die.net/man/3/pthread_attr_init
		pthread_attr_t attr;
		pthread_attr_init(&attr);
		// https://stackoverflow.com/questions/22427007/difference-between-pthread-exit-pthread-join-and-pthread-detach
		// so join is to obtain return from thread, detach destroys the thread immediately (what we want)
		pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);

		// running is user space for setting state requests, __running__ is internal feedback of what the state actually is
		snap_setattrs(self, "running", "TRUE", "__running__", "TRUE");

		if (pthread_create((pthread_t*)&(*self)->data[pthread_idx], attr, __SnapThread_callback, (void*)self) != 0){
			snap_error("unable to create thread!");
			snap_setattrs(self, "running", NULL, "__running__", NULL);

			pthread_attr_destroy(&attr);
			return (any)"ERROR";
		}

		pthread_attr_destroy(&attr);
		return NULL;
	}
	else if (EVENT == (any)"STOP" || EVENT == (any)"KILL"){

		pthread_t* t = (pthread_t*)snap_getattr(self, "thread");

		if (t && snap_getattr(self, "__running__") == (any)"TRUE"){ // TODO use running status of t directly?
			
			snap_setattr(self, "running", NULL);

			double wait = 2.; // TODO get from MSG?  "wait"
			while (wait > 0 && snap_getattr(self, "__running__") == (any)"TRUE"){
				// wait for thread to see running != TRUE and stop itself
				sleep(.01);
				wait -= .01;
			}
			if (snap_getattr(self, "__running__") == (any)"TRUE"){
				pthread_cancel(t);
			}

			// XXX we don't care about thread return value, so threads are "detached"
			//if (pthread_join(t) != 0){ // instead of join set running and wait for a bit and call cancel if too long?
			//	snap_warning("error on pthread_join");
			//}
		}
		

		return NULL;
	}

	else if (EVENT == (any)"PROCESS"){
		// this is inside thread, implement in subclass

		pthread_t* thread = (pthread_t*)snap_getattr(self, "thread");
		snap_out("inside running thread %p", thread);

		// loop here until finished
		// while (snap_getattr(self, "running") == (any)"TRUE"){
			// do something
		//}

		return NULL;
	}
	
	else if (EVENT == (any)"INIT"){

		if (snap_getattr(self, "running") == (any)"TRUE"){
			snap_warning("thread already running!  cannot init!");
			return NULL;
		}

		SnapNode_event(self, EVENT, MSG);

		// TODO args?

		return NULL;
	}

	else if (EVENT == (any)"DELETE"){
		// https://linux.die.net/man/3/pthread_cancel example at bottom

		// TODO can we protect LISTEN/IGNORE/DELETE with lock on just the threads? XXX GC register would require mutex shared by all threads...

		_snap_event(self, "STOP", MSG);

		snap_delattrs_free(self, "thread");
		snap_delattrs(self,
			"running", "__running__");
	}

	else_if_isinstance(SnapThread_event)

	return SnapNode_event(self, EVENT, MSG);
}




any SnapThreadManager_event(SnapNode* self, any EVENT, SnapNode* MSG){

	// TODO basically runs a single thread, users can send callbacks for lazy tasks to complete, or maybe reserve their own thread for their own tasks
	// does one task at a time until complete (or pushes to end of queue if not complete) and otherwise listens to refresh in main thread and cancels threads that are unresponsive?

	return SnapNode_event(self, EVENT, MSG);
}



SnapNode SnapThread_start(SnapNode* TARGET, any EVENT, SnapNode* MSG){
	// calls _snap_event(TARGET, EVENT, MSG); in new thread and returns new thread instance
	return NULL;
}










#define SnapThreadLock_attrs\
	__threadlock_data__

IDX_DECL(SnapThreadLock);


static typedef struct SnapThreadLock_data_t {
	pthread_mutex_t mutex;
	pthread_t owner;
	int count;
} SnapThreadLock_data_t;


any SnapThreadLock_event(SnapNode* self, any EVENT, SnapNode* MSG){
	// this is a 're-entrant' lock, allowing a thread to acquire lock on itself without blocking
	// for each "ACQUIRE" a "RELEASE" must be called!

	if_ID
		return SnapNode_event(self, EVENT, MSG);
	}

	else if (EVENT == (any)"ACQUIRE"){

		SnapThreadLock_data_t* data = (SnapThreadLock_data_t*)snap_getattr_at(self,
			"__threadlock_data__", IDX_SnapThreadLock___threadlock_data__);
		if (!data){
			snap_warning("no thread lock data!");
			return NULL;
		}

		pthread_t THIS = SnapThread_this_thread();

		if (SnapThread_threads_equal(data->owner, THIS)){
			// this thread already owns the lock, increment count instead
			data->count++;
			return NULL;
		}

		// lock and assign as owner
		if (pthread_mutex_lock(&data->mutex) != 0){
			snap_error("pthread_mutex_lock() error!");
			return (any)"ERROR"; // ?? exit?  would have to check for error or yikes!
		}
		data->owner = THIS; // NOTE: assigned after the mutex is acquired
		data->count++; // assumed it was 0?  it shouldn't be released if not 0...

		return NULL;
	}

	else if (EVENT == (any)"RELEASE"){
		
		SnapThreadLock_data_t* data = (SnapThreadLock_data_t*)snap_getattr_at(self,
			"__threadlock_data__", IDX_SnapThreadLock___threadlock_data__);
		if (!data){
			snap_warning("no thread lock data!");
			return NULL;
		}

		pthread_t THIS = SnapThread_this_thread();

		if (!SnapThread_threads_equal(data->owner, THIS)){
			// only releases (or does anything at all) if this thread is the owner of the lock!
			return NULL;
		}

		if (data->count > 0){
			data->count--;
			return NULL;
		}
		
		//pthread_t owner = data->owner;
		data->owner = NULL;
		data->count = 0; // sanity

		int err = pthread_mutex_unlock(&data->mutex);
		if (err != 0){
			snap_error("pthread_mutex_unlock() error %d \"%s\"", err, strerror(err));
			//data->owner = owner; // ??
			return (any)"ERROR";
		}

		return NULL;

	}

	if_ID
		return SnapNode_event(self, EVENT, MSG);
	}

	else if (EVENT == (any)"INIT"){
		SnapNode_event(self, EVENT, MSG);

		IDX_RESERVE(SnapThreadLock);
		if (IDX_SnapThreadLock___threadlock_data__ < 0)
			IDX_UPDATE(SnapThreadLock);

		if (snap_getattr_at(self, "__threadlock_data__", IDX_SnapThreadLock___threadlock_data__)){
			snap_warning("ThreadLock already initialized!");
			return NULL;
		}

		SnapThreadLock_data_t* data = (SnapThreadLock_data_t*)snap_malloc(sizeof (SnapThreadLock_data_t));
		data->mutex = NULL;
		data->owner = NULL;
		data->count = 0;

		int err = pthread_mutex_init(&data->mutex, NULL);
		if (err != 0){
			snap_error("unable to initialize mutex! %d \"%s\"", err, strerror(err));
			snap_free(data);
			snap_event(self, "DELETE");
			return (any)"ERROR";
		}

		snap_setattr_at(self, "__threadlock_data__", data);

		return NULL;
	}

	else if (EVENT == (any)"DELETE"){

		// how about start with snap_event(self, "ACQUIRE"); ??

		SnapThreadLock_data_t* data = (SnapThreadLock_data_t*)snap_getattr_at(self,
			"__threadlock_data__", IDX_SnapThreadLock___threadlock_data__);
		if (data){
			int err;
			if (data->owner){
				snap_warning("SnapThreadLock delete while still in use!");
				if (!SnapThread_threads_equal(SnapThread_this_thread(), data->owner)){
					snap_error("this thread does not own the mutex and cannot release it!  deletion aborted!");
					return (any)"ERROR";
				}
				err = pthread_mutex_unlock(&data->mutex);
				if (err != 0){
					snap_error("unable to release mutex! %d \"%s\"", err, strerror(err));
				}
			}

			err = pthread_mutex_destroy(&data->mutex);
			if (err > 0){
				snap_error("error deleting mutex but proceeding with delete %d \"%s\"", err, strerror(err));
			}

			snap_free(data);
		}
		snap_delattr_at(self, "__threadlock_data__", IDX_SnapThread___threadlock_data__);
	}

	return SnapNode_event(self, EVENT, MSG);
}




// TODO make a bridge api that holds a reference to a thread instance, which acquires a lock (global or locally assigned) on event, forwards the event, and unlocks -- same with emits, forwards them as self ID...
// on delete it would have to clean itself up too...  or just do that when child disappears?
	// TODO another approach would be to just make a wrapper around the data you want access to, which acquires the lock, possibly sharing a lock with multiple data...





any SnapThreadTest_event(SnapNode* self, any EVENT, SnapNode* MSG){

	if_ID
		return SnapNode_event(self, EVENT, MSG);
	}

	else if (EVENT == (any)"PROCESS_THREAD"){

		

		return NULL;
	}

	else if (EVENT == (any)"INIT"){
		SnapNode_event(self, EVENT, MSG);


		

		return NULL;
	}

	else if (EVENT == (any)"DELETE"){
	}

	return SnapNode_event(self, EVENT, MSG);
}





void SnapThread_run_test(void){
	
	snap_out("SnapThread_run_test()");

	SnapNode tester = SnapNode_create(SnapThreadTest_event);

	snap_event(&tester, "DELETE");

}


#endif
