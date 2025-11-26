
def build(ENV):
	# we build into the ENV instead of importing, this allows more flexibility for owning code to re-direct
	# accessed to the ENV if appropriate

	# it is a good idea to localize ENV accesses up top so if they are missing the caller is notified immediately,
	# rather than discover the missing element later on when the code is running
	SnapNode = ENV.SnapNode

	class User(SnapNode):
		# SnapNode is like object in python, it is the base class of all types that are connectible in snap

		__slots__ = [] # self.__snap_data__ will function as local __dict__, so this is just housekeeping

		@ENV.SnapProperty
		class my_cool_prop:

			def get(self, MSG):
				"()->int" # no input arguments, returns an int (None should also be acceptable)

				# it's a good idea to use same name as the property name, but you don't have to...
				# (you don't have to access self.__snap_data__ at all...)
				return self.__snap_data__['my_cool_prop'] or 0

			def set(self, MSG):
				"(int!)" # input argument is single int (required)
				value = MSG.args[0]
				if value is None:
					value = 0
				assert isinstance(value, int), 'oops, expected an int'
				self.__snap_data__['my_cool_prop'] = value
				self.changed(my_cool_prop=value) # SnapNode implements this channel for you...

			# def delete(self, MSG): -> also available, but not really useful since properties exist perpetually...
				# can be useful for data cleanup, but set(None) also works...

		# alias allows for multiple names for the same channel or property
		@my_cool_prop.alias
		class cool: pass

		@ENV.SnapChannel("str?") # the string here is the output spec, for send/emit arguments
		def my_channel(self, MSG):
			"()" # no arguments, but input is supported

			# calling a channel represents the channel input, channel can do anything it wants from there...
			# like just emit an event to it's listeners...
			self.my_channel.send('string')
				

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS) # -> **SETTINGS will be assigned to the set() of SnapProperty types by SnapNode


	ENV.User = User
	return User

def main(ENV):
	# this represents the 'body' of the module, what it should do when run directly...

	test_out = ENV.snap_test_out

	User = build(ENV)
	# or:
	User = ENV.User

	class Test(ENV.SnapNode):

		@ENV.SnapChannel
		def incoming(self, MSG):
			"()"
			ENV.snap_out("incoming source: '{}' channel: '{}'".format(MSG.source, MSG.channel), MSG.args, MSG.kwargs)

		def __init__(self):
			ENV.SnapNode.__init__(self)

			self.A = User()

			self.A.my_channel.listen(self.incoming)

			self.A.my_channel(a=1, b='bonanza')

			# properties can be accessed in multiple ways
			self.A.my_cool_prop.set(101)
			value = self.A.my_cool_prop.get()
			test_out(self.A.__getitem__('my_cool_prop') == value)
			# the preferred method is using the ['item'] api, for simplicity and readability
			# properties are then visually distinguished from channels (as data rather than behaviour)
			test_out(self.A['my_cool_prop'] == value and value == 101)
			self.A['my_cool_prop'] = 0
			test_out(self.A['my_cool_prop'] == 0)
			# and we can do augmented assigns too (if you trust the get() not to return None)
			self.A['my_cool_prop'] += 100
			test_out(self.A['my_cool_prop'] == 100)

			# TODO demonstrate all the ways property can be accessed...
			# properties are also channels, but show changed() protocol... (allows grouping and listeners just listen to the one channel)

	ENV.__run__(Test)


if __name__ == '__main__':
	# this is a classic python convention for running code when a module is run directly;
	# try opening a terminal in the folder of this file and typing `python basics_of_snap_protocol.py`

	# this imports snap and initializes a new ENV
	import snap; main(snap.SnapEnv())
