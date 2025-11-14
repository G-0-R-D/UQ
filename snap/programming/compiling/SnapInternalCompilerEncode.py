
import re
from base64 import b64decode

def build(ENV):


	class SnapInternalCompilerEncode(object):


####### ROOT NODES:

		def encode_module(self, N):

			''#list of predefinitions (classes, functions, lambda, yield, imports, ...) - everything that needs to be declared at the top of the module
			yield '\n'

			# NOTE: imports/include statements and header guards will be handled externally to this module

			for n in sorted(self.predefs.values(), key=lambda x: -x['count']):

				yield self.fully_encode(n)

				yield '\n'

			yield self.INDENT() + 'void ' + self.module_name + '__MAINBODY(SnapObject_t* ENV)'
			if self.is_headerfile:
				yield ';\n'
			else:
				yield '{\n\n'

				self.indent()

				for sub in N['body']:
					yield self.fully_encode(sub)#, sub_indent_level=1)
					yield '\n'

				self.dedent()

				yield '\n'
		
				yield self.INDENT() + '}\n'

		def encode_input_expression(self, N): raise NotImplementedError(repr(N['__type__']))
		def encode_interactive(self, N): raise NotImplementedError(repr(N['__type__']))
		def encode_function_type(self, N): raise NotImplementedError(repr(N['__type__']))


####### LITERALS:

		def encode_constant(self, N):

			value = N['value']

			data_type = N['data_type']

			if data_type == 'string':
				if value.startswith('snapc:'):
					# this is protocol to 'switch' into c from python in-place, implement as a string by itself
					# implement as c code, as is, but fix indent
					lines = value[len('snapc:'):].split('\n')
					indent_pattern = re.compile(r"(\s+)")
					smallest_indent = None
					for line in lines:
						match = indent_pattern.match(line)
						if match and (smallest_indent is None or len(match.group(1)) > len(smallest_indent)):
							smallest_indent = match.group(1)

					for line in lines:
						if line.startswith(smallest_indent):
							line = line[len(smallest_indent):]
						yield self.INDENT() + line + '\n'

				else:
					yield self.INDENT() + '_str("' + repr(''.join(['\\'+c if c == '"' else c for c in value]))[1:-1] + '")' # TODO independent lines...?
			elif data_type == 'bytes':
				value = b64decode(value) # TODO how to represent bytes in c?  char?
				yield self.INDENT() + '_bytes("' + repr(value)[2:-1] + '", ' + str(len(value)) + ')'
			elif data_type == 'integer':
				# bool isn't the right type??
				text = str(value)
				if text in ('True', 'False'): raise NotImplementedError('fix bool in ast') # TODO
				#if text == 'True':
				#	yield self.INDENT() + '_bool(1)'
				#elif text == 'False':
				#	yield self.INDENT() + '_bool(0)'
				#else:				
				#	yield self.INDENT() + '_int(' + str(value) + ')'
				yield self.INDENT() + '_int(' + str(value) + ')'
			elif data_type == 'floating_point':
				yield self.INDENT() + '_float(' + str(value) + ')'
			elif data_type == 'complex':
				raise NotImplementedError('complex numbers not yet mapped', repr(value))
			elif data_type == 'boolean':
				yield self.INDENT() + '_bool(' + str(int(value)) + ')'
			elif data_type == 'null':
				assert value is None
				yield self.INDENT() + 'NULL' # ?
			elif data_type == 'ellipsis':
				raise NotImplementedError("ellipsis is deprecated; current ast.parse doesn't even allow it.")
			else:
				raise NotImplementedError('constant type', type(value))

		def encode_formatted_value(self, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))
		def encode_joined_string(self, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

		def _encode_list_tuple_or_set(self, N):
			items = N['items']
			if items:
				item_list = ', '.join([self.fully_encode(i) for i in items])
				item_list = '_a' + str(len(items)) + '(' + item_list + ')'
				msg = '_msg_a(' + item_list + ')'
			else:
				msg = 'NULL'
			#yield self.INDENT() + '_' + N['__type__'] + '(' + msg + ')'
			yield '_' + N['__type__'] + '(' + msg + ')'

		encode_list = _encode_list_tuple_or_set
		encode_tuple = _encode_list_tuple_or_set
		encode_set = _encode_list_tuple_or_set

		def encode_dictionary(self, N):

			msg_name = '_msg'

			using_arguments = [['a',None], ['A',None], ['k',None], ['K',None]]

			kwargs = []
			unpack_kwargs = None
			for k,v in zip(N['keys'], N['values']):
				if k is None or k['__type__'] == 'NoneType':
					# if key is None then value is name of the dict to unpack (ie. {'a':1, **x})
					assert unpack_kwargs is None, 'duplicate for unpack_kwargs'
					unpack_kwargs = self.fully_encode(v)
				else:
					kwargs.extend( (self.fully_encode(k), self.fully_encode(v)) )

			if kwargs:
				using_arguments[2][1] = '_k' + str(len(kwargs) // 2) + '(' + ', '.join(kwargs) + ')'

			if unpack_kwargs:
				using_arguments[3][1] = unpack_kwargs

			using_arguments = [e for e in using_arguments if e[1] is not None]

			if using_arguments:
				msg_name += '_' + ''.join([e[0] for e in using_arguments])
				using = ', '.join([e[1] for e in using_arguments])
				msg = msg_name + '(' + using + ')'
			else:
				msg = 'NULL'

			yield '_dict(' + msg + ')'


####### VARIABLES:

		def encode_name(self, N):

			name = N['value']
			#context = NODE['context']['__type__']
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
			# (attr is like a weakref, it holds the attr and the target and then does the appropriate access to the target (set/get/del)
			yield '_attr(ENV, "' + name + '")'

		# TODO phase these out of generalized ast?  load/store context is bypassed entirely by using _attr()/_item() placeholders instead....
		def encode_load(self, N): raise NotImplementedError(N['__type__'])
		def encode_store(self, N): raise NotImplementedError(N['__type__'])
		def encode_remove(self, N): raise NotImplementedError(N['__type__'])

		def encode_starred(self, N): # TODO?
			#print('starred', NODE.keys())
			# _item(_slice(NULL, NULL, NULL))
			yield '_iter(' + self.fully_encode(N['value']) + ')'

####### EXPRESSIONS:

		def encode_expression(self, N):
			# https://docs.python.org/3/library/ast.html#ast.Expr
			# this is used when return value isn't used or stored; statement by itself

			#if NODE['value']['__type__'] == 'call' and NODE['value']['base']['__type__'] == 'name' and NODE['value']['base']['value'] == 'snap_raw':
			#	args = NODE['value']['arguments']
			#	assert len(args) == 1 and args[0]['__type__'] == 'constant' and isinstance(args[0]['value'], str), 'snap_raw must be given single string argument'
			#	yield self.INDENT() + args[0]['value'] + ';'
			#else:
			yield self.INDENT() + '_DISCARD(' + self.fully_encode(N['value']) + ');'

		def encode_unary_operation(self, N):
			yield self.fully_encode(N['operator']) + '(' + self.fully_encode(N['operand']) + ')'

		def encode_unary_add(self, N):
			yield '_uadd' # '(+x)'
		def encode_unary_subtract(self, N):
			yield '_usub' # '(-x)'
		def encode_not(self, N):
			yield '_unot' # '(not x)'
		def encode_bitwise_invert(self, N):
			yield '_uinv' # '(~x)'

		def encode_binary_operation(self, N):
			op_name = self.fully_encode(N['operator']) + '_op'
			left = self.fully_encode(N['left'])
			right = self.fully_encode(N['right'])
			yield op_name + '(' + left + ', ' + right + ')'
			#yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'


		def encode_add(self, N):
			yield '_add' # '+'
		def encode_subtract(self, N):
			yield '_sub' # '-'
		def encode_multiply(self, N):
			yield '_mul' # '*'
		def encode_divide(self, N):
			yield '_div' # '/'
		def encode_floor_divide(self, N):
			yield '_fldiv' # '//'
		def encode_modulo(self, N):
			yield '_mod' # '%'
		def encode_power(self, N):
			yield '_pow' # '**'
		def encode_bitwise_left_shift(self, N):
			yield '_bit_lshift' # '<<'
		def encode_bitwise_right_shift(self, N):
			yield '_bit_rshift' # '>>'
		def encode_bitwise_or(self, N):
			yield '_bit_or' # '|'
		def encode_bitwise_xor(self, N):
			yield '_bit_xor' # '^'
		def encode_bitwise_and(self, N):
			yield '_bit_and' # '&'
		def encode_matrix_multiply(self, N): raise NotImplementedError(repr(N['__type__']))


		def encode_bool_operation(self, N):

			if len(N['values']) == 2:
				op_name = self.fully_encode(N['operator']) + '_op'
				left = self.fully_encode(N['values'][0])
				right = self.fully_encode(N['values'][1])
				yield op_name + '(' + left + ', ' + right + ')'
			else:
				assert len(N['values']) > 2
				predef = self.predefs[id(N)]
				yield predef['predefined_name'] + '(ENV)'
				# TODO error check after? XXX in expression...

		def encode_and(self, N):
			yield '_and'
		def encode_or(self, N):
			yield '_or'


		def encode_comparison(self, N):

			if len(N['operators']) == 1:
				# operands includes 'left', so it's len 1 for 2 elements
				assert len(N['operators']) == 1 and len(N['values']) == 1
				op_name = self.fully_encode(N['operators'][0]) + '_op'
				left = self.fully_encode(N['left'])
				right = self.fully_encode(N['values'][0])
				yield op_name + '(' + left + ', ' + right + ')'
			else:
				# multiple chained comparisons will be handled by custom predefined function, we just need to call it
				assert len(N['values']) > 1
				predef = self.predefs[id(N)]
				yield predef['predefined_name'] + '(ENV)'

		def encode_equal(self, N):
			yield '_equal' # '=='
		def encode_not_equal(self, N):
			yield '_not_equal' # '!='
		def encode_less_than(self, N):
			yield '_less_than' # '<'
		def encode_less_or_equal(self, N):
			yield '_less_or_equal' # '<='
		def encode_greater_than(self, N):
			yield '_greater_than' # '>'
		def encode_greater_or_equal(self, N):
			yield '_greater_or_equal' # '>='
		def encode_is(self, N):
			yield '_is' # 'is'
		def encode_is_not(self, N):
			yield '_is_not' # 'is not'
		def encode_in(self, N):
			yield '_in' # 'in'
		def encode_not_in(self, N):
			yield '_not_in' # 'not in'

		def encode_call(self, N):

			#self.push(NODE, indent_level=0)

			base = N['base']

			# XXX instead of raw just use standalone strings that start with "snapc:..." or something
			#if base['__type__'] == 'name' and base['value'] == 'snap_raw':
			#	#name = base['value']
			#	#if name == 'snap_raw':
			#	raise Exception('snap_raw needs to be handled in expression (it must be a standalone statement)')
			#	#else:
			#	#	#arguments = ''.join(list(encode_element(SUBROOTPATH, )))
			#	#	yield CTX.INDENT() + '_call(_get(ENV, "' + name + '"), _msg(...TODO))'
			#else:

			if N['arguments'] or N['keyword_arguments']:

				msg_name = '_msg'

				using_arguments = [['a',None], ['A',None], ['k',None], ['K',None]]
					
				#next_ctx = CTX.subcontext(indent_level=0) # XXX TODO push
				args = []
				unpack_args = None
				for arg in N['arguments']:
					if arg['__type__'] == 'starred':
						unpack_args = self.fully_encode(arg)
					else:
						args.append(self.fully_encode(arg))

				if args:
					using_arguments[0][1] = '_a'+str(len(args)) + '(' +  ', '.join(args) + ')'

				if unpack_args:
					using_arguments[1][1] = unpack_args

				kwargs = []
				unpack_kwargs = None
				for kwarg in N['keyword_arguments']:
					if kwarg['key'] is None:
						unpack_kwargs = self.fully_encode(kwarg['value'])
					else:
						#print('kwarg', kwarg)
						kwargs.append(self.fully_encode(kwarg))

				if kwargs:
					using_arguments[2][1] = '_k' + str(len(kwargs)) + '(' + ', '.join(kwargs) + ')'

				if unpack_kwargs:
					using_arguments[3][1] = unpack_kwargs

				using_arguments = [e for e in using_arguments if e[1] is not None]

				if using_arguments:
					msg_name += '_' + ''.join([e[0] for e in using_arguments])
					using = ', '.join([e[1] for e in using_arguments])
					msg = msg_name + '(' + using + ')'
				else:
					msg = '_msg()'
			else:
				msg = 'NULL'

			base_element = self.fully_encode(base)
			
			yield '_call(' + base_element + ', ' + msg + ')'

			#self.pop()

		def encode_keyword(self, N):
			key = '_str("' + N['key'] + '")'
			value = self.fully_encode(N['value'])
			yield key + ', ' + value

		def encode_if_expression(self, N):
			# NOTE: this is in-place 'x if y else z' statement, if/else branching is in 'if' type...
			# TODO can this be done with a ternery?  and _as_bool()...
			#* create a c function call to represent the body of each section
			#	** unpack single else: if into else if at same level...
			# TODO just implement a function for the if as a whole, then use if, when it returns we can catch the return?
			raise NotImplementedError(repr(N['__type__']))
			yield '(if (...){} else {})' # TODO just use c if else and (else if)

		def encode_attribute(self, N):
			#print('attribute value', NODE['value'])
			base = self.fully_encode(N['value'])
			attr = N['attribute']
			if 0:#NODE['value']['__type__'] == 'name':
				# first access if from ENV
				base_stmt = '_attr(ENV, ' + base + ')'
			else:
				# all other accesses are from whatever the previous base return was
				base_stmt = base
			yield '_attr(' + base_stmt + ', _str("' + attr + '"))'

		def encode_named_expression(self, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

####### SUBSCRIPTING:

		def encode_subscript(self, N):
			# call(ENV, INSTANCE, "__getitem__", ARGS[0] = SnapSlice()) ?
			target = self.fully_encode(N['base'])
			key = self.fully_encode(N['key'])
			# TODO slice can assign, get, or delete...
			
			# TODO item is object, and we can use __setitem__ or other assignment to set/get?  like item = x or item.x or item['x']?  and it forwards to the request to the target...
			# XXX NOTE: _item is specifically __getitem__|__setitem__, _attr is __setattr__|__getattr__
			yield self.INDENT() + '_item(' + target + ', ' + key + ')'

		def encode_slice(self, N):

			keys = []
			for attr in ('start','end','step'):
				x = N[attr]
				if x is None:
					keys.append('NULL')
				else:
					# NOTE: any type can be used as slice param
					keys.append(self.fully_encode(x))
			keys = ', '.join(keys)
			yield '_slice(' + keys + ')'

####### COMPREHENSIONS:

		def _encode_comprehension(self, N):
			yield self.predefs[id(N)]['predefined_name'] + '(ENV)'

		encode_list_comprehension = _encode_comprehension
		encode_set_comprehension = _encode_comprehension
		encode_generator_comprehension = _encode_comprehension
		encode_dictionary_comprehension = _encode_comprehension
		encode_comprehension = _encode_comprehension

####### STATEMENTS:

		def encode_assign(self, N):
			#for sub in N['targets']:
			#	for root in walk_tree(sub): # TODO only check NODE['targets']
			#		if root[-1]['__type__'] == 'name':
			#			# for from import, need to know global names # TODO only if body is toplevel?
			#			self.register_ENV_name(root[-1]['value']) # XXX analysis can be done elsewhere

			#print('targets', [n['__type__'] for n in NODE['targets']])
			len_targets = len(N['targets'])
			targets = ', '.join([self.fully_encode(e) for e in N['targets']])
			value = self.fully_encode(N['value'])
			# TODO multiple targets need to be merged, but how to know they are multiple and not unpacked?  make separate _assign_multi?
			if len_targets > 1:
				targets = '_a' + str(len_targets) + '(' + targets + ')'
			yield '_assign(' + targets + ', ' + value + ')'
			#-- value is SnapObject

		def encode_annotated_assign(self, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

		def encode_augmented_assign(self, N):
			target = N['target']
			assert target['__type__'] == 'name', 'only names supported for augassign right now {}'.format(target['__type__'])
			name = target['value']
			op = self.fully_encode(N['operator'])
			value = self.fully_encode(N['value'])
			# TODO op?  use as string?
			yield '_augassign(_attr(ENV, "' + name + '"), ' + op + ', ' + value + ')'

		def encode_raise(self, N):
			assert N['from'] is None, 'unsupported from argument in raise'
			exception = self.fully_encode(N['exception'])
			yield self.INDENT() + '_RAISE(' + exception + ', NULL);\n' # EXCEPTION, LINEINFO

		def encode_assert(self, N):
			test = self.fully_encode(N['test'])
			message = N['message']
			if message:
				assert message['__type__'] == 'constant' and isinstance(message['value'], str), 'assertion with non-string {}'.format(type(message['value']))
				message = '"'+''.join(['\\'+c if c == '"' else c for c in message['value']])+'"'
			else:
				message = 'NULL'
			# how about when we're inside a try block?  then we're inside a function for the try...  so we can call the finally clause...
			yield self.INDENT() + 'if (_as_bool(' + test + ')){return __RAISE(ENV, "AssertionError", ' + message + ');\n' #if test(...): raise(...) # message

		def encode_delete(self, N):
			targets = N['targets']
			if len(targets) == 1:
				yield self.INDENT() + '_del(ENV, ' + self.fully_encode(targets[0]) + ')'
			elif len(targets) > 1:
				targets = [self.fully_encode(t) for t in N['targets']]
				args = '_a' + str(len(targets)) + '(' + ', '.join(targets) + ')'
				yield self.INDENT() + '_del_multi(ENV, ' + args + ')'# or call(ENV, INSTANCE, attr)
			else:
				raise NotImplementedError('del < 1??')

		def encode_pass(self, N):
			# there is no pass statement in c, but we'll leave a comment to indicate the intention
			yield self.INDENT() + '/* pass */'

		def encode_type_alias(self, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

####### IMPORTS:

		# backend modules will import using same build mechanism, so aside from 'snap.h' there are no other includes...
		# a main module will create the main function, include all the modules, build them all into the ENV, and then
		# begin execution...

		def encode_import(self, N):
			statements = []
			for alias in N['names']:
				# TODO if dot in name here then we import the toplevel module and bring the subs in it's namespace
				statements.append(self.INDENT() + '_import("' + alias['name'] + '");') # TODO just localize the name here?  build?
			yield '\n'.join(statements) # so no trailing '\n'
			#NOTE: this is the keyword 'import', so we need to include, otherwise we would 'build' what we need into the ENV
			#- import can appear inside functions, we need to make it global (maybe delay the build until it is accessed from ENV?)

		def encode_import_from(self, N):

			statements = []
			module = N['module']
			for alias in N['names']:
				if alias['as']:
					statements.append(self.INDENT() + '_import_from_as("' + module + '", "' + alias['name'] + '", "' + alias['as'] + '");')
				else:
					statements.append(self.INDENT() + '_import_from("' + module + '", "' + alias['name'] + '");')
			yield '\n'.join(statements) # so we only have newlines between them but don't end on one...
			#only bring in certain names?  write header with only those names?

		def encode_import_alias(self, N): raise NotImplementedError(repr(N['__type__'])) # handled by imports...

####### CONTROL FLOW:

		def encode_if(self, N):
			# TODO if body contains single if statement, then bring it up into else if here, and use its else
			#if CTX.inline(): XXX only comprehensions do this, and they can generate their own code...
			#	# in one line
			#	yield CTX.INDENT() + 'if (test){} else {}'
			#else:
			# branch vertically

			#self.push(NODE)

			#print(NODE.keys())

			else_if = []

			# TODO contain the if statement in it's own function, like with does, so we can return from it on error...
			#	-- TODO predefine the if statement and then just call it directly here, this is the call... if_statement_1()

			yield self.INDENT() + 'if (_as_bool(' + self.fully_encode(N['test']) + ')){\n'
			self.indent()
			for n in N['body']:
				yield self.fully_encode(n)
			self.dedent()
			yield self.INDENT() + '}\n'
			yield self.INDENT() + 'else {\n'
			# TODO first line of else and else if do check if test raised an error?
			yield self.INDENT(1) + '/* TODO body */\n'
			yield self.INDENT() + '}\n'

			#self.pop()

		def encode_for(self, N):
			# TODO for else: use else variable outside loop?

			# TODO turn this into a while (1) loop?  then get next items or break/raise?

			yield self.INDENT() + '/* for TODO:info */\n' # TODO print original python line

			# TODO declare vars into ENV in case return is called from inside for loop
			yield self.INDENT() + '/* declare vars outside of loop (so we can refcount them after loop completes) */\n'

			yield self.INDENT() + 'while (1){\n'

			yield self.INDENT(1) + '/* unpack iter */\n' # TODO unpack to local var, verify, and then assign to ENV as well, refcount for the local vars...

			yield self.INDENT() + '}\n'

			"""
			while (1){
				ENV[unpack] = iter;
				if (iter complete){
					break;
				}

				body
			}

			check ENV for error after loop!
			"""

			# put inside own function like with and if statements...
			#	-- TODO predefine...

			# TODO define function then use the for statement inside of it so the keywords work...

			# TODO init the for in function, then assign start function to assign from the source to the target(s), unpack into ENV basically

		def encode_while(self, N):
			# TODO for else: use variable outside loop
			yield 'while (test){}' # map to while statement
			#else?  then use function?  while_x_else()
			# TODO _as_bool(...) is a discard that returns an int

			# TODO
			"""
			init vars (in ENV)

			while (_as_bool(TEST)){
				body
			}

			check ENV for error
			"""

		def encode_break(self, N):
			yield 'break;'
			#raise ValueError('this is not the way to do', repr(TYPE))

		def encode_continue(self, N):
			yield 'continue;'
			#raise ValueError('this is not the way to do', repr(TYPE))

		def encode_try(self, N):
			"""
			if there is a finally clause we need to double nest the functions, otherwise we can get away with just one

			error check after the return
			"""
			'' # TODO just define the try body in a function, and then check if ENV exception and if so then attempt to handle it (exception can be in main code section)

			# series of functions for each branch, with error checks in ENV on return
			#make a function to handle each try/except/finally/else block, do check after call for error status
			#error status is set on ENV so check is done after call returns

			# TODO what if yield is inside try statement?  we need to pre-scan for yield, or all flow statements, and assign the next function...  partition the blocks around the keywords
			#	-- so if try contains a yield (or other flow statement) then it switches the next try state
			#	-- TODO so the main try function needs to loop on the status of the try block and keep calling the current or doing the action required...
			#	-- the yield statement means set the status of the generator of the yield value, and set the next function to the one after the yield statement...  the try blocks inside would be in the same ENV...

			predef_name = self.predefs[id(N)]['predefined_name']

			yield self.INDENT() + '_DISCARD(' + predef_name + '(ENV));\n'

			yield self.INDENT() + 'if (TODO:ENV.error){\n'

			for exception in N['exceptions']:
				yield self.INDENT(1) + '/* handle exceptions... */\n'

			# https://stackoverflow.com/questions/855759/what-is-the-intended-use-of-the-optional-else-clause-of-the-try-statement-in
			if N['else']:
				'/* if ENV has no exception raised run the else */'

			if N['finally']:
				'/* always run this */'

			yield self.INDENT() + '}\n'

			"""

			# TODO if there is a finally clause then we need to nest twice!  otherwise we could just get away with one...

			try_predef(ENV){
				try_body(ENV);
				if (ENV.exception){
					if (ENV.exception == x || ENV.exception == y || ...){
						another call? or no?
					}
				}
				else {
					if there is an else clause then include this block, no need for another function?
				}
			}
			/* finally body */ # can return here it is ok
			/* finish with error check?  report if another exception was raised... otherwise just disarm the current exception */

			"""


			#print(NODE.keys())

			#yield self.INDENT() + '_ERR_CHK(' + self.predefs[id(NODE)]['predefined_name'] + '(ENV)' + ');'

			# TODO could we add the exception to a stack?

		def encode_try_star(self, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))
		def encode_exception(self, N):
			yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(N.keys()) + '*/'

		def encode_with(self, N):
			# TODO just make a function for the with call, call the __enter__ at the beginning of the call and __exit__ *outside* the function after the call, then check errors
			# This is ENV[as] = expression() and then call __enter__ and __exit__() methods of the instance...
			yield 'with'
			"""
			ENV[as] = expression();
			_call(ENV[as], __enter__)
			with_call(ENV);
			_call(ENV[as], __exit__)
			"""
			#value = with_x(ENV, X)
			#value = with_x_as(ENV, X, "<as_name>") # TODO multiple names?  just list the multiple individual calls?

		def encode_with_item(self, N):
			#raise NotImplementedError(TYPE)
			yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(N.keys()) + '*/'



####### PATTERN MATCHING: TODO v3.8+

####### TYPE ANNOTATIONS: TODO v3.8+

####### TYPE PARAMETERS: TODO v3.8+


####### FUNCTION AND CLASS DEFINITIONS:

		def encode_function_definition(self, N):
			# this is just the instantiation of the function into the env in the module mainbody,
			# the definition was made at the top of the module with the other predefinitions
			name = N['name']
			# TODO name needs to be the name of the function defined at the top
			#predefined_name = CTX.function_predefined_name(name)
			predef_name = self.predefs[id(N)]['predefined_name']
			yield self.INDENT() + '_def("' + name + '", ' + predef_name + ');' # this is just instantiation of the function instance into ENV from the definition defined at the top of the module
			#- if defined inside another function it needs to be defined in module global scope (all of them do actually, we'll run the code inside ModuleName_mainbody(...)

		def encode_lambda(self, N):
			# NOTE: _lambda returns a lambda object with the predefined function referenced (so it can then be called by the user like a function)
			name = self.predefs[id(N)]['predefined_name']
			yield '_lambda(' + name + ')'
			#- just make a function for it, then it gets called with args...

		def encode_arguments(self, N):
			yield self.INDENT() + 'arguments()' # TODO

		def encode_argument(self, N):
			yield self.INDENT() + 'arg' # TODO

		def encode_return(self, N):
			if N['value'] is not None:
				value = self.fully_encode(N['value'])
			else:
				value = 'NULL'
			yield self.INDENT() + '_RETURN(' + value + ');'
			#map as return keyword?  return using function: SnapObject = RETURN(ENV) where we indicate we go up in scope

		def encode_yield(self, N): raise TypeError(repr(N['__type__']), '(async forbidden in backend)')
		def encode_yield_from(self, N): raise TypeError(repr(N['__type__']), '(async forbidden in backend)')

		def encode_global(self, N): # TODO
			#register with ENV so assignments to this go to the top ENV
			# TODO make this behave like _attr/_item where it's a proxy and will forward to the appropriate attr...  so it just finds the global env, and holds a reference to it and the attr...
			names = ['_str("' + n + '")' for n in NODE['names']]
			args = '_a' + str(len(names)) + '(' + ', '.join(names) + ')'
			yield self.INDENT() + '_global(' + args + ');'

		def encode_non_local(self, N):
			#register with ENV so assignments to this go to the parent ENV
			# TODO behaves like _attr or _global, but finds the first parent ENV with the attr
			names = ['_str("' + n + '")' for n in N['names']]
			args = '_a' + str(len(names)) + '(' + ', '.join(names) + ')'
			yield self.INDENT() + '_nonlocal(' + args + ');'

		def encode_newline(self, N):
			yield '\n' # TODO count?

		def encode_class_definition(self, N):
			#make type and instance functions, as well as methods in global scope, instantiate by calling the type
			name = N['name']
			predef_name = self.predefs[id(N)]['predefined_name']
			yield self.INDENT() + '_class("' + name + '", ' + predef_name + ');'



####### PREDEFINITIONS
		def encode_predefine_function_definition(self, N):
			# TODO decorators

			#self.push(NODE)

			SRC = N['__src__']
			module_name = self.module_name
			#function_name = module_name + '_' + 'func' + str(NODE['index']) + '_' + SRC['name']
			yield 'SnapObject_t* ' + N['predefined_name'] + '(SnapObject_t* ENV, SnapObject_t* MSG){\n'
			yield self.INDENT(1) + 'if (_ERRORED()){\n'
			yield self.INDENT(2) + '_RETURN(NULL);\n'
			yield self.INDENT(1) + '};\n'
			yield self.INDENT(1) + 'ENV = _LOCAL_ENV(ENV);\n\n' # sub env

			# TODO unpack the args into local ENV variables, and verify arguments are correct
			#	-- if 'data_type' then do isinstance() check for that datatype...

			#next_ctx = CTX.subcontext()
			for e in SRC['body']:
				enc = self.INDENT(1) + self.fully_encode(e)
				yield enc

			yield '\n'

			yield self.INDENT(1) + '_RETURN(NULL);\n'
			yield self.INDENT() + '}\n'

			#self.pop()

		def encode_predefine_class_definition(self, N):
			# TODO decorators?
			SRC = N['__src__']

			# TODO define the type base class, add to env, link them by name (instance gets class from __class__ var)

			# TODO type __call__ creates new instance

			# TODO class vars assign to type in __init__?

			yield 'SnapObject_t* ' + N['predefined_name'] + '(SnapObject_t* ENV, SnapObject_t* MSG){\n'
			yield self.INDENT(1) + 'ENV = _LOCAL_ENV(ENV);\n\n'

			yield self.INDENT(1) + '_RETURN(NULL);\n'
			yield self.INDENT() + '}\n'

		def encode_predefine_lambda(self, N):

			name = N['predefined_name']

			yield 'SnapObject* ' + name + '(SnapObject* ENV, SnapObject* MSG){\n'

			yield '\n'
			yield self.INDENT(1) + '/* TODO: verify arguments and ENV is the MSG? */\n\n' # TODO unpack MSG into local ENV
			# TODO lambda is single statement so we can just return the output of the whole statement?

			SRC = N['__src__']

			body = self.fully_encode(SRC['body'])

			#yield self.INDENT() + '_lambdef(' + name + ');\n'
			yield self.INDENT(1) + '_RETURN(' + body + ');\n'
			yield self.INDENT() + '};\n'

		def encode_predefine_bool_operation(self, N):

			SRC = N['__src__']

			#print(SRC.keys())

			name = N['predefined_name']

			yield self.INDENT() + 'SnapObject* ' + name + '(SnapObject* ENV){\n\n'

			op_name = self.fully_encode(SRC['operator']) + '_op'

			#print(SRC)
			left,right = self.fully_encode(SRC['values'][0]), self.fully_encode(SRC['values'][1])
			yield self.INDENT(1) + 'SnapObject* _result = ' + op_name + '(' + left + ', ' + right + ');\n'

			idx = 2
			for value in SRC['values'][idx:]:

				yield self.INDENT(1) + 'if (_as_int(_result)){_RETURN(_result);}\n'

				left = '_result'
				right = self.fully_encode(value)

				yield self.INDENT(1) + '_result = ' + op_name + '(' + left + ', ' + right + ');\n'

			yield self.INDENT(1) + '_RETURN(_result);\n'
			yield self.INDENT() + '}\n'

		def encode_predefine_comparison(self, N):

			SRC = N['__src__']

			yield self.INDENT() + 'SnapObject* ' + N['predefined_name'] + '(SnapObject* ENV){\n\n'

			op_name = self.fully_encode(SRC['operators'][0]) + '_op'

			left,right = self.fully_encode(SRC['left']), self.fully_encode(SRC['values'][0])

			yield self.INDENT(1) + 'SnapObject* _result = ' + op_name + '(' + left + ', ' + right + ');\n'

			idx = 1
			for value in SRC['values'][idx:]:

				yield self.INDENT(1) + 'if (_as_int(_result)){_RETURN(_result);}\n'

				op_name = self.fully_encode(SRC['operators'][idx]) + '_op'
				left = '_result'
				right = self.fully_encode(value)

				yield self.INDENT(1) + '_result = ' + op_name + '(' + left + ', ' + right + ');\n'

				idx += 1

			yield self.INDENT(1) + '_RETURN(_result);\n'

			yield self.INDENT() + '}\n'

		def _encode_predefine_comprehension(self, N):
			
			SRC = N['__src__']

			yield self.INDENT() + 'SnapObject_t* ' + N['predefined_name'] + '(SnapObject_t* ENV){\n\n'

			yield self.INDENT(1) + '/* TODO: ' + TYPE + ' ' + str(SRC.keys()) + '*/\n' # TODO

			yield self.INDENT() + '}\n'

		encode_predefine_list_comprehension = _encode_predefine_comprehension
		encode_predefine_generator_comprehension = _encode_predefine_comprehension
		encode_predefine_set_comprehension = _encode_predefine_comprehension
		encode_predefine_dictionary_comprehension = _encode_predefine_comprehension
		encode_predefine_comprehension = _encode_predefine_comprehension


		def encode_predefine_try(self, N):

			SRC = N['__src__']

			yield self.INDENT() + 'SnapObject_t* ' + N['predefined_name'] + '(SnapObject_t* ENV){\n\n'

			for stmt in SRC['body']:
				yield self.INDENT(1) + self.fully_encode(stmt) + '\n'

			#yield self.INDENT(1) + '/* TODO try ' + str(SRC.keys()) + ' */\n'

			# TODO check for error and handle via exception blocks and call finally no matter what

			yield self.INDENT() + '}\n'


		def encode_predefine_forXXX(self, N):

			SRC = N['__src__']

			yield 'SnapObject_t* ' + N['predefined_name'] + '(SnapObject_t* ENV){\n\n'

			# TODO register start and end function, on block

			# TODO start does assign of variables to ENV

			yield self.INDENT(1) + '/* TODO for ' + str(SRC.keys()) + ' */\n\n'

			yield self.INDENT() + '}\n'

		# XXX import logic will be external to this module (includes)
		def encode_predefine_import(self, N):
			yield
		def encode_predefine_import_from(self, N):
			yield



	ENV.SnapInternalCompilerEncode = SnapInternalCompilerEncode


