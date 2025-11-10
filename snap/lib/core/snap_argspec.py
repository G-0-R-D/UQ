
# the docstring parser and connection negotiation logic

	
EBNF = """
NAME: 'A-Za-z_ 0-9'
INT: !'0' '0-9'*
ERROR: 'pass'

identifier: NAME ['|' NAME]*
required: '!'
optional: '?'
# support for: (6 * type) (type * 6) (*type)
premultiplied: (INT '*'|'*') type
postmultiplied: type '*' INT
type: identifier ['(' (premultiplied | postmultiplied | type) [',' type]* ')']
keyword_argument: identifier '=' (type | ERROR)
argument: type
term: (keyword_argument | argument) [required | optional]
set: '(' term [',' term]* (')' | ERROR)
return_value: type
return: '->' (return_value | ERROR)
statement: ('(' set [',' set]* ')' | set) [return]
"""

EBNF_C = """
WHITESPACE: *ignore in layer 1*
NAME: 'A-Za-z_ 0-9'
INT: 1-9 0-9*

slice: ':' INT | INT [':' INT]
enumerated: '[' [slice] ']'
nested: '(' type* ')'
type: NAME [enumerated] [nested] ['|' type]*
argument: type [NAME] ['!' | '?']
return_value: type
declaration: '(' [argument [',' argument]*] ')' ['->', return_value]
"""

"""
following c style:

type name, -> identified (by name)
type, -> positional

type can be:

type|type|... -> alternative types for name or position
type[int] -> a specific count of type (maybe even can be a range? [start:end]?) or [int+] to mean more than a number or [int-] to mean less than?
	-- like: "list[3](subtype)" but "list[3](*subtype)" would also be permissable?
type* -> which would mean a list of type, unidentified types cannot follow this declaration
	-- NOTE: like: "list(*subtype)" not "list*(subtype)"
	-- XXX don't use *, just use [] to mean any number of args?
		-- instead of list(*int|float) use int|float[] where list is implied... (and could be a tuple)
	TODO also support initializers like dict(keytype:valuetype)

	-- list(type) for when we actually care about it being a list, otherwise use type[]

type can also be complex?:
list(int,int)
list[int+](int|float|bool)

? -> means optional like: int var?
! -> means required like: int var!
	- neither means it should have a default if not provided, or can accept None as a value without issue

TODO put channel emit() docstring into the declaration itself?  SnapProperty|SnapChannel('(type name, ...)')
"""
EBNF_SPEC = """
#NAME: 'A-Za-z_ 0-9'
#UINT: 1-9 0-9*

slice: ':' UINT | UINT [':' UINT]
enumerator: '[' slice ']'
dict_args: '{' (':' type | type ':' [type] | ':') '}'
nested: '(' ['*'] [type [',' type]*] ')'
type: NAME [enumerator] [nested | dict_args] ['|' type]*
argument: type [NAME] ['!' | '?']
return: type
declaration: '(' [argument [',' argument]*] ')' ['->' return]
"""

def build(ENV):

	ENV.__build__('snap.lib.parsing.parseq')
	ENV.__build__('snap.lib.parsing.grammars')

	SnapEBNFDecoder = ENV.SnapEBNFDecoder

	ParseqLayer = ENV.ParseqLayer
	ParseqDecoder = ENV.ParseqDecoder

	ANY = ENV.ParseqANY
	AND = ENV.ParseqAND
	OR = ENV.ParseqOR
	REPEAT = ENV.ParseqREPEAT
	RANGE = ENV.ParseqRANGE

	ERROR = ENV.PARSEQ_ERROR

	ITEM = ENV.ParseqITEM
	ParseqLayerITEM = ENV.ParseqLayerITEM



	# TODO:SECURITY: make sure when save/load or other parsing systems are accessing names from the ENV that they are allowed to do so!  don't allow access to ENV.__PRIVATE__! --> can ENV hide that from user actually?

	class SnapArgSpecDecoder(ParseqDecoder):

		__slots__ = []

		def decode_result(self, RESULT):
			return RESULT

		def __init__(self):
			ParseqDecoder.__init__(self)

			declaration = SnapEBNFDecoder().decode(EBNF_SPEC, definitions = {k:ParseqLayerITEM(name=k) for k in (
					'NAME','UINT')})

			#print(declaration.items())

			items = [r for r in declaration.finditer_rules(_type=ITEM) if not isinstance(r, ParseqLayerITEM)]
			items = list(sorted( items, key=lambda i: (-len(i._value_), i._value_) )) # (length, or alphanumeric)

			# the ebnf grammar is for second pass, so it will match layer items returned by layer1
			swap = {id(r):ParseqLayerITEM(name=r.name()) for r in items}
			declaration.swap_rules(swapdict=swap)


			name_continue = OR(RANGE('A','Z'), RANGE('a','z'), RANGE('0','9'), '_')
			NAME = AND(OR(RANGE('A','Z'), RANGE('a','z'), '_'), REPEAT(name_continue, min=0, max=-1),
				name='NAME', capture=True)

			UINT = REPEAT(RANGE('0','9'), # number will be validated in decode_result
				name='UINT', capture=True)

			ignore = ANY(' ','\t', #NOT(NOTANY()),
				name='ignore', capture=False)

			for rule in declaration.finditer_rules():
				name = rule.name()
				#print(rule)
				if name is None:
					rule.set(capture=False, suppress=True)
				else:
					''#print('name', name, rule)

			declaration.print_tree()

			LAYER1 = ParseqLayer(items=[

				ANY(items=items, capture=False),

				NAME,
				UINT,

				ignore,
				ERROR,
				])

			self.set(
				sublayer=LAYER1,
				items=[
					declaration,
					ERROR,
				])


			

	ENV.SnapArgSpecDecoder = SnapArgSpecDecoder
	

def main(ENV):

	build(ENV)

	TESTS = [
		#'',
		#'()',
		'(type)',
		'(type name)',
		'(type name, type2 name2)',
		'(type[])',
		'(type[2])',
	]
	ERRORS = [
		'type', # no parens
	]

	ParseqSequence = ENV.ParseqSequence

	dec = ENV.SnapArgSpecDecoder()
	for test in TESTS:
		seq = ParseqSequence(source=test)
		seq.DEBUGGER = ENV.ParseqDebugger()
		#result = dec.sublayer().match_with_result(seq)
		#while result:
		#	print('result', result)
		#	result = dec.sublayer().match_with_result(seq)

		while 1:
			result = dec.match_with_result(seq)
			if result is None or result.name() == 'ERROR':
				break
			#elif result.name() == 'ERROR':
			#	print('closest', seq.DEBUGGER.__closest_match__)#closest_match())
			#print('result', result)

		break

	#ENV.snap_out('items', dec.items())

	ENV.__run_gui__(ENV.ParseqGrammarGraphic, rule=dec)
	

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())
