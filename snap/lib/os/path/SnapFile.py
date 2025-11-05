
# from snap.lib.os.path.SnapFilepath_core import * ?

# TODO use __getattr__ __setattr__ api to be able to read and write to file?
# so we can say SnapFile()[start:end] and read the data we want (optimally without worrying about seek or caching under the hood)
# 	-- also it opens in append mode (rather than clearing a file by opening it to write!), so we intuitively just open the file 'as is' and then use the __setitem__ api to assign bytes into the file...  and include insert() call

from fcntl import fcntl, F_GETFL, F_SETFL

from os import (
	pread,
	pwrite,
)


def build(ENV):

	

	SNAP_INIT = ENV.SNAP_INIT

	def SnapFile_read_write_bytes(self, MODE, **SETTINGS):

		BUFFER = None

		any PTR = NULL;
		snap_int* LENGTH = NULL;
		snap_int* ACTUAL = NULL;
		snap_int* POSITION = NULL;

		{for_attr_in_SnapNode(MSG)
			if (attr == (any)"pointer" || attr == (any)"ptr") PTR = value;
			else if (attr == (any)"length" || attr == (any)"size") LENGTH = (snap_int*)value;
			else if (attr == (any)"actual") ACTUAL = (snap_int*)value;
			else if (attr == (any)"position") POSITION = (snap_int*)value;
			else SNAP_UNKNOWN_ATTR;
		}}

		if (!(PTR && LENGTH && POSITION)){
			snap_error("incomplete args for \"%s\"", (char*)EVENT);
			return (any)"ERROR";
		}

		snap_int actual = 0;
		if (!ACTUAL) ACTUAL = &actual;
		*ACTUAL = -1;

		// NOTE: this is a lazy loading system, fd is not created until a read or write is attempted
		int* fd = (int*)snap_event(self, "_fd_", "create", ((EVENT == (any)"__PERFORM_WRITE_BYTES__") ? "TRUE":"FALSE"));
		if (!fd){
			*ACTUAL = -1;
			return (any)"ERROR";
		}

		# https://docs.python.org/3/library/os.html#os.pread
		if MODE == self.__read_bytes__:
			*ACTUAL = (snap_int)pread(*fd, PTR, *LENGTH, *POSITION);
		else: # __write_bytes__
			*ACTUAL = (snap_int)pwrite(*fd, PTR, *LENGTH, *POSITION);

			if (*ACTUAL > 0){
				snap_int* length = (snap_int*)snap_event_noargs(self, "length");
				if (length){
					*length += SNAP_MAX(0, (*POSITION + *ACTUAL) - *length); // size only increases if write is past the previous end...
				}
			}
		}

		if (*ACTUAL < 0){
			snap_error("%s error (%d): \"%s\"", (char*)EVENT, errno, strerror(errno));
		}

		return None

	class SnapFile(SnapBytesIO):

		__slots__ = ['_path_', '_fd_']

		def path(self):
			return self._path_

		def filepath(self):
			return self.path()

		def data(self):
			return None

		def buffer(self):
			return self.data()

		def size(self):
			# just init the __fd__ before returning the size
			self.file_descriptor(create=False) # init if applicable
			return SnapBytesIO.size(self)

		def length(self):
			return self.size()

		def readable(self):
			#|| EVENT == (any)"writable"){

			fd = getattr(self, '_fd_', None)
			# NOTE: we are considering user assigned status here:
			status = SnapBytesIO.readable(self)
			if fd is not None and fd > -1 and status == True:
				# https://linux.die.net/man/2/fcntl
				# verify the file is accessible via the mode

				# TODO verify status is bool so it is safe to re-assign in raw?
				snap_raw("""
				int arg = fcntl(*fd, F_GETFL);
				if (arg > -1 && ((arg & O_RDWR) || 1)){
					// && arg & O_RDONLY) || // XXX O_RDONLY is 0!  we can't mask with it
					// if it gets here assume read is true (file is open with valid descriptor and not writable then it is readable)
					status = SnapTrue;
				}
				else {
					status = SnapFalse;
				}
				""")

			return status

		def writable(self):

			fd = getattr(self, '_fd_', None)
			status = SnapBytesIO.writable(self)
			if fd is not None and fd > -1 and status == True:
				
				snap_raw("""
				int arg = fcntl(*fd, F_GETFL);
				if (arg > -1 && (arg & O_RDWR || arg & O_WRONLY)){
					status = SnapTrue;
				}
				else {
					status = SnapFalse;
				}
				""")

			return status

		def file_descriptor(self, create=False):
			# this is a pseudo property that takes an arg of whether to create if missing
			# it is a lazy load of the file for access once a read or write is performed
			# (or it is needed for some other reason)
			# it is intended for internal use, but can be used by any process that wants the fd

			# https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/sys_stat.h.html
			# XXX safer to just attempt to open apparently https://stackoverflow.com/a/7088188
			# which makes sense, just deduce the mode from the error context

			fd = getattr(self, '_fd_', None)
			if fd:
				return fd # once created it persists until closed/nullified

			# init position to 0, nullify size until it is verified
			#position = self.position()
			position = 0 # init to 0
			i = 0
			#snap_assignattr_at(self, "__position__", &i, sizeof (snap_int), IDX_SnapBytesIO___position__);
			#snap_assignattr_at(self, "length", NULL, sizeof (snap_int), IDX_SnapBytesIO_length);
			self._length_ = None # SnapBytesIO attr...

			path = getattr(self, '_path_', None)
			if not path:
				return None


			# this is a user designation, not a file permissions indication
			readable = self.readable() == True
			writable = self.writable() == True

			# TODO this:
			snap_raw("""
			int base_flags = O_SYNC; // TODO experiment with O_DIRECT

			int _fd = -1;
			struct stat st;
			if (lstat(path, &st) != 0){
				if (snap_getattr(MSG, "create") != (any)"TRUE")
					return NULL; // which will likely result in a read/write error

				long int mode = 0666; // 6 = rw, 7 = rwx, positions refer to user, group, and something else lol
				// TODO use chmod to change permissions after created?

				base_flags |= O_CREAT;

				// TODO consider "readable"|"writable" status

				// otherwise try to create new file with maximum read/write ability or fallback to what is possible

				if (readable && writable){
					_fd = open(path, O_RDWR|base_flags, mode);
					if (_fd < 0 && (errno == EACCES || errno == EPERM)){
						// if read and write open fails (with permission error), try to open again as just read or just write
						_fd = open(path, O_RDONLY|base_flags, mode);
						if (_fd < 0)
							_fd = open(path, O_WRONLY|base_flags, mode);
					}
				}
				else if (readable){
					_fd = open(path, O_RDONLY|base_flags, mode);
				}
				else if (writable){
					_fd = open(path, O_WRONLY|base_flags, mode);
				}

				// size = 0 (new file)
				i = 0; // set for sanity
			}
			else {
				// exists, open it
				if (readable && writable){
					_fd = open(path, O_RDWR|base_flags);
					if (_fd < 0 && (errno == EACCES || errno == EPERM)){
						// if read and write open fails (with permission error), try to open again as just read or just write
						_fd = open(path, O_RDONLY|base_flags);
						if (_fd < 0)
							_fd = open(path, O_WRONLY|base_flags);
					}
				}
				else if (readable){
					_fd = open(path, O_RDONLY|base_flags);
				}
				else if (writable){
					_fd = open(path, O_WRONLY|base_flags);
				}

				// size = file size
				i = (snap_int)st.st_size;
			}

			if (_fd < 0){
				// error
				snap_error("unable to open file(\"%s\") error(%d): \"%s\"", path, errno, strerror(errno));
			}
			else {
				// success, assign fd and return it
				snap_assignattr_at(self, "_fd_", &_fd, sizeof (int), IDX_SnapFile__fd_);
				fd = (int*)snap_getattr_at(self, "_fd_", IDX_SnapFile__fd_);
				if (!fd){
					snap_error("unable to allocate fd!");
					close(_fd);
					snap_assignattr_at(self, "length", NULL, 0, IDX_SnapBytesIO_length);
				}
				else {
					snap_assignattr_at(self, "length", &i, sizeof (snap_int), IDX_SnapBytesIO_length);
				}
			}
			""")
			return fd


		def __read_bytes__(self, length=1, position=0):
			'' # TODO TODO TODO TODO TODO

			# TODO actual is obtainable from length of returned buffer

			if length < 1:
				return None
	
		def __write_bytes__(self, BUFFER, position=0):
			''

		def __SnapDataStream_truncate__(self, *a, **k):
			''


		def set(self, **SETTINGS):

			for attr,value in SETTINGS.items():

				if attr == 'path' or attr == 'filepath':
					''
				else:
					SnapBytesIO.set(self, **{attr:value})


		def __init__(self, **SETTINGS):
			SnapBytesIO.__init__(self, **SETTINGS)

			self._path_ = None
			self._fd_ = None # file descriptor returned by open()

			SNAP_INIT(self, SETTINGS,
				'path','filepath')

	ENV.SnapFile = SnapFile
	return SnapFile



