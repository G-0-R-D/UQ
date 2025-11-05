
#from snap.lib.core.SnapObject import *

#from snap.lib.parsing.parseq.ParseqResult import PARSEQ_TYPE_SEQUENCE
#from snap.lib.parsing.parseq import ParseqResult as ParseqResultModule


#ENV.__import_and_build__('snap.lib.parsing.parseq.ParseqResult')

#snap_warning = ENV.snap_warning

#SnapObject = ENV.SnapObject

def build(ENV):

	ENV.PARSEQ_MATCH_FAIL = PARSEQ_MATCH_FAIL = -199999990039393

	ENV.PARSEQ_TYPE_SEQUENCE = PARSEQ_TYPE_SEQUENCE =1

	class ParseqSequence(object):
		# NOTE: SnapDataStream is source() not superclass!  (this is buffering of SnapDataStream? TODO)

		__slots__ = [
			'_step_',
			'_source_',
			'_position_',
			'depth',
			'rootpath',
			'saved_rootpaths',
			'subparse_in_progress',
			'rule_settings',
			'saved_rule_settings',
			'MATCH_START',
			'MATCH_END',

			'DEBUGGER',
		]

		_type_code_ = PARSEQ_TYPE_SEQUENCE

		def __advance__(self):

			# NOTE: source just has to implement slicing api and __len__(), sequence can do the rest...

			step = self.step()
			source = self.source()
			length = self.length()
			if not source or length < 1 or step == 0:
				return

			position = self.position()
			#out('start position', position, step)
			if position < 0:
				position = 0
				self.set(position=position)
			if position > length:
				position = length
				self.set(position=position)

			alignment = position % abs(step)
			if alignment != 0:
				snap_warning("position unaligned to sequence data? (pos({}) %% step({}) = {})".format(position, abs(step), alignment))
				if step > 0:
					# move backward (so current position is captured)
					position -= alignment
				else: # step < 0
					# move forward to previous going backward (so current is captured)
					position += abs(step) - alignment

				if position < 0: position = 0
				if position > length: position = length
				self.set(position=position)

			if step > 0:
				# FORWARD
				if position + step <= length:

					value = source[position:position+step]

					self.set(position = position + step)
					return value #self.item(value)

			else: # step < 0

				if position + step > -1:

					value = source[position+step:position]

					self.set(position = position + step) # subtraction
					return value #self.item(value)

			return None

		#def item(self, value):
		#	# XXX can we just compare the items direct?  do we need a wrapper around the source items?
		#	# LayerITEM will compare in the same way...
		#	if not self._item_:
		#		self._item_ = ParseqITEM()
		#	self._item_.set(value=value)
		#	return self._item_

		def position(self):
			return self._position_

		def length(self):
			source = self.source()
			if source:
				return len(source)
			return 0

		def step(self):
			return self._step_

		def source(self):
			return self._source_

		def reverse(self):
			self._step_ *= -1

		def rewind(self):
			assert self._step_ != 0, 'cannot rewind; undefined step (0)'
			if self._step_ > 0:
				self.set(position = 0)
			else:
				self.set(position = self.length())

			self.MATCH_START = PARSEQ_MATCH_FAIL
			self.MATCH_END = PARSEQ_MATCH_FAIL



		def set(self, **kwargs):

			for k,v in kwargs.items():

				if k == 'position':
					self._position_ = int(v)

				elif k == 'step':
					self._step_ = int(v)

				elif k == 'source':
					self._source_ = v
					if self.step() < 0:
						self.set(step=self.step() * -1)
					self.rewind()


		def __repr__(self): # XXX TODO .snap method (operator function)
			typ = type(self).__qualname__
			return '<{}{} pos({}) step({})>'.format(typ, hex(id(self)), self.position(), self.step())

		def __len__(self):
			return self.length()

		def __bool__(self):
			return self is not None

		def __getitem__(self, KEY):
			source = self.source()
			if source:
				return source[KEY]
			return None

		def __init__(self, source=None, **kwargs):
			
			self._position_ = 0
			self._step_ = 1

			#self._item_ = None # for comparison, loaded and returned in __advance__()
			self._source_ = source

			self.depth = 0
			self.rootpath = []
			self.saved_rootpaths = []

			self.subparse_in_progress = False # for skip/ignore to indicate that further skip/ignore should not be permitted!

			# these are active rule settings which can be assigned to individual rules and will be used during the parse
			# it will apply to all their children unless they explicitly set these themselves...
			self.rule_settings = {
				# NOTE: we're grouping into dicts because rules could define custom settings, so this way we don't have to know what they are...
				#'capture_all':False,
				#'simplify':False,
				#'skip':None,
				#'ignore':None
				}
			self.saved_rule_settings = [] # list of dicts to set settings back to what they were before push_settings() call

			self.MATCH_START = PARSEQ_MATCH_FAIL
			self.MATCH_END = PARSEQ_MATCH_FAIL

			self.DEBUGGER = None

			#if 'step' not in kwargs:
			#	kwargs['step'] = 1
			self.set(**{k:v for k,v in kwargs.items() if k in ('position',)})

	ENV.ParseqSequence = ParseqSequence

