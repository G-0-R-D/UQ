

def build(ENV):

	#ENV.__build__('snap.lib.core.parsing.parseq.ParseqLayer')

	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error

	ParseqSequence = ENV.ParseqSequence
	ParseqLayer = ENV.ParseqLayer

	class ParseqDecoder(ParseqLayer):

		# XXX use ENV.PARSEQ_ERROR, defined in ParseqRules
		#ERROR = NOTANY(name='ERROR', capture=True) # matches anything, use in grammar when a match is known to fail to catch it...

		# TODO move this to debugger?
		def report_bad_result(self, RESULT, **SETTINGS):
			'if string then use result.line_info() else use repr()?'
			if not RESULT:
				'just print general error, notify that something happened but we dont know what'
				snap_error('bad result', RESULT)
				return
			try:
				lineno,colno,line = RESULT.line_info()
				'TODO print error info with line and number, cut line if it is too long'
			except TypeError:
				'just try to print the span and segment of the source that is at issue...'
				

		def dump_layer_results(self, OUTFILE_PATH, layer_index=0, **SETTINGS):
			# TODO write all the results into file for debugging, make it easy to select sublayer by layer index (0 is toplayer, error if index out of range)
			"""
			import os
			os_join = os.path.join
			THISDIR = os.path.dirname(os.path.realpath(__file__))
			with open(os_join(THISDIR,'layer1.txt'),'w') as openfile:
				openfile.write('\n'.join(['[{}] {} >> {}'.format(idx,str(result), repr(result.value())) for idx,result in enumerate(layer1)]))

			layer2 = []
			seq.rewind()
			while 1:
				result = self.search_with_result(sequence=seq)
				if not result:
					break
				seg = [result, None]
				try:
					seg[-1] = repr(result.value())
				except:
					pass
				layer2.append(seg)
			with open(os_join(THISDIR, 'layer2.txt'), 'w') as openfile:
				openfile.write('\n'.join(['[{}] {} >> {}'.format(idx, str(seg[0]), repr(seg[1])) for idx,seg in enumerate(layer2)]))
			"""

		def decode_result(self, RESULT, **SETTINGS):
			raise NotImplementedError(SNAP_FUNCTION_NAME())

		def decode(self, sequence=None, **SETTINGS):

			assert isinstance(sequence, ParseqSequence), 'input must be ParseqSequence'

			if not sequence._source_:
				raise ValueError('no source on sequence')
			#if not sequence._source_.endswith('\n'):
			#	sequence._source_ += '\n'

			#print(repr(sequence.source()))

			#MODULE = {
			#	'type':'module',
			#	'body':[]
			#	}

			#ignore = ANY(' ','\t','\n',
			#	capture=False, suppress=True)
			#ignore = OR(*[ParseqLayerITEM(name=n) for n in ('NEWLINE','INDENT','DEDENT')])

			sublayer = self.sublayer()
			if sublayer:
				# TODO root sublayer?
				sublayer._source_ = sequence

			# NOTE: simplifying collapses the (unused) tests... (but also makes it hard to determine where we are contextually!)
			self.set(simplify=False)

			while 1:

				result = self.search_with_result(sequence)
				if not result:
					break

				if result.name() == 'ERROR':
					snap_error(result, result.line_info())

				else:
					decoded = self.decode_result(result)
					if decoded:
						yield decoded
					else:
						snap_warning('no decoded result', result)

				"""
				if 0:
					''#print(result, repr(result.value()))#, result.sub_value())#, result.line_info())
				else:
					#result.print_tree()
					''#print(result.name(), result.line_info(), result.span())
				if result.rule() == ERROR:
					snap_warning("parse error", result.line_info())
				else:
					out('parse success', result.name(), result.line_info())
				if 0:
					decoded = self.decode_result(result)
					if decoded:
						if not isinstance(decoded, list):
							decoded = [decoded]
						MODULE['body'].extend(decoded)
						#print('decoded', decoded)
					else:
						''#warning('nothing returned from decode_result')
				"""

			return


		def decode_text(self, TEXT, **SETTINGS):
			sequence = ParseqSequence(source=TEXT)
			return self.decode(sequence=sequence, **SETTINGS)

		def decode_string(self, *args, **kwargs):
			return self.decode_text(*args, **kwargs)
				

		def decode_file(self, FILEPATH, **SETTINGS):
			with open(FILEPATH, 'r') as openfile:
				# TODO use a SnapFile once it's api allows __getattr__ and __setattr__ functionality...
				return self.decode_text(openfile.read(), **SETTINGS)

		def __init__(self, *args, **kwargs):
			ParseqLayer.__init__(self, *args, **kwargs)

	ENV.ParseqDecoder = ParseqDecoder
	return ParseqDecoder

