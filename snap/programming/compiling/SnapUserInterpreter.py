
# same as SnapUserCompiler, but instead of compiling to c, this maps to the opcodes directly
#	-- this will be compiled into c... 

# https://docs.python.org/3/library/operator.html
from operator import (
	# TODO these will need to be implemented by the c api, but will work in python for now!
	# XXX make c backend, these will be the ops, with implementation in c...
	lt as less_than,
	le as less_or_equal,
	eq as equal,
	ne as not_equal,
	ge as greater_or_equal,
	gt as greater_than,

	add, sub, mul, truediv, floordiv,
	mod, pow,
	lshift, rshift, or_, xor, and_, invert,
	not_, truth, is_, is_not,
	neg, pos,
	
	)

# https://realpython.com/cpython-source-code-guide/#core-compilation-process
# https://docs.python.org/3/library/dis.html#python-bytecode-instructions
# Python/compile.c
# https://github.com/python/cpython/blob/d93605de7232da5e6a182fd1d5c220639e900159/Python/compile.c

# TODO use ENV['__interpreter__'] to store stack and other state info, implement c functions for each operation, try to follow the compiled api as much as possible so they look the same

# TODO this needs to be written as a python program!  then we can compile it into a c program and it will be able to take ast input and run it in c...

def type_module(ENV, NODE):
	'this just begins evaluation of the module, so start queueing up the body'

# type_input_expression
# type_interactive
# type_function_type

def type_constant(ENV, NODE):
	'' # TODO creates a constant value (how to pass it back?) TODO just pass it back from this function!  and register it into ENV gc before doing so...

# type_formatted_value
# type_joined_string




# TODO init ENV['__interpreter__'] ?


# TODO make a function for each statement type, assign to dict, get from dict using ast '__type__'


class SnapInterpreter(object):

	# TODO write this as if 'interpreting' python to python, and then compile it with the SnapCCompiler :)

	__slots__ = []

	@property
	def ENV(self):
		# TODO keep a stack of ENV, return the current one
		raise NotImplementedError()


	def preprocess(self, NODE):
		''

	# this is kinda following compiler_visit_stmt in Python/compile.c
	# https://github.com/python/cpython/blob/d93605de7232da5e6a182fd1d5c220639e900159/Python/compile.c
	def interpret(self, NODE):
		'evaluate ast NODE' # TYPES[NODE['__type__']](ENV, NODE)


		TYPE = NODE['__type__']

		# ROOT NODES:
		if TYPE == 'module': # TODO
			
			for node in NODE['body']:
				self.interpret(node) # TODO make new sub env?

		elif TYPE == 'input_expression':
			raise NotImplementedError(TYPE)
		elif TYPE == 'interactive':
			raise NotImplementedError(TYPE)
		elif TYPE == 'function_type':
			raise NotImplementedError(TYPE)

		# LITERALS:
		elif TYPE == 'constant':
			#value = NODE['value']
			return NODE['value'] # ? ast value will already be the correct type...?
			"""
			# TODO str, bytes, int, float, complex, and bool, and the constants None and Ellipsis.
			if isinstance(value, str):
				# TODO if is a legal name then return as CSTR_<name> and register the constant string with CTX
				yield '_str("' + ''.join(['\\'+c if c == '"' else c for c in value]) + '")' # TODO independent lines...
			elif isinstance(value, bytes):
				yield '_bytes("' + repr(value)[2:-1] + '", ' + str(len(value)) + ')'
			elif isinstance(value, int):
				# bool isn't the right type??
				text = str(value)
				if text == 'True':
					yield CTX.INDENT() + '_bool(1)'
				elif text == 'False':
					yield CTX.INDENT() + '_bool(0)'
				else:				
					yield '_int(' + str(value) + ')'
			elif isinstance(value, float):
				yield '_float(' + str(value) + ')'
			elif isinstance(value, complex):
				raise NotImplementedError('complex numbers not yet mapped', repr(value))
			elif isinstance(value, bool):
				yield '_bool(' + str(int(value)) + ')'
			elif value is None:
				yield 'NULL' # ?
			# ellipsis is deprecated; current ast.parse doesn't even allow it.
			else:
				raise NotImplementedError('constant type', type(value))
			"""
		elif TYPE == 'formatted_value': # v3.8+
			raise NotImplementedError(TYPE)
		elif TYPE == 'joined_string': # v3.8+
			raise NotImplementedError(TYPE)

		elif TYPE in ('list', 'tuple', 'set'):

			# NOTE: garbage collection is handled automatically by either python or c implementation when type is instantiated...

			if TYPE == 'list':
				t = list
			elif TYPE == 'tuple':
				t = tuple
			elif TYPE == 'set':
				t = set
			else:
				raise TypeError(TYPE)

			items = NODE['items']
			if items:
				return t([interpret(ENV, item) for item in items])
			else:
				return t()

		elif TYPE == 'dict':
			# TODO try '{"a":1, **d}'

			# TODO ** keys?  key is None and then value is name to unpack...

			d = dict()
			if NODE['keys'] or NODE['values']:
				assert len(NODE['keys']) == len(NODE['values'])
				for key,value in zip(NODE['keys'], NODE['values']):
					if key is None:
						d.update(interpret(ENV, value)) # dict type?
					else:
						key = interpret(ENV, key)
						value = interpret(ENV, value)
						d[key] = value
				#return {interpret(ENV, k):interpret(ENV, v) for k,v in zip(NODE['keys'], NODE['values'])}
			else:
				return d

		# VARIABLES:
		elif TYPE == 'name': # TODO need to work out set() and del() since they are more complex, get() works pretty well though...
			name = NODE['value']
			context = NODE['context']['__type__']
			# TODO keep the attr design?
			return name # ?
			"""
			if context == 'load':
				yield CTX.INDENT() + '_get(ENV, _str("' + name + '"))'
			elif context == 'store':
				# TODO this would need to have the value to assign...
				#yield CTX.INDENT() + '_set(ENV, _str("' + name + '"))'
				yield CTX.INDENT() + '_str("' + name + '")'
			elif context == 'remove':
				#yield CTX.INDENT() + '_del(ENV, _str("' + name + '"))'
				yield CTX.INDENT() + '_str("' + name + '")'
			else:
				raise NameError('unknown context', repr(context))
			"""
			# this prevents us from having to consider the context until evaluation (so set,get,del get the same argument: _attr)
			#yield CTX.INDENT() + '_attr(ENV, "' + name + '")'
		elif TYPE == 'load':
			raise NotImplementedError(TYPE)
		elif TYPE == 'store':
			raise NotImplementedError(TYPE)
		elif TYPE == 'remove':
			raise NotImplementedError(TYPE)
		elif TYPE == 'starred': # TODO?
			#print('starred', NODE.keys())
			# _item(_slice(NULL, NULL, NULL))
			''#yield CTX.INDENT() + '_iter(' + fully_encode(NODE['value']) + ')'
			def iter(): # TODO ?
				for value in NODE['value']:
					yield interpret(ENV, value)
			return iter

		# EXPRESSIONS:
		elif TYPE == 'expression': # TODO?  probably just a passthrough
			# https://docs.python.org/3/library/ast.html#ast.Expr
			# this is used when return value isn't used or stored; statement by itself

			return interpret(ENV, NODE['value'])

			"""
			if NODE['value']['__type__'] == 'call' and NODE['value']['base']['__type__'] == 'name' and NODE['value']['base']['value'] == 'snap_raw':
				args = NODE['value']['arguments']
				assert len(args) == 1 and args[0]['__type__'] == 'constant' and isinstance(args[0]['value'], str), 'snap_raw must be given single string argument'
				#yield CTX.INDENT() + args[0]['value']
			else:
				''#yield CTX.INDENT() + '_DISCARD('
				#yield fully_encode(NODE['value'])
				#yield ');'
			"""
		elif TYPE == 'unary_operation':
			op = interpret(ENV, NODE['operator'])
			return op(interpret(ENV, NODE['operand']))
			''#yield CTX.INDENT() + '_unary_op(' + operator + ', ' + operand + ')'
		elif TYPE == 'unary_add':
			''#yield '"+"'
			return pos
		elif TYPE == 'unary_subtract':
			''#yield '"-"'
			return neg
		elif TYPE == 'not':
			''#yield '"not"'
			return not_
		elif TYPE == 'invert':
			''#yield '"invert"'
			return invert
		elif TYPE == 'binary_operation':
			op = interpret(ENV, NODE['operator'])
			left = interpret(ENV, NODE['left'])
			right = interpret(ENV, NODE['right'])
			# TODO if left/right are string constants then we need to _get(ENV, left/right)
			''#yield CTX.INDENT() + '_binary_op(' + left + ', ' + operator + ', ' + right + ')'
			return op(left, right)
		elif TYPE == 'add':
			''#yield '"+"'
			return add
		elif TYPE == 'subtract':
			''#yield '"-"'
			return sub
		elif TYPE == 'multiply':
			''#yield '"*"'
			return mul
		elif TYPE == 'divide':
			''#yield '"/"'
			return truediv
		elif TYPE == 'floor_divide':
			''#yield '"//"'
			return floordiv
		elif TYPE == 'modulo':
			''#yield '"%"'
			return mod
		elif TYPE == 'power':
			''#yield '"**"'
			return pow
		elif TYPE == 'bitwise_left_shift':
			''#yield '"<<"'
			return lshift
		elif TYPE == 'bitwise_right_shift':
			''#yield '">>"'
			return rshift
		elif TYPE == 'bitwise_or':
			''#yield '"|"'
			return or_
		elif TYPE == 'bitwise_xor':
			''#yield '"^"'
			return xor
		elif TYPE == 'bitwise_and':
			''#yield '"&"'
			return and_
		elif TYPE == 'matrix_multiply':
			raise NotImplementedError(TYPE)
		elif TYPE == 'bool_operation':
			operator = fully_encode(NODE['operator']) # one of: or, and
			# TODO items
			values = NODE['values']
			value_list = ', '.join([fully_encode(v) for v in values])
			''#yield '_bool_op(ENV, ' + operator + ', _a' + str(len(values)) + '(' + value_list + '))'# -> SnapBool # or, and, all consecutive type'
		elif TYPE == 'and':
			''#yield '"and"' # TODO make a function for and(a,b) that does: return a and b
			def both(a,b):
				return a and b
			return both
		elif TYPE == 'or':
			''#yield '"or"'
			def either(a,b):
				return a or b
			return either
		elif TYPE == 'comparison': # TODO
			# break into series of single comparisons? ops,values
			# TODO mostly the values would be from the ENV...  unless they are constants...
			''#yield 'compare(...)'

			# TODO if single then compare directly otherwise make special function the will call each and return the answer...

		elif TYPE == 'equal':
			''#yield '"=="'
			return equal
		elif TYPE == 'not_equal':
			''#yield '"!="'
			return not_equal
		elif TYPE == 'less_than':
			''#yield '"<"'
			return less_than
		elif TYPE == 'less_or_equal':
			''#yield '"<="'
			return less_or_equal
		elif TYPE == 'greater_than':
			''#yield '">"'
			return greater_than
		elif TYPE == 'greater_or_equal':
			''#yield '">="'
			return greater_or_equal
		elif TYPE == 'is':
			''#yield '"is"'
			return is_
		elif TYPE == 'is_not':
			''#yield '"is not"'
			return is_not
		elif TYPE == 'in':
			''#yield '"in"'
			def contains(a, b):
				return a in b
			return contains
		elif TYPE == 'not_in':
			''#yield '"not in"'
			def not_contains(a, b):
				return a not in b
			return not_contains
		elif TYPE == 'call': # TODO

			# TODO XXX this needs to create new env, assign vars to env, and push eval to the context

			args = []
			kwargs = {}

			if NODE['arguments']:
				for arg in NODE['arguments']:
					if arg['__type__'] == 'starred':
						# unpack
						args.extend(interpret(ENV, arg))
					else:
						args.append(interpret(ENV, arg))

			if NODE['keyword_arguments']:
				for kwarg in NODE['keyword_arguments']:
					if kwarg['key'] is None:
						# unpack
						kwargs.update(interpret(ENV, kwarg['value']))
					else:
						kwargs.append(interpret(ENV, kwarg))

			"""
			if NODE['arguments'] or NODE['keyword_arguments']:
					
				next_ctx = CTX.subcontext(indent_level=0)
				args = []
				unpack_arg = 'NULL'
				for arg in NODE['arguments']:
					if arg['__type__'] == 'starred':
						unpack_arg = fully_encode(arg)
					else:
						args.append(fully_encode(arg))
				if not args:
					args = 'NULL'
				else:
					args = '_a'+str(len(args)) + '(' +  ', '.join(args) + ')'

				kwargs = []
				unpack_kwargs = 'NULL'
				for kwarg in NODE['keyword_arguments']:
					if kwarg['key'] is None:
						unpack_kwargs = fully_encode(kwarg['value'])
					else:
						#print('kwarg', kwarg)
						kwargs.append(fully_encode(kwarg))
				if not kwargs:
					kwargs = 'NULL'
				else:
					kwargs = '_k' + str(len(kwargs)) + '(' + ', '.join(kwargs) + ')'
				msg = '_msg(' + args + ', ' + unpack_arg + ', ' + kwargs + ', ' + unpack_kwargs + ')'
			else:
				msg = 'NULL'
			"""

			base_element = interpret(ENV, NODE['base'])

			return base_element.__call__(*args, **kwargs)
				
				#yield CTX.INDENT() + '_call(' + base_element + ', ' + msg + ')'
			#if NODE['base'] == 'snap_raw':
			#	'get string and yield it as is (but remove indent, start at current level?)'
			#	yield CTX.INDENT() + '/*TODO:snap_raw*/'
			#else:
			#	yield CTX.INDENT() + 'call(ENV, INSTANCE, ATTR, ARGS, KWARGS)'# -> SnapObject (basically a method call of instance)'
		elif TYPE == 'keyword': # TODO
			# this is a keyword for an argument list (as in kwargs; key:value pairs)
			key = NODE['key'] # already a str
			value = interpret(ENV, NODE['value'])
			#yield CTX.INDENT() + key + ', ' + value
			return key, value
		elif TYPE == 'if_expression': # TODO
			#* create a c function call to represent the body of each section
			#	** unpack single else: if into else if at same level...
			''#yield CTX.INDENT() + '(if (...){} else {})' # TODO just use c if else and (else if)
		elif TYPE == 'attribute':
			#print('attribute value', NODE['value'])
			base = interpret(ENV, NODE['value']) # TODO base = interpret(NODE['value']) ?
			attr = NODE['attribute']
			if 0:#NODE['value']['__type__'] == 'name':
				# first access if from ENV
				base_stmt = '_attr(ENV, ' + base + ')'
			else:
				# all other accesses are from whatever the previous base return was
				base_stmt = base
			#yield '_attr(' + base_stmt + ', _str("' + attr + '"))'
		elif TYPE == 'named_expression': # v3.8+
			raise NotImplementedError(TYPE)

		# SUBSCRIPTING:
		elif TYPE == 'subscript': # TODO
			# call(ENV, INSTANCE, "__getitem__", ARGS[0] = SnapSlice()) ?
			# TODO get base from ENV?  call __getitem__(KEY)
			target = interpret(ENV, NODE['base'])
			key = interpret(ENV, NODE['key']) # TODO this just initiates a new slice() instance for each in the source, and returns it or passes it to base.__getitem__ and returns that?

			# TODO return _item(target, key) ?
			
			#yield CTX.INDENT() + '_item(' + target + ', ' + key + ')'
		elif TYPE == 'slice': # TODO
			keys = []
			for attr in ('start','end','step'):
				x = NODE[attr]
				if x is None:
					keys.append(None)
				else:
					keys.append(interpret(ENV, x)) # anything can be used as a slice param...
			return slice(*keys)

		# COMPREHENSIONS:
		elif TYPE == 'list_comprehension': # TODO
			''#yield CTX.INDENT() + 'ListCompr(ENV, ...)' # TODO access the list_comprehension from c api by assigning api wrappers to the ENV['__internal__']?
			def list_comprehension():
				return 'the comprehension' # TODO
			return list_comprehension()
		elif TYPE == 'set_comprehension': # TODO
			''#yield CTX.INDENT() + 'SetCompr(ENV, ...)'
		elif TYPE == 'generator_expression': # TODO
			''#yield CTX.INDENT() + 'GenCompr(ENV, ...)'
			#** have to create iterable class to represent the generator...
		elif TYPE == 'dictionary_comprehension': # TODO
			''#yield CTX.INDENT() + 'DictCompr(ENV, ...)'
		elif TYPE == 'comprehension': # TODO
			''#yield CTX.INDENT() + 'Compr(...)' # for, in...  return an iterable?  so define new iterable type and return the instance of it

		# STATEMENTS:
		elif TYPE == 'assign':
			for sub in NODE['targets']:
				for root in walk_tree(sub): # TODO only check NODE['targets']
					if root[-1]['__type__'] == 'name':
						# for from import, need to know global names # TODO only if body is toplevel?
						CTX.register_ENV_name(root[-1]['value'])

			#print('targets', [n['__type__'] for n in NODE['targets']])
			len_targets = len(NODE['targets'])
			targets = ', '.join([fully_encode(e) for e in NODE['targets']])
			value = fully_encode(NODE['value'])
			# TODO multiple targets need to be merged, but how to know they are multiple and not unpacked?  make separate _assign_multi?
			if len_targets > 1:
				targets = '_a' + str(len_targets) + '(' + targets + ')'
			#yield CTX.INDENT() + '_assign(' + targets + ', ' + value + ')'
			#-- value is SnapObject

		elif TYPE == 'annotated_assign': # 3.8+
			raise NotImplementedError(TYPE)

		elif TYPE == 'augmented_assign':
			target = NODE['target']
			assert target['__type__'] == 'name', 'only names supported for augassign right now {}'.format(target['__type__'])
			name = target['value']
			op = fully_encode(NODE['operator'])
			value = fully_encode(NODE['value'])
			#yield CTX.INDENT() + '_augassign(_attr(ENV, _str("' + name + '")), ' + op + ', ' + value + ')'

		elif TYPE == 'raise':
			assert NODE['from'] is None, 'unsupported from argument in raise'
			exception = fully_encode(NODE['exception'])
			#yield CTX.INDENT() + '_RAISE(' + exception + ', NULL);\n' # EXCEPTION, LINEINFO
			# TODO just call raise here?

		elif TYPE == 'assert': # TODO
			test = fully_encode(NODE['test'])
			message = NODE['message']
			if message:
				assert message['__type__'] == 'constant' and isinstance(message['value'], str), 'assertion with non-string {}'.format(type(message['value']))
				message = '"'+''.join(['\\'+c if c == '"' else c for c in message['value']])+'"'
			else:
				message = 'NULL'
			# how about when we're inside a try block?  then we're inside a function for the try...  so we can call the finally clause...
			#yield CTX.INDENT() + 'if (_as_bool(' + test + ')){return __RAISE(ENV, "AssertionError", ' + message + ');\n' #if test(...): raise(...) # message

		elif TYPE == 'delete': # TODO
			targets = NODE['targets']
			if len(targets) == 1:
				''#yield CTX.INDENT() + '_del(ENV, ' + fully_encode(targets[0]) + ')'
			elif len(targets) > 1:
				targets = [fully_encode(t) for t in NODE['targets']]
				args = '_a' + str(len(targets)) + '(' + ', '.join(targets) + ')'
				#yield CTX.INDENT() + '_del_multi(ENV, ' + args + ')'# or call(ENV, INSTANCE, attr)
			else:
				raise NotImplementedError('del < 1??')

		elif TYPE == 'pass':
			return None # ?

		elif TYPE == 'type_alias': # v3.8+
			raise NotImplementedError(TYPE)

		# IMPORTS:
		elif TYPE == 'import': # TODO
			statements = []
			for alias in NODE['names']:
				# TODO if dot in name here then we import the toplevel module and bring the subs in it's namespace
				statements.append(CTX.INDENT() + '_import("' + alias['name'] + '");') # TODO just localize the name here?  build?
			#yield '\n'.join(statements) # so no trailing '\n'
			#NOTE: this is the keyword 'import', so we need to include, otherwise we would 'build' what we need into the ENV
			#- import can appear inside functions, we need to make it global (maybe delay the build until it is accessed from ENV?)
		elif TYPE == 'import_from': # TODO
			statements = []
			module = NODE['module']
			for alias in NODE['names']:
				if alias['as']:
					statements.append(CTX.INDENT() + '_import_from_as("' + module + '", "' + alias['name'] + '", "' + alias['as'] + '");')
				else:
					statements.append(CTX.INDENT() + '_import_from("' + module + '", "' + alias['name'] + '");')
			#yield '\n'.join(statements) # so we only have newlines between them but don't end on one...
			#only bring in certain names?  write header with only those names?
		elif TYPE == 'import_alias':
			raise NotImplementedError(TYPE)

		# CONTROL FLOW:
		# TODO these need to use a stack to designate the operations...  and save state
		elif TYPE == 'if': # TODO

			#branch to different function calls based on truth condition (just interpret the one that is true)

			# TODO if body contains single if statement, then bring it up into else if here, and use its else
			#if CTX.inline(): XXX only comprehensions do this, and they can generate their own code...
			#	# in one line
			#	yield CTX.INDENT() + 'if (test){} else {}'
			#else:
			# branch vertically
			
			elseif = []

			#yield CTX.INDENT() + 'if (_as_bool(test)){\n'
			#for n in NODE['body']:
			#	for s in encode_element(SUBROOTPATH, n, CTX.subcontext()):
			#		yield s
			#	yield '\n'
			#yield CTX.INDENT() + '}\n'
			#yield CTX.INDENT() + 'else {\n'
			# TODO first line of else and else if do check if test raised an error?
			#yield CTX.INDENT(1) + '/* TODO body */\n'
			#yield CTX.INDENT() + '}'
		elif TYPE == 'for': # TODO

			# TODO preprocess breaks the for statement into a series of functions, just like we do in c
			# then we iterate here calling block['current']() until error or complete, and then return
			# continue sets the block state and returns, as well as break and the other control flow statements...

			# TODO so start is a function that just starts calling each interpret statement and checking break condition...

			# TODO make an object to represent the current state (or dict), and the just keep calling the active function until ended...  (so continue is set and then return)

			# TODO so this needs to basically iterate the block until it is complete (block status indicates exit / return)

			# TODO use dict for block, push to stack, and assign the dict 'start','cleanup','end' as functions, then process here until complete (assign status to dict block, check it here)

			# TODO for else: use else variable outside loop?
			''#yield 'for (...){}' #as function? for_x_in(ENV, X, IN) ? or can we use for directly?
			#else?  for_x_in_else(ENV, X, IN, ELSE_CALLBACK) ?
		elif TYPE == 'while': # TODO
			# TODO for else: use variable outside loop
			''#yield 'while (test){}' # map to while statement
			#else?  then use function?  while_x_else()
		elif TYPE == 'break':
			# TODO assign to current block?  return indicator as well?
			''#yield 'break;' # ?
		elif TYPE == 'continue':
			# TODO set current block back to start
			''#yield 'continue;'
		elif TYPE == 'try': # TODO
			# series of functions for each branch, with error checks in ENV on return
			#make a function to handle each try/except/finally/else block, do check after call for error status
			#error status is set on ENV so check is done after call returns
			''#yield 'TODO:try'
		elif TYPE == 'try_star': # v3.11+
			raise NotImplementedError(TYPE)
		elif TYPE == 'exception':
			raise NotImplementedError(TYPE)
		elif TYPE == 'with': # TODO
			# This is ENV[as] = expression() and then call __enter__ and __exit__() methods of the instance...
			''#yield 'with'
			#value = with_x(ENV, X)
			#value = with_x_as(ENV, X, "<as_name>") # TODO multiple names?  just list the multiple individual calls?

			# TODO just setup the env and variables, then iterate through the body until exit, and then run cleanup
		elif TYPE == 'with_item':
			raise NotImplementedError(TYPE)

		# PATTERN MATCHING: TODO v3.8+

		# TYPE ANNOTATIONS: TODO v3.8+

		# TYPE PARAMETERS: TODO v3.8+

		# FUNCTION AND CLASS DEFINITIONS:
		elif TYPE == 'function_definition': # TODO
			# this is just the instantiation of the function into the env in the module mainbody,
			# the definition was made at the top of the module with the other predefinitions
			name = NODE['name']
			# TODO name needs to be the name of the function defined at the top
			#predefined_name = CTX.function_predefined_name(name)
			predef_name = CTX.get_predef_for(NODE)['predefined_name']
			#yield CTX.INDENT() + '_funcdef("' + name + '", ' + predef_name + ');' # this is just instantiation of the function instance into ENV from the definition defined at the top of the module
			#- if defined inside another function it needs to be defined in module global scope (all of them do actually, we'll run the code inside ModuleName_mainbody(...)
		elif TYPE == 'lambda': # TODO lambda can change function signature for specific args?
			''#yield CTX.INDENT() + '_lambdef("' + name + '", TODO:lambda name from ctx);'
			#- just make a function for it
		elif TYPE == 'arguments': # TODO
			''#yield CTX.INDENT() + 'arguments()'
		elif TYPE == 'argument': # TODO
			''#yield CTX.INDENT() + 'arg'
		elif TYPE == 'return': # TODO
			value = fully_encode(NODE['value'])
			#yield CTX.INDENT() + '_RETURN(' + value + ')'
			#map as return keyword?  return using function: SnapObject = RETURN(ENV) where we indicate we go up in scope
		elif TYPE == 'yield': # TODO
			''#yield CTX.INDENT() + 'yield'
			#need to create an iterator object, with a series of functions that handle each segment before yield...?
		elif TYPE == 'yield_from': # TODO
			''#yield CTX.INDENT() + 'yield_from'
		elif TYPE == 'global': # TODO
			#register with ENV so assignments to this go to the top ENV
			# TODO make this behave like _attr/_item where it's a proxy and will forward to the appropriate attr...  so it just finds the global env, and holds a reference to it and the attr...
			''#yield CTX.INDENT() + 'global(ENV, attr)'
		elif TYPE == 'non_local': # TODO
			#register with ENV so assignments to this go to the parent ENV
			# TODO behaves like _attr or _global, but finds the first parent ENV with the attr
			''#yield CTX.INDENT() + 'nonlocal(ENV, attr)'
		elif TYPE == 'class_definition': # TODO
			#make type and instance functions, as well as methods in global scope, instantiate by calling the type
			name = NODE['name']
			#yield CTX.INDENT() + '_classdef("' + name + '", ' + CTX.class_predefined_name(name) + ');'


		elif TYPE == 'newline':
			# TODO
			'keep track of current c newlines, and add extra newlines, or just always add newlines to try to space the statements like they were in python'
			# TODO in the python decoder add spacers based on the line info, where needed inside any node with a body...

			# TODO also include python line/function info for debugging along with the c ones...

		else:
			raise TypeError('unknown type', repr(TYPE))


def build(ENV):
	ENV.SnapInterpreter = SnapInterpreter

def main(ENV):

	'test' # TODO pass ast and see it get evaluated

