
from fcntl import fcntl, F_GETFL, F_SETFL

import shlex

import sys

from os import (

	O_NONBLOCK,
	O_RDWR,

	WNOHANG,
	WUNTRACED,
	WCONTINUED,
	WIFEXITED,
	WEXITSTATUS,
	WIFSIGNALED,
	WIFSTOPPED,

	waitpid,
	kill,
	fork,
	pipe,
	read,
	write,
	fdopen,
	close,
	dup2,

	execvp,

	)

from signal import (
	# TODO ENV start should catch SystemExit, KeyboardInterrupt, etc... and emit through ENV to be handled?  then subprocess can always shutdown properly...
	SIGSTOP,
	SIGCONT,
	SIGTERM,
	SIGKILL,
)

def build(ENV):

	SnapNode = ENV.SnapNode

	snap_time = ENV.snap_time
	snap_sleep = ENV.snap_sleep

	snap_devnull = ENV.snap_devnull

	def _SnapSubprocess_set_fd_options(FD, **SETTINGS):
		# https://stackoverflow.com/a/1549344
		if FD < 0:
			raise TypeError("FD < 0", FD)

		BLOCKING = False

		for attr,value in SETTINGS.items():
			if attr == 'blocking': BLOCKING = bool(value)
			else: ENV.snap_warning(ENV.SNAP_FUNCNAME(), "unknown attr", repr(attr))

		flags = fcntl(FD, F_GETFL, 0)
		if flags < 0:
			raise ValueError("invalid flags for FD", flags, FD)

		#if BLOCKING:
		flags = (flags & ~O_NONBLOCK) if BLOCKING else (flags | O_NONBLOCK)

		if fcntl(FD, F_SETFL, flags) != 0:
			raise IOError("unable to set flags for FD", flags, FD)

		return None

	def SnapSubprocess_send_signal(PID, SIGNAL):
		# XXX deprecated, user api will use strings for signals and remap them
		# https://linux.die.net/man/2/kill
		"""
		"The kill() system call can be used to send any signal to any process group or process."

		If pid is positive, then signal sig is sent to the process with the ID specified by pid.

		If pid equals 0, then sig is sent to every process in the process group of the calling process.

		If pid equals -1, then sig is sent to every process for which the calling process has permission to send signals, except for process 1 (init), but see below.

		If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid.

		If sig is 0, then no signal is sent, but error checking is still performed; this can be used to check for the existence of a process ID or process group ID. 
		"""

		# scary name; "kill" should really just be called "send"
		#try:
		kill(PID, SIGNAL)
		#except OSError as e:
		#assert err == 0, "{}".format([PID, SIGNAL, err, os.strerror(err)])

		return None



	def _SnapSubprocess_set_and_save_env(RESTORE_ENV, ENV):

		# NOTE: all entries will need to be duplicated, since they will be invalid once unset...

		"""
		for_attr_in_SnapNode(&ENV)

			if (!value){
				// remove from env
			}
		}
		"""

		return None

	def _SnapSubprocess_restore_env(RESTORE_ENV):

		# if no value then unsetenv
		# otherwise setenv

		return None
			

	class SnapSubprocess(SnapNode):

		__slots__ = []#'_returncode_', '_pid_', '_pipes_', '_clean_pipes_', '_status_']

		@ENV.SnapProperty
		class pid:

			def get(self, MSG):
				"""()->int"""
				pid = self.__snap_data__['pid']
				if pid is None:
					return -1
				return pid

		@ENV.SnapProperty
		class pipes:

			def get(self, MSG):
				"""()->list(3 * int)"""
				pipe_info = self.__snap_data__['__pipe_info__']
				if pipe_info is None:
					return [-1, -1, -1]
				else:
					return pipe_info['pipes']

		@ENV.SnapProperty
		class status:

			def get(self, MSG):
				"""()->int"""
				status = self.__snap_data__['status']
				if status is None:
					return -1
				return status

		@ENV.SnapProperty
		class returncode:

			def get(self, MSG):
				"""()->int"""
				# None returncode means not finished, otherwise 0 is okay and anything else is an error
				return self.__snap_data__['returncode']

		@returncode.shared
		class exitcode: pass

		@ENV.SnapProperty
		class processing:

			def get(self, MSG):
				"""()->bool"""
				return self['running']


		# TODO make stdout, stderr, stdin properties?  or channels?  channels...  their status is set on __init__

		@ENV.SnapProperty
		class running:

			def get(self, MSG):
				"""()->bool"""
				# https://support.sas.com/documentation/onlinedoc/sasc/doc/lr2/waitpid.htm
				#SnapSubprocess_data_t* data = (SnapSubprocess_data_t*)snap_getattr_at(self, "SnapSubprocess_data_t", IDX_SnapSubprocess_SnapSubprocess_data_t);

				# TODO use a threadlock?

				# TODO should this just verify pid > -1 and then jump to waitpid?  if that fails THEN it checks returncode attr assigned?

				_return = self.poll()

				PID = self['pid']

				data = self.__snap_data__

				if not _return and PID > -1 and self['returncode'] is None:

					# once returncode is set assume not running any more
					# https://stackoverflow.com/questions/5278582/checking-the-status-of-a-child-process-in-c
					# https://www.youtube.com/watch?v=DiNmwwQWl0g
					# https://linux.die.net/man/2/wait

					# https://linux.die.net/man/2/waitpid

					#int status;
					pid,data['status'] = waitpid(PID, WNOHANG|WUNTRACED|WCONTINUED)
					if pid == 0: # || pid == pid:
						# snap_out("still running %d", pid)
						return True

					else:

						if pid == PID and WIFEXITED(self['status']):
							ENV.snap_out("process terminated")

						#if (pid == -1){
						#	snap_error("waitpid return (%d) \"%s\"", pid, strerror(errno));
						#}

						ENV.snap_out("complete with status({}) pid({}) pid({})".format(self['status'], pid, PID))
						# no longer running, update status and set returncode
						# example here: https://linux.die.net/man/2/wait
						returncode = -1
						if WIFEXITED(self['status']):
							# application has exited normally (completed, not terminated)
							returncode = WEXITSTATUS(self['status'])
							if returncode != 0:
								ENV.snap_warning("error in subprocess call! returncode", returncode)

						# https://linux.die.net/man/2/sigaction
						elif WIFSIGNALED(self['status']):
							# WTERMSIG(data->status);
							# WCOREDUMP(data->status);
							# printf("killed by signal %d\n", WTERMSIG(data->status));
							pass

						elif WIFSTOPPED(self['status']):
							# WSTOPSIG(data->status);
							#printf("stopped by signal %d\n", WSTOPSIG(data->status));
							pass

						elif WIFCONTINUED(self['status']):
							# don't really need this I guess but nice to know it's there
							pass

						else:
							ENV.snap_warning("unknown status", self['status'])

						data['returncode'] = returncode

				return _return

		@ENV.SnapProperty
		class finished:

			def get(self, MSG):
				"""()->bool"""
				return not self['running']


		@ENV.SnapChannel
		def next(self, MSG):
			"()"

			# TODO make this the non-blocking one, make communicate() blocking so it behaves the way it did in python...

			# for now just use this one for immediate comms...

			return SnapSubprocess.communicate(self, MSG)

		@ENV.SnapChannel
		def communicate(self, MSG):#stdin=None, **SETTINGS):
			"""(stdin=bool?, buffer_size=int?)"""

			stdin,buffer_size = MSG.unpack('stdin', None, 'buffer_size', 4096)

			"""
			// XXX replace with "PROCESS" and assign IOs to self (works better because they need somewhere to go anyway)

			// TODO pass SnapBytesIO as both "read"|"input" or "write"|"output"?  read/write into internal buffers from user first?
			// TODO also support assigning the SnapBytesIO locally, just like SnapCurlResponse does... (send to args, send to local) -- after reading/writing into pre-allocated local buffers...

			// TODO use SnapBytesIO, pass in "write" IO if applicable, and returns locally assigned "read" IO (which can be pre-assigned for a custom behaviour...?)
			// NOTE: NULL return does not mean finished; check "finished" property to know
			// TODO make a special SnapBytesIOReuseable class that adds an internal size, and reallocates only when size becomes larger...  up to a limit?
			// or have optional seek position?
			// TODO also rename to "NEXT"?
			// XXX just use a SnapString, and set fresh and return new each time?  maybe track it's actual size?
			// TODO what if write buffer can't be handled?  how to communicate that if it's an IO?

			// stdout and stderr and their sizes are designated by user, if they aren't provided but are in use, warn
			// TODO overwrite the sizes with the actual (-1 if errored or N/A)

			// stdin goes to pipe, out and err read from pipes
			// also give feedback if not all is used?  -1 if error or N/A
			"""

			"""
			SNAPLIST(user_buffers, NULL, NULL, NULL); // (char**) for stdin, stdout, stderr
			SNAPLIST(user_sizes, NULL, NULL, NULL); // (snap_int*) sizes for stdin, stdout, stderr buffers

			{for_attr_in_SnapNode(MSG)

				if (attr == (any)"stdin" || attr == (any)"stdin_buffer") user_buffers->data[0] = value;
				else if (attr == (any)"stdout" || attr == (any)"stdout_buffer") user_buffers->data[1] = value;
				else if (attr == (any)"stderr" || attr == (any)"stderr_buffer") user_buffers->data[2] = value;

				else if (attr == (any)"stdin_size") user_sizes->data[0] = value;
				else if (attr == (any)"stdout_size") user_sizes->data[1] = value;
				else if (attr == (any)"stderr_size") user_sizes->data[2] = value;

				else SNAP_UNKNOWN_ATTR;
			}}
			"""

			# TODO blocking option to consume all buffers until process has completed? XXX it's better to leave that to the user, it's just a simple loop anyway!

			_return = [0, None, None] # [<stdin write size>, <stdout buffer>, <stderr buffer>]

			#if not self.running():
			#	return _return

			# since we set the pipes to be non-blocking we shouldn't need to use select...

			#ENV.snap_out("communicate start")

			if stdin is not None:
				# stdin
				# https://linux.die.net/man/2/write
				_return[0] = write(pipe, stdin)
					#pipe, user_buffers->data[i], (size_t)*(snap_int*)user_sizes->data[i]);
				if _return[0] < 0:
					ENV.snap_warning("write error")

				#if (*(snap_int*)user_sizes->data[i] < 0){
				#	snap_warning("[%d] write error(%d) \"%s\"", i, errno, strerror(errno));
				#}

			pipes = self['pipes']
			idx = 0 # will start at 1
			while idx < 2:
				idx += 1

				pipe = pipes[idx]

				if pipe < 0:
					continue

				# stdout, stderr
				# https://linux.die.net/man/2/read
				# https://www.geeksforgeeks.org/python-os-read-method/
				#ENV.snap_out("reading pipe", idx)
				try:
					_return[idx] = read(pipe, buffer_size)
					#ENV.snap_out('read pipe', pipe, idx)
				except BlockingIOError:
					''#ENV.snap_out('pipe not ready', idx)

			#ENV.snap_out("communicate complete")

			# TODO don't return size of in, assign that to a local or something?  just return stdout,stderr like python does

			return _return[1:]

		@ENV.SnapChannel
		def poll(self, MSG):
			# returns TRUE if running XXX can we query the subprocess directly?  pid?
			# https://man7.org/linux/man-pages/man2/kill.2.html
			# "If sig is 0, then no signal is sent, but ... checks are still performed;
			# this can be used to check for the existence of a process ID..."

			try:
				pid = self['pid']
				assert pid > -1 and kill(pid, 0)
				return True
			except:
				return False

		@ENV.SnapChannel
		def wait(self, MSG):#timeout=None, sleep_interval=None):
			# wait until timeout or until process is done

			timeout,sleep_interval = MSG.unpack('timeout',None, 'sleep_interval',None)

			if sleep_interval is None:
				sleep_interval = .01

			if timeout is not None:
				timeout = snap_time() + timeout
				while self['running'] and snap_time() < timeout:
					snap_sleep(sleep_interval)

			else:
				while self['running']:
					snap_sleep(sleep_interval)

			return None

		@ENV.SnapChannel
		def pause(self, MSG):

			pid = self['pid']
			assert pid > -1, 'cannot pause; invalid pid {}'.format(pid)

			if self['running']:
				kill(pid, SIGSTOP)
				return True

			return False # indicates already paused

		@ENV.SnapChannel
		def resume(self, MSG):

			pid = self['pid']
			assert pid > -1, 'cannot resume; invalid pid {}'.format(pid)

			if not self['running']:
				kill(pid, SIGCONT)
				self.__snap_data__['returncode'] = None # ?
				return True

			return False # cannot resume



		def _shutdown(self, MODE):
			# NOTE: MODE will be the method used

			# TODO check pid > -1?  or _returncode_ is None?

			#if self._pid_ > -1 and self._returncode_ is None:
			#	ENV.snap_debug('process already shutdown?')
			#	return True

			PID = self['pid']

			if PID > -1:

				if MODE == 'TERMINATE':
					kill(PID, SIGKILL)
				else:
					# try gentle shutdown
					kill(PID, SIGTERM)

				timeout = snap_time() + .5
				while self['running'] and snap_time() < timeout:
					# waitpid is called by running()
					snap_sleep(.01)

				if self['running']:
					ENV.snap_error('unable to terminate subprocess {}'.format(PID))

			self.__snap_data__['pid'] = None


			pipe_info = self.__snap_data__['__pipe_info__']
			if pipe_info:

				pipes = pipe_info['pipes']
				clean_pipes = pipe_info['clean_pipes']

				i = 0
				while i < 3:

					if clean_pipes[i] and pipes[i] > -1:
						try:
							close(pipes[i])
						except Exception as e:
							ENV.snap_error("unable to close pipe", i, pipes[i], ENV.snap_exception_info(e))
					clean_pipes[i] = False
					pipes[i] = -1

					i += 1

					# TODO if close: cleanup args and env?

			return True

		def stop(self):
			return self._shutdown('STOP')

		def terminate(self):
			return self._shutdown('TERMINATE')

		def close(self):
			return self._shutdown('CLOSE')



		def send_signal(self, SIGNAL):
			# TODO use strings for signals, remap to os signals...
			assert self._pid_ > -1, 'invalid pid {}'.format(self._pid_)
			assert isinstance(SIGNAL, str), 'user api uses strings for signal identities'
			#return SnapSubprocess_send_signal(self._pid_, SIGNAL)
			#kill(self._pid_, remap[SIGNAL])
			raise NotImplementedError()

		@ENV.SnapChannel
		def start(self, MSG):#COMMAND, **SETTINGS):

			COMMAND = MSG.unpack('command',None)

			self.close()

			if isinstance(COMMAND, str):
				COMMAND = shlex.split(COMMAND)
			elif isinstance(COMMAND, (tuple,list)):
				pass # ok
			else:
				raise TypeError('command must be string or tuple/list of strings', type(COMMAND))

			data = self.__snap_data__

			data['returncode'] = None

			data['pid'] = -1

			data['__pipe_info__'] = pipe_info = {
				'pipes':[-1] * 3,
				'clean_pipes':[False] * 3,
			}
			pipes = pipe_info['pipes']
			clean_pipes = pipe_info['clean_pipes']

			self.__snap_data__['status'] = None

			self.__snap_data__['args'] = None
			self.__snap_data__['env'] = None

			use_shell = False
			user_env = {}

			PIPES = {
				# -999 indicates unassigned, 0+ will be assigned but controlled by user, -1 is assigned by us
				# io_mode is index of [read, write] pipe
				'stdin':{'pipes':[-1,-1], 'assign':None, 'io_mode':1},
				'stdout':{'pipes':[-1,-1], 'assign':None, 'io_mode':0},
				'stderr':{'pipes':[-1,-1], 'assign':None, 'io_mode':0},
			}

			for attr,value in MSG.kwargs.items():
				
				# NOTE: child process will always assign pipe() return fid to stdin,stdout,stderr
				# while main process will either assign to global or to local
				# TODO achieve this by forwarding the pipe output to stdout,stderr ourself
				# https://www.youtube.com/watch?v=5fnVr-zH-SE

				if attr in PIPES.keys():

					if value is True or value == "PIPE":
						PIPES[attr]['assign'] = -1 # assigned by us

					elif value is None or value is False:
						pass # unused # TODO shouldn't this be -999 or something?

					elif isinstance(value, int):
						PIPES[attr]['assign'] = value # assigned by user, no cleanup

					else:
						raise TypeError('invalid pipe', repr(attr))

				elif attr == 'env':
					raise NotImplementedError(repr(attr))

				elif attr == 'shell':
					use_shell = bool(value)

				else:
					ENV.snap_warning("unknown attr", repr(attr))

			"""
			if (!data->args){
				snap_warning("no command for subprocess call!");
				int returncode = -1;
				snap_assignattr_at(self, "returncode", &returncode, sizeof (int), IDX_SnapSubprocess_returncode);
				return NULL; //(any)"ERROR";
			}
			"""	
			ENV.snap_out(PIPES)

			for idx,pname in enumerate(PIPES.keys()):

				pinfo = PIPES[pname]

				if pinfo['assign'] is None:
					# unused
					continue

				elif pinfo['assign'] == -1:
					# this means pipe is used but needs new assign (don't use globals)
					pinfo['pipes'][:] = pipe()
					mode = pinfo['io_mode']
					pipes[idx] = pinfo['pipes'][mode]
					clean_pipes[idx] = True
					_SnapSubprocess_set_fd_options(pinfo['pipes'][mode], blocking=False)

				elif pinfo['assign'] > -1:
					# controlled by user
					pipes[idx] = pinfo['assign']
					clean_pipes[idx] = False
					_SnapSubprocess_set_fd_options(pinfo['assign'], blocking=False)

				else:
					raise TypeError('invalid pipe config?')

			# https://linux.die.net/man/2/pipe

			# https://man7.org/linux/man-pages/man7/environ.7.html
			# "When a child process is created via fork(2), it inherits a copy of its parent's environment."
			# so we modify the current env before the fork, save the previous values, then set them back in the main process after the child has duplicated it...

			# TODO apparently setenv can be called in the child process
			# https://unix.stackexchange.com/questions/489749/question-about-global-environment-variables-and-fork-exec/489767#489767

			# TODO setenv has a memory leak, look into alternative options...

			if user_env:
				raise NotImplementedError('user env')

			if use_shell:
				raise NotImplementedError("use_shell")
				
				"""
				https://github.com/python/cpython/blob/main/Lib/subprocess.py
				if shell:
		            # On Android the default shell is at '/system/bin/sh'.
					unix_shell = ('/system/bin/sh' if
		                      hasattr(sys, 'getandroidapilevel') else '/bin/sh')
		            args = [unix_shell, "-c"] + args
					if executable:
						args[0] = executable
				"""

			data['pid'] = fork() # should raise on fail (in c it is a fail if < 0)

			assert data['pid'] >= 0, 'unable to create subprocess'

			if data['pid'] == 0:
				# child process

				#setenv("SPOONS","TRUE",1);
				#snap_out("child environ %s", getenv("SPOONS"));

				# https://www.youtube.com/watch?v=OVFEWSP7n8c
				# https://linux.die.net/man/3/execl
				# http://unixwiz.net/techtips/remap-pipe-fds.html

				# redirecting standard output https://www.youtube.com/watch?v=5fnVr-zH-SE

				# STDIN always remapped, because otherwise it would be sharing global stdin! TODO make it possible to do that... (if NULL assigned?) XXX should work to pass in the stdin fd directly, etc...

				for idx,pname in enumerate(PIPES.keys()):
					pinfo = PIPES[pname]
					if pinfo['assign'] is None:
						# fd unused (but don't send to global, so send to devnull)
						dup2(snap_devnull(), getattr(sys, pname).fileno())

					elif pinfo['assign'] == -1:
						# NOTE: we're in the child process, so the read/write is reversed (ie. stdin is read/input in here)
						mode = pinfo['io_mode']
						other_mode = int(not mode)
						close(pinfo['pipes'][mode])
						pinfo['pipes'][mode] = -1
						# set the custom pipe to be the global pipe
						dup2(pinfo['pipes'][other_mode], getattr(sys, pname).fileno())

					else:
						# use designated fd
						if pinfo['assign'] != getattr(sys, pname).fileno():
							dup2(pinfo['assign'], getattr(sys, pname).fileno())
							close(pinfo['assign']) # because fork duplicates it?  verified https://youtu.be/5fnVr-zH-SE?t=825
							# https://stackoverflow.com/questions/30226530/same-file-descriptor-after-fork "fork duplicates the copy"
							# TODO https://stackoverflow.com/questions/11635219/dup2-dup-why-would-i-need-to-duplicate-a-file-descriptor/11636056#11636056
						
				"""
				if (STDIN_FD < -1){
					// fd unused
					dup2(snap_devnull(), fileno(stdin));
				}
				else if (STDIN_FD == -1){
					// use pipe
					close(STDIN[WRITE]); // close stdin write
					STDIN[WRITE] = -1;
					dup2(STDIN[READ], fileno(stdin)); // assign read fd to STDIN
					//close(STDIN[READ]);
					//STDIN[READ] = -1;
				}
				else {
					// use designated fd
					if (STDIN_FD != fileno(stdin)){
						dup2(STDIN_FD, fileno(stdin));
						close(STDIN_FD); // because fork duplicates it?  verified https://youtu.be/5fnVr-zH-SE?t=825
						// https://stackoverflow.com/questions/30226530/same-file-descriptor-after-fork "fork duplicates the copy"
						// TODO https://stackoverflow.com/questions/11635219/dup2-dup-why-would-i-need-to-duplicate-a-file-descriptor/11636056#11636056
					}
				}

				if (STDOUT_FD < -1){
					dup2(snap_devnull(), fileno(stdout));
				}
				else if (STDOUT_FD == -1){
					close(STDOUT[READ]); // close stdout read
					STDOUT[READ] = -1;
					dup2(STDOUT[WRITE], fileno(stdout)); // assign write fd to STDOUT
					//close(STDOUT[WRITE]); // this is an extra copy?
					//STDOUT[WRITE] = -1;
				}
				else {
					if (STDOUT_FD != fileno(stdout)){
						dup2(STDOUT_FD, fileno(stdout));
						close(STDOUT_FD);
					}
				}

				if (STDERR_FD < -1){
					dup2(snap_devnull(), fileno(stderr));
				}
				else if (STDERR_FD == -1){
					close(STDERR[READ]); // close stderr read
					STDERR[READ] = -1;
					dup2(STDERR[WRITE], fileno(stderr)); // assign write fd to STDERR
					//close(STDERR[WRITE]);
					//STDERR[WRITE] = -1;
				}
				else {
					if (STDERR_FD != fileno(stderr)){
						dup2(STDERR_FD, fileno(stderr));
						close(STDERR_FD);
					}
				}
				"""

				"""
				/*
				if env is None:
					os.execvp(executable, args)
				else:
					os.execvpe(executable, args, env)
				"""

				# TODO can env be achieved with setenv?
				# https://stackoverflow.com/questions/31341533/how-to-capture-environment-after-fork-and-exec-in-c

				# https://man7.org/linux/man-pages/man7/environ.7.html
				# "Arguments may also be placed in the environment at the point of an exec(3).  A C program can manipulate its environment using the functions getenv(3), putenv(3), setenv(3), and unsetenv(3)."

				# TODO if we want to be super safe, before calling fork, we can getenv and save existing entries (if existing),
				# then setenv new entries, then call fork, and unsetenv/setenv to reset in main process...
				# (values are const char*, so if they exist we know they are set...)

				# TODO we can resolve the path ourself by searching the getenv("PATH");

				# TODO try working around the execve problem by adding the ENV variables to the command?
				# https://unix.stackexchange.com/questions/56444/how-do-i-set-an-environment-variable-on-the-command-line-and-have-it-appear-in-c
				# https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_09_01
				# https://man7.org/linux/man-pages/man3/exec.3.html
				# "All other exec() functions (which do not include 'e' in the suffix) take the environment for the new process image from the external variable "environ" in the calling process."
				# "execvpe() searches ... using the value of PATH ... If the specified filename includes a slash character, then PATH is ignored, and the file at the specified pathname is executed. ... If [PATH] isn't defined, the path list defaults to a list that includes the directories returned by confstr(_CS_PATH) ... If permission is denied for a file (the attempted execve(2) failed with the error EACCES), these functions will continue searching the rest of the search path.

				# https://linux.die.net/man/2/execve
				# https://linux.die.net/man/3/execvpe
				#execlp("watch", "watch", "-n", "1", "-d", "sensors", NULL);
				#execv(data->args[0], data->args);//, data->env); // TODO use this and do our own path resolution following the spec, allow path as argument too
				# https://docs.python.org/3/library/os.html#os.execvp
				COMMAND = [str(i) if not isinstance(i, str) else i for i in COMMAND]
				#ENV.snap_out('sending command', COMMAND)
				execvp(COMMAND[0], COMMAND)#, data->env);
				#execve(data->args[0], data->args, newenviron);//data->env); // TODO why does this stop running and not output anything? something to do with _POSIX_VERSION?

				# https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/fs/exec.c#l1376

				# this code will ONLY run if exec fails to run
				ENV.snap_error("subprocess exec failed")
				sys.exit(-1) # we are still in fork() child!

			else:
				# main/parent process

				# TODO use fcntl to make sure non-blocking mode is set on all pipes (even if fd is user assigned)

				#if (restore_env){
				#	// TODO main process resets env vars using setenv for all restore_env
				#}

				for idx,pname in enumerate(PIPES.keys()):
					pinfo = PIPES[pname]

					if pinfo['assign'] == -1:
						# close read of input and write of output if it is a pipe, otherwise leave it alone
						other_mode = int(not pinfo['io_mode'])
						close(pinfo['pipes'][other_mode])
						pinfo['pipes'][other_mode] = -1

				# if refresh_mode is NULL or "USER" then user must call PROCESS or read/write to buffers manually
				# if (refresh_mode == (any)"BLOCKING" || refresh_mode == (any)"BLOCK" || refresh_mode == (any)"SELF"){
				# snap_event_noargs(self, "PROCESS"); // this will run until subprocess terminates
				# }

				# now user calls "WAIT" or "COMMUNICATE" until complete...

			return None

		def __init__(self, command=None, **SETTINGS):
			SnapNode.__init__(self)

			#self._returncode_ = None # int once assigned (which means process has completed)
			#self._pid_ = -1
			#self._pipes_ = [-1] * 3
			#self._clean_pipes_ = [False] * 3 # bool whether or not pipe is managed by self (if fd is given by user it will not be closed by subprocess)
			#self._status_ = -1

			# https://linux.die.net/man/3/getopt
			# https://linux.die.net/man/8/ld.so
			#char** args; // NULL terminated list of strings making up the command (allocated)
			#char** env; // NULL terminated list of strings
			# TODO also allow configuration of path?

			if command or SETTINGS:
				self.start(command, **SETTINGS)
			#if command is not None:
			#	self.start(command, **SETTINGS)

			ENV.QUIT.listen(self.__delete__)

		@ENV.SnapChannel
		def __delete__(self, MSG):
			ENV.QUIT.ignore(self.__delete__)
			if self['running']:
				self.terminate()


	ENV.SnapSubprocess = SnapSubprocess



def main(ENV):

	
	#buffer_size = 4096

	#char read_buffer[buffer_size];
	#snap_memset(read_buffer, 0, buffer_size);

	#command_list = ["/usr/bin/watch", "-n", "1", "-d", "sensors"]
	command_list = ["ls"]

	sub = ENV.SnapSubprocess(command=command_list, stderr=True, stdout="PIPE")

	timeout = ENV.snap_time() + 3
	#while (snap_event_noargs(&sub, "running") == (any)"TRUE"){
	while ENV.snap_time() < timeout:

		stdout, stderr = sub.communicate()

		if stdout or stderr:
			#snap_out("received(%li): \"%s\"", processed_size, read_buffer);
			ENV.snap_out("received stdout", len(stdout), stdout)
		if stderr:
			ENV.snap_out("recieved stderr", len(stderr), stderr)

		ENV.snap_sleep(.1)

	del sub

	#PATH = os.getenv("PATH")
	#ENV.snap_out("path %s", PATH)


	# test both buffer methods (callback or read/write)

	# test pause and resume

	# test piping commands together "|"

	# test different shell/env/executable scenarios (make some to use safely?)

	ENV.snap_out('ok')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

