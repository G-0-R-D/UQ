
import ast, os, re
from base64 import b64encode

# https://docs.python.org/3/library/ast.html
# https://docs.python.org/3/reference/grammar.html

# https://docs.python.org/3/library/functions.html#compile
# https://docs.python.org/3/library/ast.html#ast.parse


NEWLINE_SCANNER = re.compile(r'\n')

def newline_indices(TEXT):
	# so we can remap newline coordinates into absolute span coordinates (much easier to work with, and smaller! (2 ints instead of 4))
	lines = {1:0}
	idx = 1
	for match in NEWLINE_SCANNER.finditer(TEXT):
		idx += 1
		lines[idx] = match.end()
	return lines

def add_spacing(NODE, TEXT):
	assert 'body' in NODE

	# TODO this could probably be generalized in the base class as it would always be true...?

	# TODO check the spans in the text for newlines between and insert {'__type__':'newline', 'count':x} for them

	return NODE


def build(ENV):

	SnapProgrammingLanguageDecoder = ENV.SnapProgrammingLanguageDecoder

	class SnapPythonLanguageDecoder(SnapProgrammingLanguageDecoder):

		__slots__ = []

		__VERSION_TABLE__ = {
			# this isn't an accurate history (though it could be ;)) this is just for basic feedback and analysis for compat
			# TODO do this by attempting a parse of 'everything.py' in different versions of python?
			# TODO can search the feature and 'pep' to find the version it was introduced...
			# https://peps.python.org/pep-0000/#finished-peps-done-with-a-stable-interface
			(0,0,0):['Module', 'Expression', 'Interactive', 'Constant',
					'List', 'Tuple', 'Set', 'Dict',
					'Name', 'Load', 'Store', 'Del',
					'Starred', # ? probably later than 0...
					'Expr',
					'UnaryOp', 'UAdd', 'USub', 'Not', 'Invert',
					'BinOp', 'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd',
					'BoolOp', 'And', 'Or',
					'Compare', 'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn',
					'Call', 'keyword', 'IfExp', 'Attribute', 'NamedExpr',
					'Subscript', 'Slice',
					'ListComp', 'SetComp', 'GeneratorExp', 'DictComp', 'comprehension',
					'Assign', 'AugAssign',
					'Raise', 'Assert', 'Delete',
					'Pass',
					'Import', 'ImportFrom',
					'If', 'For', 'While', 'Break', 'Continue', 'Try', 'ExceptHandler',
					'With', 'withitem',
					'FunctionDef', 'Lambda', 'arguments', 'arg', 'Return', 'Yield',
					'Global', 'Nonlocal',
					'ClassDef',
					],
			(3,3,0):['YieldFrom',],
			(3,5,0):['FunctionType',
					'FormattedValue', 'JoinedStr',
					'MatMult',
					'AnnAssign',
					'AsyncFunctionDef', 'Await', 'AsyncFor', 'AsyncWith'],
			(3,8,0):['TypeIgnore',], # TODO
			(3,10,0):['Match', 'match_case', 'MatchValue', 'MatchSingleton', 'MatchSequence', 'MatchStar', 'MatchMapping', 'MatchClass',
					'MatchAs', 'MatchOr'],
			(3,11,0):['TryStar'],
			(3,12,0):['TypeAlias',
					'TypeVar', 'ParamSpec', 'TypeVarTuple', # TODO: (3,13,0): added default_value param (each of these <-)
					],
			(3,14,0):['TemplateStr', 'Interpolation', ],
		}
		__VERSION_TABLE__ = {name:k for k,v in __VERSION_TABLE__.items() for name in v}


		@ENV.SnapProperty
		class __newline_index__:

			def get(self, MSG):
				"()->?"
				index = self.__snap_data__['__newline_index__']
				if index is None:
					text = self['text']
					assert isinstance(text, str), 'no text for index'
					index = self.__snap_data__['__newline_index__'] = newline_indices(text)
				return index

		@ENV.SnapProperty
		class language:
			def get(self, MSG):
				"()->str"
				return "python"

		# ROOT NODE:
		def convert_Module(self, N):
			N['__type__'] = 'module'
			N['body']
			return N

		def convert_Expression(self, N):
			# needs to be different than Expr below
			N['__type__'] = 'input_expression'
			N['body']
			return N

		def convert_Interactive(self, N):
			N['__type__'] = 'interactive'
			N['body']
			return N

		def convert_FunctionType(self, N): # v3.8+
			# NOTE: this is not FunctionDef, hopefully this isn't used anywhere
			N['__type__'] = 'function_type'
			#N['argtypes']
			#N['returns']
			return N

		# LITERALS:
		def convert_Constant(self, N):
			N['__type__'] = 'constant'
			value = N['value']
			if isinstance(value, bytes):
				N['value'] = b64encode(value).decode() # bytes as str (json encoded)
			N['data_type'] = {
				'int':'integer',
				'float':'floating_point',
				'str':'string',
				'bool':'boolean',
				'NoneType':'null',
				'bytes':'bytes',
				}[value.__class__.__name__]
			del N['kind'] # not even sure what this is, it's always None and isn't in the docs
			return N

		def convert_FormattedValue(self, N): # v3.8+
			N['__type__'] = 'formatted_value'
			#N['value']
			#N['conversion']
			#N['format_spec']

			# TODO remap this to a 'call' to py_fmt_str() implemented in snap.h? XXX make it user level, so it's just a call to a name (from ENV / builtins)
			return N

		def convert_JoinedStr(self, N): # v3.8+
			N['__type__'] = 'joined_string'
			#N['values']
			return N

		def convert_TemplateStr(self, N):
			# TODO
			raise NotImplementedError(N['__type__'])

		def convert_Interpolation(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_List(self, N):
			N['__type__'] = 'list'
			N['items'] = N.pop('elts')
			N['context'] = N.pop('ctx')
			return N

		def convert_Tuple(self, N):
			N['__type__'] = 'tuple'
			N['items'] = N.pop('elts')
			N['context'] = N.pop('ctx')
			return N

		def convert_Set(self, N):
			N['__type__'] = 'set'
			N['items'] = N.pop('elts')
			return N

		def convert_Dict(self, N):
			N['__type__'] = 'dictionary'
			assert len(N['keys']) == len(N['values']), 'bad dict?'
			return N

		# VARIABLES:
		def convert_Name(self, N):
			N['__type__'] = 'name'
			N['value'] = N.pop('id')
			N['context'] = N.pop('ctx')
			return N

		def convert_Load(self, N):
			N['__type__'] = 'load'
			return N

		def convert_Store(self, N):
			N['__type__'] = 'store'
			return N

		def convert_Del(self, N):
			N['__type__'] = 'remove' # renamed to prevent confusion with del statement which is separate!
			return N

		def convert_Starred(self, N):
			N['__type__'] = 'starred'
			N['context'] = N.pop('ctx')
			N['value']
			return N

		# EXPRESSIONS:
		def convert_Expr(self, N):
			N['__type__'] = 'expression'
			N['value']
			return N

		def convert_UnaryOp(self, N):
			N['__type__'] = 'unary_operation'
			N['operator'] = N.pop('op')
			N['operand']
			return N

		def convert_UAdd(self, N):
			N['__type__'] = 'unary_add'
			return N

		def convert_USub(self, N):
			N['__type__'] = 'unary_subtract'
			return N

		def convert_Not(self, N):
			N['__type__'] = 'not'
			return N

		def convert_Invert(self, N):
			N['__type__'] = 'bitwise_invert' # ones compliment in binary
			return N

		def convert_BinOp(self, N):
			N['__type__'] = 'binary_operation'
			N['operator'] = N.pop('op')
			N['left']
			N['right']
			return N

		def convert_Add(self, N):
			N['__type__'] = 'add'
			return N

		def convert_Sub(self, N):
			N['__type__'] = 'subtract'
			return N

		def convert_Mult(self, N):
			N['__type__'] = 'multiply'
			return N

		def convert_Div(self, N):
			N['__type__'] = 'divide'
			return N

		def convert_FloorDiv(self, N):
			N['__type__'] = 'floor_divide'
			return N

		def convert_Mod(self, N):
			N['__type__'] = 'modulo'
			return N

		def convert_Pow(self, N):
			N['__type__'] = 'power'
			return N

		def convert_LShift(self, N):
			N['__type__'] = 'bitwise_left_shift'
			return N

		def convert_RShift(self, N):
			N['__type__'] = 'bitwise_right_shift'
			return N

		def convert_BitOr(self, N):
			N['__type__'] = 'bitwise_or'
			return N

		def convert_BitXor(self, N):
			N['__type__'] = 'bitwise_xor'
			return N

		def convert_BitAnd(self, N):
			N['__type__'] = 'bitwise_and'
			return N

		def convert_MatMult(self, N):
			# https://stackoverflow.com/questions/27385633/what-is-the-symbol-for-in-python
			# a @ b is matrix multiplication?
			raise NotImplementedError("@ matrix multiplication") # TODO report line info
			N['__type__'] = 'matrix_multiply'
			return N

		def convert_BoolOp(self, N):
			N['__type__'] = 'bool_operation'
			N['operator'] = N.pop('op')
			N['values']
			return N

		def convert_And(self, N):
			N['__type__'] = 'and'
			return N

		def convert_Or(self, N):
			N['__type__'] = 'or'
			return N

		def convert_Compare(self, N):
			N['__type__'] = 'comparison'
			N['operators'] = N.pop('ops')
			N['values'] = N.pop('comparators')
			N['left']
			return N

		def convert_Eq(self, N):
			N['__type__'] = 'equal'
			return N

		def convert_NotEq(self, N):
			N['__type__'] = 'not_equal'
			return N

		def convert_Lt(self, N):
			N['__type__'] = 'less_than'
			return N

		def convert_LtE(self, N):
			N['__type__'] = 'less_or_equal'
			return N

		def convert_Gt(self, N):
			N['__type__'] = 'greater_than'
			return N

		def convert_GtE(self, N):
			N['__type__'] = 'greater_or_equal'
			return N

		def convert_Is(self, N):
			N['__type__'] = 'is'
			return N

		def convert_IsNot(self, N):
			N['__type__'] = 'is_not'
			return N

		def convert_In(self, N):
			N['__type__'] = 'in'
			return N

		def convert_NotIn(self, N):
			N['__type__'] = 'not_in'
			return N

		def convert_Call(self, N):
			N['__type__'] = 'call'
			N['base'] = N.pop('func')
			N['arguments'] = N.pop('args')
			N['keyword_arguments'] = N.pop('keywords')
			return N

		def convert_keyword(self, N):
			N['__type__'] = 'keyword'
			N['key'] = N.pop('arg')
			N['value']
			return N

		def convert_IfExp(self, N):
			N['__type__'] = 'if_expression'
			N['if'] = N.pop('test')
			N['body']
			N['else'] = N.pop('orelse')
			return N

		def convert_Attribute(self, N):
			N['__type__'] = 'attribute'
			N['attribute'] = N.pop('attr')
			N['context'] = N.pop('ctx')
			N['value']
			return N

		def convert_NamedExpr(self, N):
			N['__type__'] = 'named_expression'
			N['target']
			N['value']
			return N

		# SUBSCRIPTING:
		def convert_Subscript(self, N):
			N['__type__'] = 'subscript'
			N['base'] = N.pop('value')
			N['key'] = N.pop('slice')
			N['context'] = N.pop('ctx')
			return N

		def convert_Slice(self, N):
			N['__type__'] = 'slice'
			N['start'] = N.pop('lower')
			N['end'] = N.pop('upper')
			N['step']
			return N

		# COMPREHENSIONS:
		def convert_ListComp(self, N):
			N['__type__'] = 'list_comprehension'
			N['item'] = N.pop('elt')
			N['generators']
			return N

		def convert_SetComp(self, N):
			N['__type__'] = 'set_comprehension'
			N['item'] = N.pop('elt')
			N['generators']
			return N

		def convert_GeneratorExp(self, N):
			N['__type__'] = 'generator_comprehension'
			N['item'] = N.pop('elt')
			N['generators']
			return N

		def convert_DictComp(self, N):
			N['__type__'] = 'dictionary_comprehension'
			N['key']
			N['value']
			N['generators']
			return N

		def convert_comprehension(self, N):
			N['__type__'] = 'comprehension'
			N['for'] = N.pop('target')
			N['in'] = N.pop('iter')
			N['ifs']
			N['asynchronous'] = bool(N.pop('is_async'))
			return N

		# STATEMENTS:
		def convert_Assign(self, N):
			N['__type__'] = 'assign'
			N['targets']
			N['value']
			#N['type_comment']
			return N

		def convert_AnnAssign(self, N):
			N['__type__'] = 'annotated_assign'
			N['target']
			#N['annotation']
			N['value']
			N['simple'] = bool(N['simple']) # simple target is just one 'Name'
			return N

		def convert_AugAssign(self, N):
			N['__type__'] = 'augmented_assign'
			N['target']
			N['operator'] = N.pop('op')
			N['value']
			return N

		def convert_Raise(self, N):
			N['__type__'] = 'raise'
			N['exception'] = N.pop('exc')
			# https://stackoverflow.com/a/24752607
			N['from'] = N.pop('cause')
			return N

		def convert_Assert(self, N):
			N['__type__'] = 'assert'
			N['test']
			N['message'] = N.pop('msg')
			return N

		def convert_Delete(self, N):
			N['__type__'] = 'delete'
			N['targets']
			return N

		def convert_Pass(self, N):
			N['__type__'] = 'pass'
			return N

		def convert_TypeAlias(self, N):
			N['__type__'] = 'type_alias'
			#N['name']
			#N['type_params']
			#N['value']
			return N

		# IMPORTS:
		def convert_Import(self, N):
			N['__type__'] = 'import'
			N['names']
			return N

		def convert_ImportFrom(self, N):
			N['__type__'] = 'import_from'
			N['module']
			N['names']
			N['level'] # this is count of preceding dots as in from ..x import ... would be 2 dots before x so 2
			return N

		def convert_alias(self, N):
			N['__type__'] = 'import_alias'
			N['name']
			if 'asname' in N:
				# https://peps.python.org/pep-0221/
				N['as'] = N.pop('asname')
				self['version'] = (2,0,0)
			return N

		# CONTROL FLOW:
		def convert_If(self, N):
			N['__type__'] = 'if'
			N['test']
			N['body']
			N['else'] = N.pop('orelse')
			return N

		def convert_For(self, N):
			N['__type__'] = 'for'
			N['target']
			N['in'] = N.pop('iter')
			N['body']
			N['else'] = N.pop('orelse')
			#N['type_comment']
			return N

		def convert_While(self, N):
			N['__type__'] = 'while'
			N['test']
			N['body']
			N['else'] = N.pop('orelse')
			return N

		def convert_Break(self, N):
			N['__type__'] = 'break'
			return N

		def convert_Continue(self, N):
			N['__type__'] = 'continue'
			return N

		def convert_Try(self, N):
			N['__type__'] = 'try'
			N['body']
			N['exceptions'] = N.pop('handlers')
			N['else'] = N.pop('orelse')
			N['finally'] = N.pop('finalbody')
			return N

		def convert_TryStar(self, N):
			# https://stackoverflow.com/a/77177924
			N['__type__'] = 'try_star'
			#N['body']
			#N['exceptions'] = N.pop('handlers')
			#N['else'] = N.pop('orelse')
			#N['finally'] = N.pop('finalbody')
			return N

		def convert_ExceptHandler(self, N):
			N['__type__'] = 'exception'
			N['type']
			N['as'] = N.pop('name')
			N['body']
			return N

		def convert_With(self, N):
			N['__type__'] = 'with'
			N['items']
			N['body']
			#N['type_comment']
			return N

		def convert_withitem(self, N):
			N['__type__'] = 'with_item'
			N['expression'] = N.pop('context_expr')
			N['as'] = N.pop('optional_vars')
			return N

		# PATTERN MATCHING: TODO v3.8+
		def convert_match_case(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchValue(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchSingleton(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchSequence(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchStar(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchMapping(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchClass(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchAs(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_MatchOr(self, N):
			raise NotImplementedError(N['__type__'])

		# TYPE ANNOTATIONS: TODO v3.8+

		def convert_TypeIgnore(self, N):
			raise NotImplementedError(N['__type__'])

		# TYPE PARAMETERS: TODO v3.8+
		def convert_TypeVar(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_ParamSpec(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_TypeVarTuple(self, N):
			raise NotImplementedError(N['__type__'])

		# FUNCTION AND CLASS DEFINITIONS:
		def convert_FunctionDef(self, N):
			N['__type__'] = 'function_definition'
			N['name']
			N['arguments'] = N.pop('args')['values']
			N['body']
			N['decorators'] = N.pop('decorator_list')
			del N['returns']
			if 'type_params' in N:
				self['version'] = (3,1,2)
			return N

		def convert_Lambda(self, N):
			N['__type__'] = 'lambda'
			N['arguments'] = N.pop('args')
			N['body']
			return N

		def convert_arguments(self, N):
			N['__type__'] = 'arguments'

			# https://docs.python.org/3/library/ast.html#ast.arguments
			# switching to a flat list of args with attributes attached, rather than whatever it is that's going on here!

			args = N['values'] = []

			posonlyargs = N.pop('posonlyargs')
			idx = 0
			for arg in posonlyargs:
				# In Python 3.8, all arguments before '/' must be specified by position
				arg['special_request'] = 'positional_only' # XXX just flag positional_only = True, and ignore it if unused...
				args.append(arg)
				idx += 1

			if N['args']:
				gather = N['args']
				args.extend(gather)
				# defaults are values for positional arguments, "if there are fewer defaults, they correspond to the last n arguments"
				defaults = N['defaults']
				if defaults:
					gather = gather[-len(defaults):]
					assert len(gather) == len(defaults)
					for arg,default in zip(gather, defaults):
						arg['value'] = default
			
			if N['vararg']:
				arg = N['vararg']
				arg['unpack'] = 'LIST'
				args.append(arg)

			idx = 0
			for arg in N['kwonlyargs']:
				# Any argument after '*' must be specified using a keyword
				arg['special_request'] = 'keyword_only'
				args.append(arg)
				if N['kw_defaults'][idx] is None:
					arg['value'] = None
				else:
					arg['value'] = N['kw_defaults'][idx]
				idx += 1


			if N['kwarg']:
				arg = N['kwarg']
				arg['unpack'] = 'DICTIONARY'
				args.append(arg)
			
			#assert args, 'empty arguments'

			del N['args']
			del N['defaults']
			del N['vararg']
			del N['kwarg']
			del N['kwonlyargs']
			del N['kw_defaults']

			return N

		def convert_arg(self, N):
			N['__type__'] = 'argument'
			N['name'] = N.pop('arg')
			#N['annotation']
			#N['type_comment']
			return N

		def convert_Return(self, N):
			N['__type__'] = 'return'
			N['value']
			return N

		def convert_Yield(self, N):
			N['__type__'] = 'yield'
			N['value']
			return N

		def convert_YieldFrom(self, N):
			N['__type__'] = 'yield_from'
			N['value']
			return N

		def convert_Global(self, N):
			N['__type__'] = 'global'
			N['names'] # list of str
			return N

		def convert_Nonlocal(self, N):
			N['__type__'] = 'non_local'
			N['names'] # list of str
			return N

		def convert_ClassDef(self, N):
			N['__type__'] = 'class_definition'
			N['name']
			N['bases']
			N['keywords']
			N['body']
			N['decorators'] = N.pop('decorator_list')
			if 'type_params' in N:
				self['version'] = (3,1,2)
			return N


		# TODO Async
		# https://stackoverflow.com/questions/49005651/how-does-asyncio-actually-work
		def convert_AsyncFunctionDef(self, N):
			# TODO version 3,1,2: type_params
			raise NotImplementedError(N['__type__'])

		def convert_Await(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_AsyncFor(self, N):
			raise NotImplementedError(N['__type__'])

		def convert_AsyncWith(self, N):
			raise NotImplementedError(N['__type__'])




		def decode_ast_node(self, AST_NODE):

			if not isinstance(AST_NODE, ast.AST):
				#print('not ast', AST_NODE)
				return AST_NODE # assume raw data type like a string or None or something (global and nonlocal use this for names which is a list of str)

			N = ORIGINAL = {}
			TYPE = N['__type__'] = AST_NODE.__class__.__name__

			for field in getattr(AST_NODE, '_fields', []):
				value = getattr(AST_NODE, field)

				if isinstance(value, list):
					N[field] = [self.decode_ast_node(e) for e in value]
				elif isinstance(value, ast.AST):
					N[field] = self.decode_ast_node(value)
				elif isinstance(value, (str, bytes, float, int, bool)) or value is None:
					N[field] = value
				else:
					raise TypeError('miss', type(value), field, value.__class__.mro())

			for attr in getattr(AST_NODE, '_attributes', []):
				if attr in (
					'lineno', 'end_lineno', 'col_offset', 'end_col_offset'):
					continue
				ENV.snap_warning('ignore attr', N['__type__'], repr(attr))

			if TYPE in ('FunctionDef', 'AsyncFunctionDef', 'ClassDef', 'Module'):
				doc = ast.get_docstring(AST_NODE, clean=False)
				if doc is not None:
					#print('docstring!', TYPE, N, repr(doc))
					N['documentation'] = {'__type__':'str', 'value':doc}

			#if 

			#print('type', N['__type__'])

			with_span_info = self['with_span_info']
			if with_span_info:

				lineno = getattr(AST_NODE, 'lineno', None)
				if lineno is not None:
					col_offset = getattr(AST_NODE, 'col_offset', None)
					end_lineno = getattr(AST_NODE, 'end_lineno', None)
					end_col_offset = getattr(AST_NODE, 'end_col_offset', None)

					NEWLINES = self['__newline_index__']

					N['__line_info__'] = {'span':[NEWLINES[lineno] + col_offset, NEWLINES[end_lineno] + end_col_offset]}

					# TODO either make this just a span in absolute coordinates, or indicate the line start and then the span relative to that...
					# TODO just store the span?  we can always scan for lines
					#	-- pre-parse the input for line counts, put them in dict, then just access them for a total index offset we can use to get the absolute span coordinates...

					"""
					#print(lineno, end_lineno, col_offset, end_col_offset)
					if lineno is not None and end_lineno is not None:
						lineinfo['lines'] = [lineno, end_lineno]

					if col_offset is not None and end_col_offset is not None:
						lineinfo['columns'] = [col_offset, end_col_offset]

					if lineinfo:
						N['__line_info__'] = lineinfo
					"""


			self['version'] = N

			if with_span_info and self['preserve_spacing'] and 'body' in N:
				''#N =  add_spacing(N, self['text'])

			if self['generalized']:

				ORIGINAL = N.copy()

				# https://docs.python.org/3/library/ast.html#root-nodes

				converter = getattr(self, 'convert_' + TYPE, None)
				if not converter:
					ENV.snap_warning('no converter for', repr(TYPE))
					raise NotImplementedError('convert_' + TYPE)
				else:
					N = converter(N)

				#N['__original__'] = ORIGINAL

			return N

	

		def parse(self, TEXT):
			return ast.parse(TEXT, '<string>')


	ENV.SnapPythonLanguageDecoder = SnapPythonLanguageDecoder

def main(ENV):

	import json

	#ENV.__build__('snap.lib.programming.language.SnapProgrammingLanguageDecoder')
	build(ENV)

	dec = ENV.SnapPythonLanguageDecoder()
	with open(__file__, 'r') as openfile:
		j = dec.decode(openfile.read())

	print(json.dumps(j, indent=4))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

