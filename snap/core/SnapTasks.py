
from types import MethodType, GeneratorType
from weakref import ref as weakref_ref

def build(ENV):

	SnapNode = ENV.SnapNode

	SnapBoundChannel = ENV.SnapBoundChannel # for check

	snap_time_since_epoch = ENV.snap_time_since_epoch
	snap_list_rotate = ENV.snap_list_rotate

	SnapMessage = ENV.SnapMessage

	def task(CALLABLE, MSG):

		yield

		if isinstance(CALLABLE, SnapBoundChannel):
			node,channel,method = CALLABLE.__data__
			if method is None:
				return # if channel doesn't exist then there is nothing to call, but ignore silently?

			_return = CALLABLE.__direct__(MSG)
		else:
			_return = CALLABLE(MSG)

		if not isinstance(_return, GeneratorType):
			return

		# if the method returns a generator type (uses yield) then we keep processing it until it is complete...
		# it is the user's job to make sure the processing does not take a long time

		while 1:
			
			try:
				next(_return)
			except StopIteration:
				return # no error
			#except Exception as e:
			#	ENV.snap_error(node, channel, 'error >>')
			#	ENV.snap_print_exception(e)
			#	ENV.snap_print_stack()
			#	return

			yield


	def still_time():
		# True if the elapsed time is within the current rate
		ENV.mainloop # touch
		MAINLOOP = ENV.__PRIVATE__['__MAINLOOP_NODE__']
		return (snap_time_since_epoch() - MAINLOOP['__last_time__']) < MAINLOOP['__rate__']


	class SnapTasks(SnapNode):

		__slots__ = []

		@ENV.SnapChannel
		def process(self, MSG):
			'process fast tasks, call each one for one iteration once -- check how long it takes?  resume on next cycle?'
			# have two lists, move from one to the other until empty then reset?
			# also put long running tasks in own section?

			# can have a regular method that will then be called once and discarded (callback), or returns an GeneratorType that can then be called repeatedly until it quits or is cancelled...

			# do lazy stuff here as well...
			# TODO do lazy by allowing user to assign to a timeout?  then just connect that node/group to the timers for that time...?
			#	-- if timers supports generators then we could just use timers...  these are just repeat timers anyway...
			#	-- this api can continue to exist but it just forwards to timers?


			# TODO use a taskgroup for the mainloop group as well, but process it from here?
			#	-- tasks is basically just the groups?  if the groups exist then they keep themselves registered on each iteration...


			# TODO evaluate all callbacks
			# TODO evaluate one lazy callback

			tasks = self['__tasks__']
			if tasks:

				# evaluate all at most once per mainloop (but only as many as can be completed before rate is exceeded)
				# new tasks are appended so there should be no issue if tasks are changed during evaluation...
				remaining = len(tasks)

				while 1:

					task = tasks[0]

					try:
						next(task)
						snap_list_rotate(tasks, -1) # move to end of queue
					except StopIteration: # TODO Exception as e: then check if exception is StopIteration otherwise report the error?
						tasks.pop(0)

					remaining -= 1
					if not (remaining > 0 and still_time()):
						# this approach ensures at least one task will always evaluate
						break

			else:
				# done; nothing to do
				ENV.mainloop.ignore(self.process)


		@ENV.SnapChannel
		def callback(self, MSG):
			# callbacks are 'lazy'; one is evaluated per mainloop iteration

			CH = MSG.args[0]

			# the rest of the message is user provided callback arguments, args and kwargs
			submsg = SnapMessage(*MSG.args[1:])

			tasks = self['__tasks__'] or []

			tasks.append(task(CH, submsg))

			self['__tasks__'] = tasks 

			ENV.mainloop.listen(self.process)

		#def cancel(self, MSG):
		#	'' # the preferred method is to just return from the iterator, or raise StopIteration

		def __init__(self):
			SnapNode.__init__(self)

			# TODO constant, 1 sec, and consecutive tiers?  consecutive means finish the first task before getting to the next one, runs at one second?

			# TODO either callback or lazy_callback, callback will always call on each mainloop iteration, lazy callback calls next in queue on each iteration (not based on time!)
			#	-- time-based callbacks need to be done using timers!

			# a task is a method of a SnapNode, which could also be a generator (in which case it keeps going)
			#	-- then we just iterate until it stops or errors, or until TASKS.cancel(node.method) is called?

			self['__tasks__'] = []


	ENV.SnapTasks = SnapTasks
	ENV.TASKS = SnapTasks()

def main(ENV):

	class User(ENV.SnapNode):

		@ENV.SnapChannel
		def load(self, MSG):
			for i in range(10):
				print('load', i)
				yield i # can yield or not, doesn't matter

		def __init__(self):
			ENV.SnapNode.__init__(self)

	user = User()

	ENV.TASKS.callback(user.load)

	ENV.mainloop(seconds=10)

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


