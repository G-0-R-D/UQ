
#from snap.lib.parsing.parseq.ParseqDecoder import *
#from snap.lib.parsing.parseq.ParseqEncoder import *

#from snap.lib.parsing.parseq import ParseqSequence as ParseqSequenceModule

def build(ENV):

	# TODO work on a visual feedback (gui) for the debugger, where we can show the steps of the parse in the gui with user interaction to make it clear what the steps were...  (just save the necessary data to report it in post, or maybe emit it...?)
	class ParseqDebugger(object):

		#__slots__ = []

		def error(self, *a):
			''

		def warning(self, *a):
			''

		def out(self, *a):
			''

		def test_out(self, TEST):
			''

		def reset(self, **SETTINGS):
			'reset'
			if 'closest_match' in SETTINGS:
				'reset closest_match only?'


		def debug_level(self):
			return self.__debug_level__

		def register_closest_match(self, SEQUENCE, RULE, START, END):
			if self.debug_level() < 0:
				return
			assert SEQUENCE is not None
			CLOSEST_MATCH = self.__closest_match__
			if SEQUENCE not in CLOSEST_MATCH:
				CLOSEST_MATCH[SEQUENCE] = {'level':len(CLOSEST_MATCH), 'span':[START,END]}
			else:
				span = CLOSEST_MATCH[SEQUENCE]['span']
				if span[-1] < END: # TODO backwards?
					span[-1] = END

			if CLOSEST_MATCH[SEQUENCE]['level'] > 0:
				''#print('match', PRIVATE['DEPTH'], RULE, START, END)
			#RULE.print_tree()


		def closest_match(self):
			# TODO return line info for lowest?
			for sequence, info in self.__closest_match__.items():
				if info['level'] == 0:
					end = info['span'][-1]
					start = max(0, end-1)
					return ENV.ParseqResult(sequence=sequence, rule=None, span=[start,end], subs=None)#.line_info()
			#print(PRIVATE['CLOSEST_MATCH'])
			#return PRIVATE['CLOSEST_MATCH']
			if self.__debug_level__ > -1:
				raise NotImplementedError()
			return None




		def incr(self):
			self.__depth__ += 1

		def decr(self):
			self.__depth__ -= 1
			# TODO verify > -1?


		def set(self, **SETTINGS):

			for attr,value in SETTINGS.items():
				if attr == 'debug_level':
					self.__debug_level__ = int(value)

		def __init__(self, **SETTINGS):

			self.__debug_level__ = 0 # XXX is this needed?  if debugger is in use we can assume we want to use it...  we just need to include what we want to report on or capture specifically...
			self.__closest_match__ = {}
			self.__depth__ = 0

			self.set(**SETTINGS)

	"""
	def build(ENV):


		def reset_debugging():
			reset_closest_match()

		#def set_debug_level(NUM): # TODO make as series of flags for debug features?
		#	PARSEQ_DEBUG_LEVEL[0] = NUM

		#def debug_level():
		#	return PARSEQ_DEBUG_LEVEL[0]


		def lex_test(TOPLAYER, SEQUENCE):
			'' # this is really just layer.sublayer().search(SEQUENCE)...


		PARSEQ_DEBUGGERS = [] # ParseqDebugger() instances (will add/remove themselves)

		# XXX make specific commands so we don't have to spam **INFO when debugger is off!  just do like incref()/decref(), match(result), ... and let the debugger do the analysis...
		def parseq_debugger_register(**INFO):

			# TODO if level > 0 then always register the closest / longest match info?

			if not PARSEQ_DEBUGGERS:
				return

			for debugger in PARSEQ_DEBUGGERS:
				debugger.register(**INFO)


		# TODO keep track of matches per-line?  (use result.line_info(), and save each set per-line)
		# then when we match ERROR we can print the whole line of matches and see if they make sense (or we can save everything from a match?  so we can check back to it?)
		#	-- NOTE: we could just save the results in a list ourselves!


		def modified_profiles(*profiles, **SETTINGS):
			d = {}
			for profile in profiles:
				d.update(profile)
			d.update(SETTINGS)
			return d

		class ParseqDebugger(object): # TODO make this a ParseqLayer subclass that can even be used as such!  so we can kind of insert the debugger into the parser stack if desired...

			# TODO initialize self and assign as active_debug session (global var) for all match updates to report to...

			# TODO should this be a ParseqLayer subclass so we can make use of caching api?


			def next(self, count=None):

				if count is None:
					count = 1

				rule = self._rule_
				sequence = self._sequence_

				while count != 0:
					count -= 1
					count = max(count, -1) # clamp; < 0 means run forever

					# TODO search without result but don't stop on suppressed?
					result = rule.search_with_result(sequence)
					if not result:
						return False

					if result.name() == "ERROR":
						lineno, col, line = result.line_info()
						#snap_error(result, repr(result.value()), result.line_info())
						snap_error(result, col, repr(line[:col]), repr(line))
						return False

					elif 'error' in result.name().lower():
						snap_warning(result, repr(result.value()), result.line_info())
						return False

					else:
						'all results should be recorded (with each layer results separate?)'
						print(result, repr(result.value()))#, result.line_info())

				return True

			def get_results(self, lineno=None, **SETTINGS):
				'return results with lineno == lineno or other options...'

			def run_to_error(self):
				while 1:
					# TODO option to print levels of output (regardless of error status)
					if not self.next(count=-1):
						'check error status and report if error'
						break

				return self # for chaining commands
					

			def __init__(self, RULE, SEQUENCE, **SETTINGS):

				# TODO make some profiles for common debugging scenarios?  the profiles are just dicts of settings to pass into init?

				# TODO enable debugging flags?  or register self so parsing calls can add entries to self?  for full match checking?

				# TODO context to keep track of results and query what went wrong, helpful in diagnosing errors

				assert (RULE and SEQUENCE), 'missing rule({}) or sequence({})'.format(type(ROOT), type(SEQUENCE))

				self._rule_ = RULE
				self._sequence_ = SEQUENCE

				if SEQUENCE.position() != 0:
					snap_warning("sequence not at start (0)")

				self._saved_results_ = []

				self._verbosity_ = 0 # flags of verbosity levels (to include)

	"""
	ENV.ParseqDebugger = ParseqDebugger

