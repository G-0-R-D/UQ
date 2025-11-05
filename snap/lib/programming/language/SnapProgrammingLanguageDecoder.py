
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapProgrammingLanguageDecoder(SnapNode):

		__slots__ = []

		__VERSION_TABLE__ = {}

		@ENV.SnapProperty
		class generalized:
			# convert to the generalized snap json ast format (c compat)

			def get(self, MSG):
				"()->bool"
				b = self.__snap_data__['generalized']
				if b is None:
					return True
				return bool(b)

			def set(self, MSG):
				"(bool!)"
				value = bool(MSG.args[0])
				if value is None:
					del self.__snap_data__['generalized']
				else:
					self.__snap_data__['generalized'] = value
				self.changed(generalized=value)

		@generalized.shared
		class generalize: pass

		@ENV.SnapProperty
		class with_span_info:

			def get(self, MSG):
				"()->bool"
				wspan = self.__snap_data__['with_span_info']
				if wspan is None:
					return True
				return bool(wspan)

			def set(self, MSG):
				"(bool!)"
				value = bool(MSG.args[0])
				self.__snap_data__['with_span_info'] = value
				self.changed(with_line_info=value)

		@with_span_info.shared
		class with_line_info: pass

		@ENV.SnapProperty
		class language:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['language'] or '<UNKNOWN>'

		@ENV.SnapProperty
		class version:

			def get(self, MSG):
				"()->tuple(int,int,int)"
				version = self.__snap_data__['version']
				if not version:
					return (0,0,0)
				return tuple(version)

			def set(self, MSG):
				"(tuple(int,int,int)|dict)"
				# TODO set from node or tuple

				X = MSG.args[0]

				if isinstance(X, dict):
					assert '__type__' in X, 'not an ast node: {}'.format(repr(X))
					version = self.__VERSION_TABLE__.get(X['__type__'], (0,0,0))
				elif isinstance(X, (tuple,list)):
					# so we can say self.set_min_version((<maj>,<min>,<mic>)) if a node feature is new (rather than the node itself)
					assert tuple(type(x) for x in X) == (int, int, int), 'invalid version format, must be (int, int, int): {}'.format(X)
					version = X
				else:
					raise TypeError('not a version', type(X))

				current = self.__snap_data__['version']
				if current is None:
					current = self.__snap_data__['version'] = [0,0,0]

				if current < list(version):
					current[:] = version

				self.changed(version=tuple(current))
				


		def decode_ast_elementXXX(self, AST_NODE):
			
			N = ORIGINAL = self.decode_ast_node(AST_NODE)

			#print('type', N['__type__'])

			with_span_info = self['with_span_info']
			if with_span_info:

				info = self.get_line_info(AST_NODE)
				if info is not None:
					N['__line_info__'] = info


			self['version'] = N

			if not self['generalized']:

				if with_span_info and self['preserve_spacing'] and 'body' in N:
					''#return add_spacing(N, self['text'])

				return N

			# https://docs.python.org/3/library/ast.html#root-nodes

			converter = getattr(self, 'convert_' + TYPE, None)
			if not converter:
				ENV.snap_warning('no converter for', repr(TYPE))
				raise NotImplementedError('convert_' + TYPE)
			else:
				N = converter(N)

			if with_span_info and self['preserve_spacing'] and 'body' in N:
				''#N = add_spacing(N, SETTINGS['__source_text__'])

			N['__original__'] = ORIGINAL.copy()

			return N


		def reset(self):
			self.__snap_data__['version'] = [0,0,0]
			self.__snap_data__['language'] = None
			del self.__snap_data__['text']

		def decode(self, TEXT, **SETTINGS):
			'text or filepath input'
			assert isinstance(TEXT, str), 'text input must be str'

			self.reset()

			self['text'] = TEXT
			self.__snap_data__['version'] = [0,0,0]

			self.set(**SETTINGS)

			tree = self.parse(TEXT)
			dec = self.decode_ast_node(tree)
			#if self['generalized']:
			#	dec = self.postprocess(dec)

			dec['__info__'] = {
				'version':self['version'], #tuple(self.__min_version__),
				'language':self['language'], #self.LANGUAGE_NAME,
			}

			self.reset()

			return dec

		# TODO decode_file()?

		def parse(self, TEXT):
			raise NotImplementedError() # should return ast structure in json format? XXX return in language format...  decode_element will turn it to json


	ENV.SnapProgrammingLanguageDecoder = SnapProgrammingLanguageDecoder
