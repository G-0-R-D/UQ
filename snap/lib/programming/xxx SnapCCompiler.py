
import os
from base64 import b64decode

# TODO
"""
this functions as a pseudo compiler, following python's compile.c

basically the ENV is passed into each op, as it calls them one by one
this outputs a flat list of 'op codes' which are actually functions to handle the operation units, along with a message for args


"""


# TODO how to do interpreted code: in the same way as items/attrs are wrapped in temporary containers we could make alternate versions of the operator functions so that they actually just create evaluation nodes that will be processed later...  then each node calls eval() on it's contents and passes the result to it's own operation...
#	-- save them in a list in the body of the parent, creating an evaluation code structure (that could even be walked?  or inspected?)
#	-- evaluation must be done in loop, with stack, we could actually just queue up the original operator functions and their arguments...

def clean_name(NAME):
	for token in ('.','/','\\',' '): # TODO use 'is alphanumeric or underscore', else underscore
		NAME = NAME.replace(token, '_')
	return NAME


	
def walk_tree(NODE):

	#if NODE.get('__type__') != 'module':
	#	print('warning: toplevel node is not a module?', repr(NODE.get('__type__')))

	QUEUE = [[NODE]]
	while QUEUE:

		PATH = QUEUE.pop(0)
		#SRC_NODE = NODE['__src__']

		yield PATH

		NODE = PATH[-1]
		if NODE is None:
			continue

		#if 'body' in NODE and TYPE not in ('class_definition',):
		#	NODE['locals'] = {} # has own local namespace XXX this would be creating new sub ENV


		# ENQUEUE
		for attr,value in NODE.items():
			if isinstance(value, list) and all([isinstance(d, dict) and '__type__' in d for d in value]):
				QUEUE.extend([PATH + [n] for n in value])
			elif isinstance(value, dict) and '__type__' in value:
				QUEUE.append(PATH + [value])



def remap_generator_branch(ROOT):

	# TODO each test (while,for,if,...) is in it's own function, which queues up the next section
	"""
	{...} denotes new function
	go to = assign next function to ENV param (__next_func__) and return from current function

	def func():
		{(A:func):
		...

		(A:while:queue)}
		{(A:while>> if (test): {^B:while} else: {^B:func}}
			{B:while

			break = go to B:func

			continue = go to A:while

			...}
		{(B:func)
		...}


	"""

	# TODO basically the body is broken into functions, at the end of the function the next one is queued and then the function returns
	# evaluation continues until a flag is set (yield, return, error; not the actual return of the function)
	# the first function of a new branch (body) does the test and either goes to the next function (into a body or back out to the next section of the previous parent body)
	# there must always be a function at the end of the body for that logic, so sub-body only has to return to next parent body, even if the last function is empty other than queueing next call (like back to the test call of a while loop to possibly do it again...)
	# so the algorithm just gives each segment a unique id (and maybe each type a unique id as well), and then just split into the test, and segments/functions for each section
	# so really this is just a re-tree, where we place the existing nodes into new nodes representing the new tree, and those nodes can have their name, and register...  keep track of current root to know where to return to...  sub-node just needs to know parent node start function and end function...

	# has body: function, class -- except those would be in their own namespace, so maybe that doesn't count?
	#	-- they would implement their own yield keyword, class can't have yield in mainbody only in methods anyway...
	#	for, while, if, with, try, lambda?, if_comp?
	# for = start just attempts to get next item, set to ENV, and continue on (start function can run until yield, break/continue, or end)
	# while = start is now if, which branches into body or continues to next parent...  start can also run until yield, break/continue, or end
	# if = no change?
	# with = no change? (regular implementation would handle the return and execute the cleanup already)
	#	-- except it needs to be broken up if there is a yield?  so cleanup happens after?  but what if iterator is deleted while yielded?
	# try = no change?
	# lambda = no change?
	# if_comp = no change?
	#	** all will need to be partitioned if a yield statement is anywhere below them, but otherwise not...

	# start -> yield -> ... -> yield -> end
	#	-- start -> yield (or start of sub-body containing yield...)

	# TODO to cleanup properly from try/with during a yield we set ENV variables and check them when the object is deleted...  so any active try,with,etc... gets properly handled...?
	#	-- maybe try, with, etc... should always be implemented by using a class instance and deleting it when finished?  instead of just a function...?
	# what if everything is implemented as a class?  including, for, if, while?
	#	-- then with(*items) would create with class into ENV?


	# TODO try,with can be functions BUT need to be classes in the yield case to save and restore state (and call finally/cleanup after resume!)
	#	-- then ENV can easily clean up with a simple DECREF (calls the finally)
	#	-- assign a __private__ member to struct for internal use, ENV can store temp objects outside of user scope in there...

	TYPE = ROOT['__type__']

	if 'body' in ROOT:
		if TYPE == 'while':
			# end of previous body section would just queue the next segment (and evaluation would resume because there would be no yield or error or return flag...)
			'end of loop cycles back to test'
	else:
		yield ROOT

	"""
	each body must be in new function segment **if it contains a yield statement...**
	"""

	return

def remap_generator(ROOT):
	assert ROOT['__type__'] == 'function_definition', 'generator root must be function_definition, not: {}'.format(repr(ROOT['__type__']))
	
	'' # TODO each body needs to be broken up into a test and a function between each yield statement
	#	-- the functions chain together, calling the next function if the end is reached
	#	-- so each if/for/while/... loop or conditional branch inside the iterator will need it's own function...
	#	-- so one function representing the test, and then a series of functions for the body between each yield (only need to break it if there is a yield statement somewhere inside/below it)

	# TODO break each section into a series of functions, the functions queue (assign) the next function to an ENV variable and then return
	#	-- evaluation continues until yield value is returned?  or errored?  or finished?
	#	-- each loop is broken up, check is done in single function

	raise NotImplementedError()

def build(ENV):

	class SnapCCompiler(object):

		__slots__ = ['settings', 'imports','stack','predefs',
			'__op_index__',
			]

		@property
		def indent_token(self):
			try:
				return self.settings['indent_token']
			except:
				return '\t'

		@property
		def is_headerfile(self):
			return self.settings.get('is_headerfile', False)



		@property
		def filepath(self):
			return self.settings.get('filepath', 'unknown')

		@property
		def basename(self):
			return os.path.basename(self.filepath)

		@property
		def module_name(self):
			return clean_name(self.basename)

		# TODO can we push the class to a stack?  get the classname of the current class as a property?
		def class_instance_name(self, CLASSNAME):
			# TODO find class in stack...
			return '__' + self.module_name + '_' + CLASSNAME

		def class_type_name(self, CLASSNAME):
			return self.class_instance_name(CLASSNAME) + 'Type'

		def class_predefined_name(self, CLASSNAME):
			return self.module_name + '_class_' + CLASSNAME

		def method_name(self, CLASSNAME, METHODNAME):
			return self.class_instance_name(CLASSNAME) + '_' + METHODNAME + '__mthd'



		def function_predefined_name(self, FUNCNAME):
			return self.module_name + '_' + FUNCNAME + '__func'

		"""
		def get_predef_for(self, SRC):
			predefs = self.persistent.get('predefinitions',[])
			for p in predefs:
				if p['__src__'] is SRC:
					return p
			raise ValueError('not found', SRC)

		def predefs(self, *TERMS):
			predefs = self.persistent.get('predefinitions',[])
			if not predefs:
				return predefs
			if not TERMS:
				return predefs
			return [p for p in predefs if p['__src__']['__type__'] in TERMS]
		"""


		def header_guard_name(self):
			return '__' + clean_name(self.filepath) + '_H__'

		def register_ENV_name(self, NAME):
			'add to self.persistent["ENV"]["names"]'
			# TODO list modules... ?  need to organize multiple modules and imports across project...


		"""
		def push(self, TYPE, start, end):
			# https://github.com/python/cpython/blob/d93605de7232da5e6a182fd1d5c220639e900159/Python/compile.c#L1629
			# compiler_push_fblock(self, TYPE, 
			''#self.stack = self.stack + [{'node':NODE, **SETTINGS}]

			# XXX TODO this needs to be in c, allocating to the ENV['__internal__'].stack

		def pop(self):
			return self.stack.pop(-1)
		"""

		def copyXXX(self, **SETTINGS):
			settings = self.settings.copy()
			settings.update(SETTINGS)
			c = Context(**settings)
			c.persistent = self.persistent
			return c

		def subcontextXXX(self, **SETTINGS):
			settings = self.settings.copy()
			settings['indent_level'] = settings.get('indent_level', 0) + 1
			settings.update(SETTINGS)
			c = Context(**settings)
			c.persistent = self.persistent
			return c

		def set(self, **SETTINGS):


			# TODO validate
			self.settings.update(SETTINGS)

		def INDENT(self, level=0):
			# XXX TODO we add stack indent level onto self.settings indent_level (so when indent_level is assigned it is included)

			indent_level = self.settings.get('indent_level', 0)

			idx = len(self.stack)
			while idx > len(self.stack):
				idx -= 1
				if 'indent_level' in self.stack[idx]:
					indent_level = self.stack[idx]['indent_level']
					break

			indent_level += level
			return indent_level * self.indent_token






		def preprocess_element(self, NODE):
			# op codes:
			# https://docs.python.org/3/library/dis.html#dis.Instruction

			# this is using self as context, create lists of opcodes with indices, then the encoder just writes them to strings...

			TYPE = N['__type__']

			imports = self.imports
			predefs = self.predefs

			def num(__TYPE__):
				return len([True for n in predefs.values() if n['__type__'] == __TYPE__]) + 1

			def add_predef(PRE):
				predefs[id(PRE['__src__'])] = PRE
				PRE['count'] = len(predefs)

			pre = {'__type__':'predefine_' + TYPE, '__src__':NODE, 'index':num('predefine_' + TYPE)}

			# TODO SnapMessage() used as arg to op?  op(ENV, MSG) and use _var("name") to get from ENV?

			# ROOT NODES:
			if TYPE == 'module': # TODO

				# TODO module main is now just a realloc of ENV->stack to the indices required, so maybe put that in here?

				pass # TODO make this walk the tree, build a tree of predefined nodes, and track the line numbers and operation counts so we know those numbers on next encode_element() calls...
				# TODO define the operator names, and operations here, encoding will now just yield the strings

			elif TYPE == 'input_expression':
				raise NotImplementedError(TYPE)
			elif TYPE == 'interactive':
				raise NotImplementedError(TYPE)
			elif TYPE == 'function_type':
				raise NotImplementedError(TYPE)

			# LITERALS:
			elif TYPE == 'constant':

				# TODO explicit declaration of str, bytes, int, bool, float, complex, or null...  where does it go?  in args or push into ENV using a command?  ENV->__args__?  so args can evaluate piece-wise as well?  args = SnapMessage instance...
				pass

			elif TYPE == 'formatted_value': # v3.8+
				raise NotImplementedError(TYPE)
			elif TYPE == 'joined_string': # v3.8+
				raise NotImplementedError(TYPE)

			elif TYPE in ('list', 'tuple', 'set'):
				pass
				"""
				items = NODE['items']
				if items:
					#'_call(_get(ENV, "' + TYPE + '"), _msg())'
					item_list = ', '.join([self.fully_encode(item) for item in items])
					item_list = '_a' + str(len(items)) + '(' + item_list + ')'
					msg = '_msg_a(' + item_list + ')'
				else:
					msg = 'NULL'
				yield self.INDENT() + '_' + TYPE + '(' + msg + ')'
				"""

			elif TYPE == 'dictionary':
				pass
				"""
				msg_name = '_msg'

				using_arguments = [['a',None], ['A',None], ['k',None], ['K',None]]

				kwargs = []
				unpack_kwargs = None
				for k,v in zip(NODE['keys'], NODE['values']):
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

				yield self.INDENT() + '_dict(' + msg + ')'
				"""

			# VARIABLES:
			elif TYPE == 'name':
				pass # use _var("string") and get from ENV on execution?
				#name = NODE['value']
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
				#yield self.INDENT() + '_attr(ENV, "' + name + '")'
			elif TYPE == 'load':
				raise NotImplementedError(TYPE)
			elif TYPE == 'store':
				raise NotImplementedError(TYPE)
			elif TYPE == 'remove':
				raise NotImplementedError(TYPE)
			elif TYPE == 'starred': # TODO?
				#print('starred', NODE.keys())
				# _item(_slice(NULL, NULL, NULL))
				#yield self.INDENT() + '_iter(' + self.fully_encode(NODE['value']) + ')'
				pass

			# EXPRESSIONS:
			elif TYPE == 'expression': # TODO?  probably just a passthrough
				# https://docs.python.org/3/library/ast.html#ast.Expr
				# this is used when return value isn't used or stored; statement by itself

				#if NODE['value']['__type__'] == 'call' and NODE['value']['base']['__type__'] == 'name' and NODE['value']['base']['value'] == 'snap_raw':
				#	args = NODE['value']['arguments']
				#	assert len(args) == 1 and args[0]['__type__'] == 'constant' and isinstance(args[0]['value'], str), 'snap_raw must be given single string argument'
				#	yield self.INDENT() + args[0]['value'] + ';'
				#else:

				#yield self.INDENT() + '_DISCARD(' + self.fully_encode(NODE['value']) + ');'
				pass

			elif TYPE == 'unary_operation':
				#op_name = self.fully_encode(NODE['operator'])
				#yield self.INDENT() + op_name + '(' + self.fully_encode(NODE['operand']) + ')'
				pass

			elif TYPE == 'unary_add':
				#yield '_str("+")'
				#yield '_uadd'
				pass
			elif TYPE == 'unary_subtract':
				#yield '_str("-")'
				#yield '_usub'
				pass
			elif TYPE == 'not':
				#yield '_str("not")'
				#yield '_unot'
				pass
			elif TYPE == 'invert':
				#yield '_str("~")'
				#yield '_uinv'
				pass

			elif TYPE == 'binary_operation':
				"""
				op_name = self.fully_encode(NODE['operator']) + '_op'
				left = self.fully_encode(NODE['left'])
				right = self.fully_encode(NODE['right'])
				yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'
				"""
				pass

			elif TYPE == 'add':
				#yield '_str("+")'
				#yield '_add'
				pass
			elif TYPE == 'subtract':
				#yield '_str("-")'
				#yield '_sub'
				pass
			elif TYPE == 'multiply':
				#yield '_str("*")'
				#yield '_mul'
				pass
			elif TYPE == 'divide':
				#yield '_str("/")'
				#yield '_div'
				pass
			elif TYPE == 'floor_divide':
				#yield '_str("//")'
				#yield '_fldiv'
				pass
			elif TYPE == 'modulo':
				#yield '_str("%")'
				#yield '_mod'
				pass
			elif TYPE == 'power':
				#yield '_str("**")'
				#yield '_pow'
				pass
			elif TYPE == 'bitwise_left_shift':
				#yield '_str("<<")'
				#yield '_lbit_shift'
				pass
			elif TYPE == 'bitwise_right_shift':
				#yield '_str(">>")'
				#yield '_rbit_shift'
				pass
			elif TYPE == 'bitwise_or':
				#yield '_str("|")'
				#yield '_bit_or'
				pass
			elif TYPE == 'bitwise_xor':
				#yield '_str("^")'
				#yield '_bit_xor'
				pass
			elif TYPE == 'bitwise_and':
				#yield '_str("&")'
				#yield '_bit_and'
				pass
			elif TYPE == 'matrix_multiply':
				raise NotImplementedError(TYPE)
			elif TYPE == 'bool_operation':
				"""
				if len(NODE['values']) == 2:
					op_name = self.fully_encode(NODE['operator']) + '_op'
					left = self.fully_encode(NODE['values'][0])
					right = self.fully_encode(NODE['values'][1])
					yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'
				else:
					assert len(NODE['values']) > 2
					predef = self.predefs[id(NODE)]
					yield self.INDENT() + predef['predefined_name'] + '(ENV)'
				"""
				pass

			elif TYPE == 'and':
				#yield '_str("and")'
				#yield '_and'
				pass
			elif TYPE == 'or':
				#yield '_str("or")'
				#yield '_or'
				pass
			elif TYPE == 'comparison':
				"""
				if len(NODE['operators']) == 1:
					# operands includes 'left', so it's len 1 for 2 elements
					assert len(NODE['operators']) == 1 and len(NODE['values']) == 1
					op_name = self.fully_encode(NODE['operators'][0]) + '_op'
					left = self.fully_encode(NODE['left'])
					right = self.fully_encode(NODE['values'][0])
					yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'
				else:
					# multiple chained comparisons will be handled by custom predefined function, we just need to call it
					assert len(NODE['values']) > 1
					predef = self.predefs[id(NODE)]
					yield self.INDENT() + predef['predefined_name'] + '(ENV)'
				"""
				pass

			elif TYPE == 'equal':
				#yield '_str("==")'
				#yield '_equal'
				pass
			elif TYPE == 'not_equal':
				#yield '_str("!=")'
				#yield '_not_equal'
				pass
			elif TYPE == 'less_than':
				#yield '_str("<")'
				#yield '_less_than'
				pass
			elif TYPE == 'less_or_equal':
				#yield '_str("<=")'
				#yield '_less_or_equal'
				pass
			elif TYPE == 'greater_than':
				#yield '_str(">")'
				#yield '_greater_than'
				pass
			elif TYPE == 'greater_or_equal':
				#yield '_str(">=")'
				#yield '_greater_or_equal'
				pass
			elif TYPE == 'is':
				#yield '_str("is")'
				#yield '_is'
				pass
			elif TYPE == 'is_not':
				#yield '_str("is not")'
				#yield '_is_not'
				pass
			elif TYPE == 'in':
				#yield '_str("in")'
				#yield '_in'
				pass
			elif TYPE == 'not_in':
				#yield '_str("not in")'
				#yield '_not_in'
				pass

			elif TYPE == 'call': # TODO
				pass
				#self.push(NODE, indent_level=0)
				"""
				base = NODE['base']

				# XXX instead of raw just use standalone strings that start with "snapc:..." or something
				#if base['__type__'] == 'name' and base['value'] == 'snap_raw':
				#	#name = base['value']
				#	#if name == 'snap_raw':
				#	raise Exception('snap_raw needs to be handled in expression (it must be a standalone statement)')
				#	#else:
				#	#	#arguments = ''.join(list(encode_element(SUBROOTPATH, )))
				#	#	yield CTX.INDENT() + '_call(_get(ENV, "' + name + '"), _msg(...TODO))'
				#else:

				if NODE['arguments'] or NODE['keyword_arguments']:

					msg_name = '_msg'

					using_arguments = [['a',None], ['A',None], ['k',None], ['K',None]]
						
					#next_ctx = CTX.subcontext(indent_level=0) # XXX TODO push
					args = []
					unpack_args = None
					for arg in NODE['arguments']:
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
					for kwarg in NODE['keyword_arguments']:
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
				
				yield self.INDENT() + '_call(' + base_element + ', ' + msg + ')'

				#self.pop()
				"""

			elif TYPE == 'keyword':
				pass
				"""
				key = '_str("' + NODE['key'] + '")'
				value = self.fully_encode(NODE['value'])
				yield self.INDENT() + key + ', ' + value
				"""

			elif TYPE == 'if_expression': # TODO
				#* create a c function call to represent the body of each section
				#	** unpack single else: if into else if at same level...
				#yield self.INDENT() + '(if (...){} else {})' # TODO just use c if else and (else if)
				pass

			elif TYPE == 'attribute':
				pass
				"""
				#print('attribute value', NODE['value'])
				base = self.fully_encode(NODE['value'])
				attr = NODE['attribute']
				if 0:#NODE['value']['__type__'] == 'name':
					# first access if from ENV
					base_stmt = '_attr(ENV, ' + base + ')'
				else:
					# all other accesses are from whatever the previous base return was
					base_stmt = base
				yield '_attr(' + base_stmt + ', _str("' + attr + '"))'
				"""

			elif TYPE == 'named_expression': # v3.8+
				raise NotImplementedError(TYPE)

			# SUBSCRIPTING:
			elif TYPE == 'subscript': # TODO
				pass
				"""
				# call(ENV, INSTANCE, "__getitem__", ARGS[0] = SnapSlice()) ?
				target = self.fully_encode(NODE['base'])
				key = self.fully_encode(NODE['key'])
				# TODO slice can assign, get, or delete...
				
				# TODO item is object, and we can use __setitem__ or other assignment to set/get?  like item = x or item.x or item['x']?  and it forwards to the request to the target...
				# XXX NOTE: _item is specifically __getitem__|__setitem__, _attr is __setattr__|__getattr__
				yield self.INDENT() + '_item(' + target + ', ' + key + ')'
				"""

			elif TYPE == 'slice':
				pass
				"""
				keys = []
				for attr in ('start','end','step'):
					x = NODE[attr]
					if x is None:
						keys.append('NULL')
					else:
						# NOTE: any type can be used as slice param
						keys.append(self.fully_encode(x))
				keys = ', '.join(keys)
				yield self.INDENT() + '_slice(' + keys + ')'
				"""

			# COMPREHENSIONS:
			elif TYPE in (
				'list_comprehension',
				'set_comprehension',
				'generator_comprehension',
				'dictionary_comprehension',
				'comprehension',
				):
				pass
				"""
				yield self.INDENT() + self.predefs[id(NODE)]['predefined_name'] + '(ENV)'
				"""

			# STATEMENTS:
			elif TYPE == 'assign':
				"""
				for sub in NODE['targets']:
					for root in walk_tree(sub): # TODO only check NODE['targets']
						if root[-1]['__type__'] == 'name':
							# for from import, need to know global names # TODO only if body is toplevel?
							self.register_ENV_name(root[-1]['value'])

				#print('targets', [n['__type__'] for n in NODE['targets']])
				len_targets = len(NODE['targets'])
				targets = ', '.join([self.fully_encode(e) for e in NODE['targets']])
				value = self.fully_encode(NODE['value'])
				# TODO multiple targets need to be merged, but how to know they are multiple and not unpacked?  make separate _assign_multi?
				if len_targets > 1:
					targets = '_a' + str(len_targets) + '(' + targets + ')'
				yield self.INDENT() + '_assign(' + targets + ', ' + value + ');'
				#-- value is SnapObject
				"""
				pass

			elif TYPE == 'annotated_assign': # 3.8+
				raise NotImplementedError(TYPE)

			elif TYPE == 'augmented_assign':
				pass
				"""
				target = NODE['target']
				assert target['__type__'] == 'name', 'only names supported for augassign right now {}'.format(target['__type__'])
				name = target['value']
				op = self.fully_encode(NODE['operator'])
				value = self.fully_encode(NODE['value'])
				# TODO op?  use as string?
				yield self.INDENT() + '_augassign(_attr(ENV, _str("' + name + '")), ' + op + ', ' + value + ')'
				"""

			elif TYPE == 'raise':
				pass
				"""
				assert NODE['from'] is None, 'unsupported from argument in raise'
				exception = self.fully_encode(NODE['exception'])
				yield self.INDENT() + '_RAISE(' + exception + ', NULL);\n' # EXCEPTION, LINEINFO
				"""

			elif TYPE == 'assert': # TODO
				pass
				"""
				test = self.fully_encode(NODE['test'])
				message = NODE['message']
				if message:
					assert message['__type__'] == 'constant' and isinstance(message['value'], str), 'assertion with non-string {}'.format(type(message['value']))
					message = '"'+''.join(['\\'+c if c == '"' else c for c in message['value']])+'"'
				else:
					message = 'NULL'
				# how about when we're inside a try block?  then we're inside a function for the try...  so we can call the finally clause...
				yield self.INDENT() + 'if (_as_bool(' + test + ')){return __RAISE(ENV, "AssertionError", ' + message + ');\n' #if test(...): raise(...) # message
				"""

			elif TYPE == 'delete': # TODO
				pass
				"""
				targets = NODE['targets']
				if len(targets) == 1:
					yield self.INDENT() + '_del(ENV, ' + self.fully_encode(targets[0]) + ')'
				elif len(targets) > 1:
					targets = [self.fully_encode(t) for t in NODE['targets']]
					args = '_a' + str(len(targets)) + '(' + ', '.join(targets) + ')'
					yield self.INDENT() + '_del_multi(ENV, ' + args + ')'# or call(ENV, INSTANCE, attr)
				else:
					raise NotImplementedError('del < 1??')
				"""

			elif TYPE == 'pass':
				# there is no pass statement in c, but we'll leave a comment to indicate the intention
				pass
				"""
				yield self.INDENT() + '/* pass */'
				"""

			elif TYPE == 'type_alias': # v3.8+
				raise NotImplementedError(TYPE)

			# IMPORTS:
			elif TYPE == 'import': # TODO
				pass
				"""
				statements = []
				for alias in NODE['names']:
					# TODO if dot in name here then we import the toplevel module and bring the subs in it's namespace
					statements.append(self.INDENT() + '_import("' + alias['name'] + '");') # TODO just localize the name here?  build?
				yield '\n'.join(statements) # so no trailing '\n'
				#NOTE: this is the keyword 'import', so we need to include, otherwise we would 'build' what we need into the ENV
				#- import can appear inside functions, we need to make it global (maybe delay the build until it is accessed from ENV?)
				"""

			elif TYPE == 'import_from': # TODO
				pass
				"""
				statements = []
				module = NODE['module']
				for alias in NODE['names']:
					if alias['as']:
						statements.append(self.INDENT() + '_import_from_as("' + module + '", "' + alias['name'] + '", "' + alias['as'] + '");')
					else:
						statements.append(self.INDENT() + '_import_from("' + module + '", "' + alias['name'] + '");')
				yield '\n'.join(statements) # so we only have newlines between them but don't end on one...
				#only bring in certain names?  write header with only those names?
				"""
			elif TYPE == 'import_alias':
				raise NotImplementedError(TYPE)

			# CONTROL FLOW:
			elif TYPE == 'if': # TODO
				pass
				"""
				# TODO if body contains single if statement, then bring it up into else if here, and use its else
				#if CTX.inline(): XXX only comprehensions do this, and they can generate their own code...
				#	# in one line
				#	yield CTX.INDENT() + 'if (test){} else {}'
				#else:
				# branch vertically

				#self.push(NODE)

				else_if = []

				# TODO contain the if statement in it's own function, like with does, so we can return from it on error...
				#	-- TODO predefine the if statement and then just call it directly here, this is the call... if_statement_1()

				yield self.INDENT() + 'if (_as_bool(test)){\n'
				for n in NODE['body']:
					for s in self.encode_element(n):
						yield s
					yield '\n'
				yield self.INDENT() + '}\n'
				yield self.INDENT() + 'else {\n'
				# TODO first line of else and else if do check if test raised an error?
				yield self.INDENT(1) + '/* TODO body */\n'
				yield self.INDENT() + '}'

				#self.pop()
				"""

			elif TYPE == 'for': # TODO
				# https://github.com/python/cpython/blob/d93605de7232da5e6a182fd1d5c220639e900159/Python/compile.c#L2651

				start,cleanup,end = {},{},{}
				
				# TODO self.push_fblock(c, NODE, start, end) ?

				# self.preprocess_element(NODE['in'])

				# TODO ADDOP GET_ITER? # TODO accesses NODE['target']?

				# TODO compiler_use_next_block(start)

				# TODO ADDOP_JREL(FOR_ITER, cleanup)

				# self.preprocess_element(NODE['body'])

				# TODO ADDOP_JABS(JUMP_ABSOLUTE, start)

				# compiler_use_next_block(cleanup)

				# compiler_pop_fblock(NODE, start)

				# for stmt in NODE['else']:
				#	self.preprocess_element(stmt)

				# compiler_use_next_block(end)
				
				"""
				basicblock *start, *cleanup, *end;

				start = compiler_new_block(c);
				cleanup = compiler_new_block(c);
				end = compiler_new_block(c);
				if (start == NULL || end == NULL || cleanup == NULL)
					return 0;

				if (!compiler_push_fblock(c, FOR_LOOP, start, end))
					return 0;

				VISIT(c, expr, s->v.For.iter);
				ADDOP(c, GET_ITER);
				compiler_use_next_block(c, start);
				ADDOP_JREL(c, FOR_ITER, cleanup);
				VISIT(c, expr, s->v.For.target);
				VISIT_SEQ(c, stmt, s->v.For.body);
				ADDOP_JABS(c, JUMP_ABSOLUTE, start);
				compiler_use_next_block(c, cleanup);

				compiler_pop_fblock(c, FOR_LOOP, start);

				VISIT_SEQ(c, stmt, s->v.For.orelse);
				compiler_use_next_block(c, end);
				return 1;
				"""

				yield 'for (...){}' #as function? for_x_in(ENV, X, IN) ? or can we use for directly?
				#else?  for_x_in_else(ENV, X, IN, ELSE_CALLBACK) ?
			elif TYPE == 'while': # TODO
				# TODO for else: use variable outside loop
				yield 'while (test){}' # map to while statement
				#else?  then use function?  while_x_else()
			elif TYPE == 'break':
				yield 'break;' # ? XXX TODO flow statements will set state of current block (from ENV)
				#raise ValueError('this is not the way to do', repr(TYPE))
			elif TYPE == 'continue':
				yield 'continue;'
				#raise ValueError('this is not the way to do', repr(TYPE))
			elif TYPE == 'try': # TODO
				# series of functions for each branch, with error checks in ENV on return
				#make a function to handle each try/except/finally/else block, do check after call for error status
				#error status is set on ENV so check is done after call returns

				# TODO what if yield is inside try statement?  we need to pre-scan for yield, or all flow statements, and assign the next function...  partition the blocks around the keywords
				#	-- so if try contains a yield (or other flow statement) then it switches the next try state
				#	-- TODO so the main try function needs to loop on the status of the try block and keep calling the current or doing the action required...
				#	-- the yield statement means set the status of the generator of the yield value, and set the next function to the one after the yield statement...  the try blocks inside would be in the same ENV...

				yield self.INDENT() + '_ERR_CHK(' + self.predefs[id(NODE)]['predefined_name'] + '(ENV)' + ');'

			elif TYPE == 'try_star': # v3.11+
				raise NotImplementedError(TYPE)
			elif TYPE == 'exception':
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

			elif TYPE == 'with': # TODO
				# This is ENV[as] = expression() and then call __enter__ and __exit__() methods of the instance...
				yield 'with'
				#value = with_x(ENV, X)
				#value = with_x_as(ENV, X, "<as_name>") # TODO multiple names?  just list the multiple individual calls?

			elif TYPE == 'with_item':
				#raise NotImplementedError(TYPE)
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

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
				predef_name = self.predefs[id(NODE)]['predefined_name']
				yield self.INDENT() + '_funcdef("' + name + '", ' + predef_name + ');' # this is just instantiation of the function instance into ENV from the definition defined at the top of the module
				#- if defined inside another function it needs to be defined in module global scope (all of them do actually, we'll run the code inside ModuleName_mainbody(...)

			elif TYPE == 'lambda':
				# NOTE: _lambda returns a lambda object with the predefined function referenced (so it can then be called by the user like a function)
				name = self.predefs[id(NODE)]['predefined_name']
				yield self.INDENT() + '_lambda(' + name + ')'
				#- just make a function for it

			elif TYPE == 'arguments': # TODO
				yield self.INDENT() + 'arguments()'

			elif TYPE == 'argument': # TODO
				yield self.INDENT() + 'arg'

			elif TYPE == 'return': # TODO
				if NODE['value'] is not None:
					value = self.fully_encode(NODE['value'])
				else:
					value = 'NULL'
				yield self.INDENT() + '_RETURN(' + value + ')'
				#map as return keyword?  return using function: SnapObject = RETURN(ENV) where we indicate we go up in scope

			elif TYPE == 'yield': # TODO
				# TODO yield statement becomes _RETURN(yield(ENV)) so ENV is set (and ENV is the iterator ENV)
				#yield self.INDENT() + 'yield'
				#need to create an iterator object, with a series of functions that handle each segment before yield...?
				#raise ValueError('this is not the way to do', repr(TYPE))
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

			elif TYPE == 'yield_from': # TODO
				#yield self.INDENT() + 'yield_from'
				#raise ValueError('this is not the way to do', repr(TYPE))
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

			elif TYPE == 'global': # TODO
				#register with ENV so assignments to this go to the top ENV
				# TODO make this behave like _attr/_item where it's a proxy and will forward to the appropriate attr...  so it just finds the global env, and holds a reference to it and the attr...
				names = ['_str("' + n + '")' for n in NODE['names']]
				args = '_a' + str(len(names)) + '(' + ', '.join(names) + ')'
				yield self.INDENT() + '_global(' + args + ');'

			elif TYPE == 'non_local': # TODO
				#register with ENV so assignments to this go to the parent ENV
				# TODO behaves like _attr or _global, but finds the first parent ENV with the attr
				names = ['_str("' + n + '")' for n in NODE['names']]
				args = '_a' + str(len(names)) + '(' + ', '.join(names) + ')'
				yield self.INDENT() + '_nonlocal(' + args + ');'

			elif TYPE == 'class_definition': # TODO
				#make type and instance functions, as well as methods in global scope, instantiate by calling the type
				name = NODE['name']
				predef_name = self.predefs[id(NODE)]['predefined_name']
				yield self.INDENT() + '_classdef("' + name + '", ' + predef_name + ');'


			elif TYPE == 'newline':
				# TODO
				'keep track of current c newlines, and add extra newlines, or just always add newlines to try to space the statements like they were in python'
				# TODO in the python decoder add spacers based on the line info, where needed inside any node with a body...

				# TODO also include python line/function info for debugging along with the c ones...
				yield '\n'

		def preprocess(self, NODE):

			'' # TODO basically do preprocess walk, and fill the data into the CTX (so we can analyze it without also getting all the string data...)
			# --predefinitions, imports, ... into CTX.persistent

			imports = self.imports
			predefs = self.predefs

			def num(TYPE):
				return len([True for n in predefs.values() if n['__type__'] == TYPE]) + 1

			def add_predef(PRE):
				predefs[id(PRE['__src__'])] = PRE
				PRE['count'] = len(predefs)

			for root in walk_tree(NODE):
				N = root[-1]
				TYPE = N['__type__']
				count = len(predefs)

				pre = {'__type__':'predefine_' + TYPE, '__src__':N, 'index':num('predefine_' + TYPE)}

				if TYPE == 'class_definition':
					add_predef(pre)
					pre['predefined_name'] = self.module_name + '_class_' + N['name']
					pre['predefined_type_name'] = self.module_name + '_type_' + N['name']
				elif TYPE == 'function_definition':
					add_predef(pre)
					pre['predefined_name'] = self.module_name + '_func_' + N['name']
				elif TYPE == 'lambda':
					add_predef(pre)
					pre['predefined_name'] = self.module_name + '_lambda' + str(pre['index'])
				elif TYPE == 'yield':
					search_root = root[:]
					while search_root and search_root[-1]['__type__'] != 'function_definition':
						search_root.pop(-1)
					assert search_root, 'unable to find yield origin! {}'.format([n['__type__'] for n in root])
					# check if already registered as a generator...
					# call remap_generator(function) -> the function call will return the instance of the generator class... (which we also need to register as class predefinition)
					#	-- remap_generator just creates class predef, with all the pieces of the broken method segments...
					# syntax: _YIELD(VALUE) will set local var, set next function, and return the value (with refcounting)
					'search for parent function in root, re-assign as generator type'
					# TODO
					# TODO yield could be inside try which might have already been coded...  is that an issue?  might not be...
				elif TYPE == 'try':
					# TODO make try a class to store state like iterators will...  maybe even connect the functions in the same kind of way...
					add_predef(pre)
					pre['predefined_name'] = self.module_name + '_try' + str(pre['index'])
					'''
					TODO:
					should look like:
					def try_func(ENV):
						<try body>
					def except...():
						<except body>
					def else():
						''
					def finally():
						<finally body>

					try()
					check_error()
					if error call exception block TODO what if it returns?  we need to store state as locals like with the generator...
						-- make try a class... check outside of the main call for a return value (using the class vars/env?)
					call finally()


					try():

						try_func(ENV, TRY_FEEDBACK_DICT):
							...

						if (TRY_FEEBACK_DICT['EXCEPTION'] == 1):
							exception1():
								...

						elif ...

						else:
							else_block()

						finally(ENV, TRY_FEEDBACK_DICT):
							...

						<check if raise from finally?>
					'''


				elif TYPE in (
					'list_comprehension',
					'set_comprehension',
					'generator_comprehension',
					'dictionary_comprehension',
					'comprehension',
					):

					# TODO

					name = {
						'list_comprehension':'list_comp',
						'set_comprehension':'set_comp',
						'generator_comprehension':'gen_comp',
						'dictionary_comprehension':'dict_comp',
						'comprehension':'comp',
					}[TYPE]

					add_predef(pre)
					pre['predefined_name'] = self.module_name + '_' + name + str(pre['index'])

					#item = self.fully_encode(NODE['item'])
					#generators = [self.fully_encode(g) for g in NODE['generators']]
					#args = '_a' + str(len(generators)) + '(' + ', '.join(generators) + ')'
					#yield self.INDENT() + name + '(' + item + ', ' + args + ')'
				#elif TYPE == 'set_comprehension': # TODO
				#	yield self.INDENT() + '_set_comp(...)'
				#elif TYPE == 'generator_expression': # TODO
					# This returns new generator
					# abstract generator = just a series of functions, they queue themselves up, so they just need to see the generator object to access the variables...
				#	yield self.INDENT() + '_gen_comp(...)'
					#** have to create iterable class to represent the generator...

				elif TYPE == 'bool_operation':
					if len(N['values']) > 2:
						add_predef(pre)
						pre['predefined_name'] = self.module_name + '_bool_op' + str(pre['index'])
				elif TYPE == 'comparison':
					if len(N['operators']) > 1:
						add_predef(pre)
						pre['predefined_name'] = self.module_name + '_compare' + str(pre['index'])


				# CONTROL FLOW

				elif TYPE == 'for':
					add_predef(pre)
					pre['predefined_name'] = self.module_name + '_for' + str(pre['index'])

					


				elif TYPE in ('import', 'import_from'):
					# NOTE: we have to register the ENV names because they can be files if they aren't attributes of a module...
					imports.append(N)


				if 'body' in N:
					'' # TODO register variables in ENV (for from import visibility)



		def fully_encode(self, NODE, indent_level=0):
			s = self.settings
			indent_before = s.get('indent_level', 0)
			s['indent_level'] = indent_level
			_return = ''.join(list(self.encode_element(NODE)))
			s['indent_level'] = indent_before
			return _return


		def encode_element(self, NODE):
			# https://docs.python.org/3/library/ast.html
			# input is ast json output from python_decoder.py
			"""
			SnapObject = structure of an object (simulates PyObj)
			SnapNode = usage of object with channels and listeners...

			** all of the utility functions would also implicitly take ENV as first arg...
			** assigns and variable access redirect to the ENV... (x = 1 becomes ENV['x'] = 1 but probably a bit more complex syntax)
				-- basic flow is to assign to ENV in the function and then return the value/result for use
			"""

			#if self.stack is None:
			#	self.stack = []
			#SUBROOTPATH = self.stack + [NODE] # premade for convenience... XXX TODO this is now push(NODE) and pop()

			#def fully_encode(N, indent_level=0):
			#	indent_before = self.indent_level
			#	self.settings['indent_level'] = indent_level
			#	_return = ''.join(list(self.encode_element(N)))
			#	#_return = ''.join(list(encode_element(SUBROOTPATH, N, CTX.subcontext(indent_level=indent_level))))
			#	self.settings['indent_level'] = indent_before
			#	return _return

			TYPE = NODE['__type__']

			# ROOT NODES:
			if TYPE == 'module': # TODO
				''#list of predefinitions (classes, functions, lambda, yield, imports, ...) - everything that needs to be declared at the top of the module
				yield '\n'

				# NOTE: imports/include statements and header guards will be handled externally to this module
				predefs = self.predefs

				#has_index = list(sorted([n for n in predefs.values() if 'index' in n], key=lambda x: -x['index']))
				#no_index = [n for n in predefs.values() if n not in has_index]

				for n in sorted(predefs.values(), key=lambda x: -x['count']):

					yield self.fully_encode(n)

					yield '\n'

				if self.is_headerfile:
					yield self.INDENT() + 'void ' + self.module_name + '__MAINBODY(SnapObject*);\n'
				else:
					yield self.INDENT() + 'void ' + self.module_name + '__MAINBODY(SnapObject* ENV){\n'

					yield '\n'

					for sub in NODE['body']:
						yield self.fully_encode(sub, indent_level=self.settings['indent_level']+1)
						yield '\n'

					yield '\n'
			
					yield self.INDENT() + '}\n'

			elif TYPE == 'input_expression':
				raise NotImplementedError(TYPE)
			elif TYPE == 'interactive':
				raise NotImplementedError(TYPE)
			elif TYPE == 'function_type':
				raise NotImplementedError(TYPE)

			# LITERALS:
			elif TYPE == 'constant':

				value = NODE['value']

				data_type = NODE['data_type']

				if data_type == 'string':
					yield self.INDENT() + '_str("' + repr(''.join(['\\'+c if c == '"' else c for c in value]))[1:-1] + '")' # TODO independent lines...?
				elif data_type == 'bytes':
					value = b64decode(value) # TODO how to represent bytes in c?
					yield self.INDENT() + '_bytes("' + repr(value)[2:-1] + '", ' + str(len(value)) + ')'
				elif data_type == 'integer':
					# bool isn't the right type??
					text = str(value)
					if text == 'True':
						yield self.INDENT() + '_bool(1)'
					elif text == 'False':
						yield self.INDENT() + '_bool(0)'
					else:				
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
				# ellipsis is deprecated; current ast.parse doesn't even allow it.
				else:
					raise NotImplementedError('constant type', type(value))

			elif TYPE == 'formatted_value': # v3.8+
				raise NotImplementedError(TYPE)
			elif TYPE == 'joined_string': # v3.8+
				raise NotImplementedError(TYPE)

			elif TYPE in ('list', 'tuple', 'set'):
				items = NODE['items']
				if items:
					#'_call(_get(ENV, "' + TYPE + '"), _msg())'
					item_list = ', '.join([self.fully_encode(item) for item in items])
					item_list = '_a' + str(len(items)) + '(' + item_list + ')'
					msg = '_msg_a(' + item_list + ')'
				else:
					msg = 'NULL'
				yield self.INDENT() + '_' + TYPE + '(' + msg + ')'

			elif TYPE == 'dictionary':

				msg_name = '_msg'

				using_arguments = [['a',None], ['A',None], ['k',None], ['K',None]]

				kwargs = []
				unpack_kwargs = None
				for k,v in zip(NODE['keys'], NODE['values']):
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

				yield self.INDENT() + '_dict(' + msg + ')'

			# VARIABLES:
			elif TYPE == 'name':
				name = NODE['value']
				context = NODE['context']['__type__']
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
				yield self.INDENT() + '_attr(ENV, "' + name + '")'
			elif TYPE == 'load':
				raise NotImplementedError(TYPE)
			elif TYPE == 'store':
				raise NotImplementedError(TYPE)
			elif TYPE == 'remove':
				raise NotImplementedError(TYPE)
			elif TYPE == 'starred': # TODO?
				#print('starred', NODE.keys())
				# _item(_slice(NULL, NULL, NULL))
				yield self.INDENT() + '_iter(' + self.fully_encode(NODE['value']) + ')'

			# EXPRESSIONS:
			elif TYPE == 'expression': # TODO?  probably just a passthrough
				# https://docs.python.org/3/library/ast.html#ast.Expr
				# this is used when return value isn't used or stored; statement by itself

				#if NODE['value']['__type__'] == 'call' and NODE['value']['base']['__type__'] == 'name' and NODE['value']['base']['value'] == 'snap_raw':
				#	args = NODE['value']['arguments']
				#	assert len(args) == 1 and args[0]['__type__'] == 'constant' and isinstance(args[0]['value'], str), 'snap_raw must be given single string argument'
				#	yield self.INDENT() + args[0]['value'] + ';'
				#else:
				yield self.INDENT() + '_DISCARD(' + self.fully_encode(NODE['value']) + ');'

			elif TYPE == 'unary_operation':
				op_name = self.fully_encode(NODE['operator'])
				yield self.INDENT() + op_name + '(' + self.fully_encode(NODE['operand']) + ')'

			elif TYPE == 'unary_add':
				#yield '_str("+")'
				yield '_uadd'
			elif TYPE == 'unary_subtract':
				#yield '_str("-")'
				yield '_usub'
			elif TYPE == 'not':
				#yield '_str("not")'
				yield '_unot'
			elif TYPE == 'bitwise_invert':
				#yield '_str("~")'
				yield '_uinv'

			elif TYPE == 'binary_operation':
				op_name = self.fully_encode(NODE['operator']) + '_op'
				left = self.fully_encode(NODE['left'])
				right = self.fully_encode(NODE['right'])
				yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'
				#yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'

			elif TYPE == 'add':
				#yield '_str("+")'
				yield '_add'
			elif TYPE == 'subtract':
				#yield '_str("-")'
				yield '_sub'
			elif TYPE == 'multiply':
				#yield '_str("*")'
				yield '_mul'
			elif TYPE == 'divide':
				#yield '_str("/")'
				yield '_div'
			elif TYPE == 'floor_divide':
				#yield '_str("//")'
				yield '_fldiv'
			elif TYPE == 'modulo':
				#yield '_str("%")'
				yield '_mod'
			elif TYPE == 'power':
				#yield '_str("**")'
				yield '_pow'
			elif TYPE == 'bitwise_left_shift':
				#yield '_str("<<")'
				yield '_lbit_shift'
			elif TYPE == 'bitwise_right_shift':
				#yield '_str(">>")'
				yield '_rbit_shift'
			elif TYPE == 'bitwise_or':
				#yield '_str("|")'
				yield '_bit_or'
			elif TYPE == 'bitwise_xor':
				#yield '_str("^")'
				yield '_bit_xor'
			elif TYPE == 'bitwise_and':
				#yield '_str("&")'
				yield '_bit_and'
			elif TYPE == 'matrix_multiply':
				raise NotImplementedError(TYPE)
			elif TYPE == 'bool_operation':

				if len(NODE['values']) == 2:
					op_name = self.fully_encode(NODE['operator']) + '_op'
					left = self.fully_encode(NODE['values'][0])
					right = self.fully_encode(NODE['values'][1])
					yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'
				else:
					assert len(NODE['values']) > 2
					predef = self.predefs[id(NODE)]
					yield self.INDENT() + predef['predefined_name'] + '(ENV)'

			elif TYPE == 'and':
				#yield '_str("and")'
				yield '_and'
			elif TYPE == 'or':
				#yield '_str("or")'
				yield '_or'
			elif TYPE == 'comparison':
				
				if len(NODE['operators']) == 1:
					# operands includes 'left', so it's len 1 for 2 elements
					assert len(NODE['operators']) == 1 and len(NODE['values']) == 1
					op_name = self.fully_encode(NODE['operators'][0]) + '_op'
					left = self.fully_encode(NODE['left'])
					right = self.fully_encode(NODE['values'][0])
					yield self.INDENT() + op_name + '(' + left + ', ' + right + ')'
				else:
					# multiple chained comparisons will be handled by custom predefined function, we just need to call it
					assert len(NODE['values']) > 1
					predef = self.predefs[id(NODE)]
					yield self.INDENT() + predef['predefined_name'] + '(ENV)'

			elif TYPE == 'equal':
				#yield '_str("==")'
				yield '_equal'
			elif TYPE == 'not_equal':
				#yield '_str("!=")'
				yield '_not_equal'
			elif TYPE == 'less_than':
				#yield '_str("<")'
				yield '_less_than'
			elif TYPE == 'less_or_equal':
				#yield '_str("<=")'
				yield '_less_or_equal'
			elif TYPE == 'greater_than':
				#yield '_str(">")'
				yield '_greater_than'
			elif TYPE == 'greater_or_equal':
				#yield '_str(">=")'
				yield '_greater_or_equal'
			elif TYPE == 'is':
				#yield '_str("is")'
				yield '_is'
			elif TYPE == 'is_not':
				#yield '_str("is not")'
				yield '_is_not'
			elif TYPE == 'in':
				#yield '_str("in")'
				yield '_in'
			elif TYPE == 'not_in':
				#yield '_str("not in")'
				yield '_not_in'

			elif TYPE == 'call': # TODO

				#self.push(NODE, indent_level=0)

				base = NODE['base']

				# XXX instead of raw just use standalone strings that start with "snapc:..." or something
				#if base['__type__'] == 'name' and base['value'] == 'snap_raw':
				#	#name = base['value']
				#	#if name == 'snap_raw':
				#	raise Exception('snap_raw needs to be handled in expression (it must be a standalone statement)')
				#	#else:
				#	#	#arguments = ''.join(list(encode_element(SUBROOTPATH, )))
				#	#	yield CTX.INDENT() + '_call(_get(ENV, "' + name + '"), _msg(...TODO))'
				#else:

				if NODE['arguments'] or NODE['keyword_arguments']:

					msg_name = '_msg'

					using_arguments = [['a',None], ['A',None], ['k',None], ['K',None]]
						
					#next_ctx = CTX.subcontext(indent_level=0) # XXX TODO push
					args = []
					unpack_args = None
					for arg in NODE['arguments']:
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
					for kwarg in NODE['keyword_arguments']:
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
				
				yield self.INDENT() + '_call(' + base_element + ', ' + msg + ')'

				#self.pop()

			elif TYPE == 'keyword':
				key = '_str("' + NODE['key'] + '")'
				value = self.fully_encode(NODE['value'])
				yield self.INDENT() + key + ', ' + value

			elif TYPE == 'if_expression': # TODO
				#* create a c function call to represent the body of each section
				#	** unpack single else: if into else if at same level...
				yield self.INDENT() + '(if (...){} else {})' # TODO just use c if else and (else if)

			elif TYPE == 'attribute':
				#print('attribute value', NODE['value'])
				base = self.fully_encode(NODE['value'])
				attr = NODE['attribute']
				if 0:#NODE['value']['__type__'] == 'name':
					# first access if from ENV
					base_stmt = '_attr(ENV, ' + base + ')'
				else:
					# all other accesses are from whatever the previous base return was
					base_stmt = base
				yield '_attr(' + base_stmt + ', _str("' + attr + '"))'

			elif TYPE == 'named_expression': # v3.8+
				raise NotImplementedError(TYPE)

			# SUBSCRIPTING:
			elif TYPE == 'subscript': # TODO
				# call(ENV, INSTANCE, "__getitem__", ARGS[0] = SnapSlice()) ?
				target = self.fully_encode(NODE['base'])
				key = self.fully_encode(NODE['key'])
				# TODO slice can assign, get, or delete...
				
				# TODO item is object, and we can use __setitem__ or other assignment to set/get?  like item = x or item.x or item['x']?  and it forwards to the request to the target...
				# XXX NOTE: _item is specifically __getitem__|__setitem__, _attr is __setattr__|__getattr__
				yield self.INDENT() + '_item(' + target + ', ' + key + ')'

			elif TYPE == 'slice':
				keys = []
				for attr in ('start','end','step'):
					x = NODE[attr]
					if x is None:
						keys.append('NULL')
					else:
						# NOTE: any type can be used as slice param
						keys.append(self.fully_encode(x))
				keys = ', '.join(keys)
				yield self.INDENT() + '_slice(' + keys + ')'

			# COMPREHENSIONS:
			elif TYPE in (
				'list_comprehension',
				'set_comprehension',
				'generator_comprehension',
				'dictionary_comprehension',
				'comprehension',
				):
				yield self.INDENT() + self.predefs[id(NODE)]['predefined_name'] + '(ENV)'

			# STATEMENTS:
			elif TYPE == 'assign':
				for sub in NODE['targets']:
					for root in walk_tree(sub): # TODO only check NODE['targets']
						if root[-1]['__type__'] == 'name':
							# for from import, need to know global names # TODO only if body is toplevel?
							self.register_ENV_name(root[-1]['value'])

				#print('targets', [n['__type__'] for n in NODE['targets']])
				len_targets = len(NODE['targets'])
				targets = ', '.join([self.fully_encode(e) for e in NODE['targets']])
				value = self.fully_encode(NODE['value'])
				# TODO multiple targets need to be merged, but how to know they are multiple and not unpacked?  make separate _assign_multi?
				if len_targets > 1:
					targets = '_a' + str(len_targets) + '(' + targets + ')'
				yield self.INDENT() + '_assign(' + targets + ', ' + value + ');'
				#-- value is SnapObject

			elif TYPE == 'annotated_assign': # 3.8+
				raise NotImplementedError(TYPE)

			elif TYPE == 'augmented_assign':
				target = NODE['target']
				assert target['__type__'] == 'name', 'only names supported for augassign right now {}'.format(target['__type__'])
				name = target['value']
				op = self.fully_encode(NODE['operator'])
				value = self.fully_encode(NODE['value'])
				# TODO op?  use as string?
				yield self.INDENT() + '_augassign(_attr(ENV, _str("' + name + '")), ' + op + ', ' + value + ')'

			elif TYPE == 'raise':
				assert NODE['from'] is None, 'unsupported from argument in raise'
				exception = self.fully_encode(NODE['exception'])
				yield self.INDENT() + '_RAISE(' + exception + ', NULL);\n' # EXCEPTION, LINEINFO

			elif TYPE == 'assert': # TODO
				test = self.fully_encode(NODE['test'])
				message = NODE['message']
				if message:
					assert message['__type__'] == 'constant' and isinstance(message['value'], str), 'assertion with non-string {}'.format(type(message['value']))
					message = '"'+''.join(['\\'+c if c == '"' else c for c in message['value']])+'"'
				else:
					message = 'NULL'
				# how about when we're inside a try block?  then we're inside a function for the try...  so we can call the finally clause...
				yield self.INDENT() + 'if (_as_bool(' + test + ')){return __RAISE(ENV, "AssertionError", ' + message + ');\n' #if test(...): raise(...) # message

			elif TYPE == 'delete': # TODO
				targets = NODE['targets']
				if len(targets) == 1:
					yield self.INDENT() + '_del(ENV, ' + self.fully_encode(targets[0]) + ')'
				elif len(targets) > 1:
					targets = [self.fully_encode(t) for t in NODE['targets']]
					args = '_a' + str(len(targets)) + '(' + ', '.join(targets) + ')'
					yield self.INDENT() + '_del_multi(ENV, ' + args + ')'# or call(ENV, INSTANCE, attr)
				else:
					raise NotImplementedError('del < 1??')

			elif TYPE == 'pass':
				# there is no pass statement in c, but we'll leave a comment to indicate the intention
				yield self.INDENT() + '/* pass */'

			elif TYPE == 'type_alias': # v3.8+
				raise NotImplementedError(TYPE)

			# IMPORTS:
			elif TYPE == 'import': # TODO
				statements = []
				for alias in NODE['names']:
					# TODO if dot in name here then we import the toplevel module and bring the subs in it's namespace
					statements.append(self.INDENT() + '_import("' + alias['name'] + '");') # TODO just localize the name here?  build?
				yield '\n'.join(statements) # so no trailing '\n'
				#NOTE: this is the keyword 'import', so we need to include, otherwise we would 'build' what we need into the ENV
				#- import can appear inside functions, we need to make it global (maybe delay the build until it is accessed from ENV?)

			elif TYPE == 'import_from': # TODO
				statements = []
				module = NODE['module']
				for alias in NODE['names']:
					if alias['as']:
						statements.append(self.INDENT() + '_import_from_as("' + module + '", "' + alias['name'] + '", "' + alias['as'] + '");')
					else:
						statements.append(self.INDENT() + '_import_from("' + module + '", "' + alias['name'] + '");')
				yield '\n'.join(statements) # so we only have newlines between them but don't end on one...
				#only bring in certain names?  write header with only those names?
			elif TYPE == 'import_alias':
				raise NotImplementedError(TYPE)

			# CONTROL FLOW:
			elif TYPE == 'if': # TODO
				# TODO if body contains single if statement, then bring it up into else if here, and use its else
				#if CTX.inline(): XXX only comprehensions do this, and they can generate their own code...
				#	# in one line
				#	yield CTX.INDENT() + 'if (test){} else {}'
				#else:
				# branch vertically

				#self.push(NODE)

				else_if = []

				# TODO contain the if statement in it's own function, like with does, so we can return from it on error...
				#	-- TODO predefine the if statement and then just call it directly here, this is the call... if_statement_1()

				yield self.INDENT() + 'if (_as_bool(test)){\n'
				for n in NODE['body']:
					for s in self.encode_element(n):
						yield s
					yield '\n'
				yield self.INDENT() + '}\n'
				yield self.INDENT() + 'else {\n'
				# TODO first line of else and else if do check if test raised an error?
				yield self.INDENT(1) + '/* TODO body */\n'
				yield self.INDENT() + '}'

				#self.pop()

			elif TYPE == 'for': # TODO
				# TODO for else: use else variable outside loop?

				# put inside own function like with and if statements...
				#	-- TODO predefine...

				# TODO define function then use the for statement inside of it so the keywords work...

				# TODO init the for in function, then assign start function to assign from the source to the target(s), unpack into ENV basically

				yield 'for (...){}' #as function? for_x_in(ENV, X, IN) ? or can we use for directly?
				#else?  for_x_in_else(ENV, X, IN, ELSE_CALLBACK) ?
			elif TYPE == 'while': # TODO
				# TODO for else: use variable outside loop
				yield 'while (test){}' # map to while statement
				#else?  then use function?  while_x_else()
			elif TYPE == 'break':
				yield 'break;' # ? XXX TODO flow statements will set state of current block (from ENV)
				#raise ValueError('this is not the way to do', repr(TYPE))
			elif TYPE == 'continue':
				yield 'continue;'
				#raise ValueError('this is not the way to do', repr(TYPE))
			elif TYPE == 'try': # TODO
				# series of functions for each branch, with error checks in ENV on return
				#make a function to handle each try/except/finally/else block, do check after call for error status
				#error status is set on ENV so check is done after call returns

				# TODO what if yield is inside try statement?  we need to pre-scan for yield, or all flow statements, and assign the next function...  partition the blocks around the keywords
				#	-- so if try contains a yield (or other flow statement) then it switches the next try state
				#	-- TODO so the main try function needs to loop on the status of the try block and keep calling the current or doing the action required...
				#	-- the yield statement means set the status of the generator of the yield value, and set the next function to the one after the yield statement...  the try blocks inside would be in the same ENV...

				yield self.INDENT() + '_ERR_CHK(' + self.predefs[id(NODE)]['predefined_name'] + '(ENV)' + ');'

			elif TYPE == 'try_star': # v3.11+
				raise NotImplementedError(TYPE)
			elif TYPE == 'exception':
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

			elif TYPE == 'with': # TODO
				# This is ENV[as] = expression() and then call __enter__ and __exit__() methods of the instance...
				yield 'with'
				#value = with_x(ENV, X)
				#value = with_x_as(ENV, X, "<as_name>") # TODO multiple names?  just list the multiple individual calls?

			elif TYPE == 'with_item':
				#raise NotImplementedError(TYPE)
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

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
				predef_name = self.predefs[id(NODE)]['predefined_name']
				yield self.INDENT() + '_funcdef("' + name + '", ' + predef_name + ');' # this is just instantiation of the function instance into ENV from the definition defined at the top of the module
				#- if defined inside another function it needs to be defined in module global scope (all of them do actually, we'll run the code inside ModuleName_mainbody(...)

			elif TYPE == 'lambda':
				# NOTE: _lambda returns a lambda object with the predefined function referenced (so it can then be called by the user like a function)
				name = self.predefs[id(NODE)]['predefined_name']
				yield self.INDENT() + '_lambda(' + name + ')'
				#- just make a function for it

			elif TYPE == 'arguments': # TODO
				yield self.INDENT() + 'arguments()'

			elif TYPE == 'argument': # TODO
				yield self.INDENT() + 'arg'

			elif TYPE == 'return': # TODO
				if NODE['value'] is not None:
					value = self.fully_encode(NODE['value'])
				else:
					value = 'NULL'
				yield self.INDENT() + '_RETURN(' + value + ')'
				#map as return keyword?  return using function: SnapObject = RETURN(ENV) where we indicate we go up in scope

			elif TYPE == 'yield': # TODO
				# TODO yield statement becomes _RETURN(yield(ENV)) so ENV is set (and ENV is the iterator ENV)
				#yield self.INDENT() + 'yield'
				#need to create an iterator object, with a series of functions that handle each segment before yield...?
				#raise ValueError('this is not the way to do', repr(TYPE))
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

			elif TYPE == 'yield_from': # TODO
				#yield self.INDENT() + 'yield_from'
				#raise ValueError('this is not the way to do', repr(TYPE))
				yield self.INDENT() + '/* TODO ' + TYPE + ' ' + str(NODE.keys()) + '*/'

			elif TYPE == 'global': # TODO
				#register with ENV so assignments to this go to the top ENV
				# TODO make this behave like _attr/_item where it's a proxy and will forward to the appropriate attr...  so it just finds the global env, and holds a reference to it and the attr...
				names = ['_str("' + n + '")' for n in NODE['names']]
				args = '_a' + str(len(names)) + '(' + ', '.join(names) + ')'
				yield self.INDENT() + '_global(' + args + ');'

			elif TYPE == 'non_local': # TODO
				#register with ENV so assignments to this go to the parent ENV
				# TODO behaves like _attr or _global, but finds the first parent ENV with the attr
				names = ['_str("' + n + '")' for n in NODE['names']]
				args = '_a' + str(len(names)) + '(' + ', '.join(names) + ')'
				yield self.INDENT() + '_nonlocal(' + args + ');'

			elif TYPE == 'class_definition': # TODO
				#make type and instance functions, as well as methods in global scope, instantiate by calling the type
				name = NODE['name']
				predef_name = self.predefs[id(NODE)]['predefined_name']
				yield self.INDENT() + '_classdef("' + name + '", ' + predef_name + ');'


			elif TYPE == 'newline':
				# TODO
				'keep track of current c newlines, and add extra newlines, or just always add newlines to try to space the statements like they were in python'
				# TODO in the python decoder add spacers based on the line info, where needed inside any node with a body...

				# TODO also include python line/function info for debugging along with the c ones...
				yield '\n'


			# PREDEFINITIONS
			elif TYPE == 'predefine_function_definition':
				# TODO decorators

				#self.push(NODE)

				SRC = NODE['__src__']
				module_name = self.module_name
				#function_name = module_name + '_' + 'func' + str(NODE['index']) + '_' + SRC['name']
				yield 'SnapObject* ' + NODE['predefined_name'] + '(SnapObject* ENV, SnapObject* MSG){\n'
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

			elif TYPE == 'predefine_class_definition':
				# TODO decorators?
				SRC = NODE['__src__']

				# TODO type() must be hardcoded!  -- translate into hard compiled definition

				# NOTE: class type handler is just attribute access, so it doesn't accept a message

				yield 'SnapObject* ' + NODE['predefined_name'] + '(SnapObject* ENV, SnapObject* INSTANCE, const char* ATTR){\n'
				yield self.INDENT(1) + 'ENV = _LOCAL_ENV(ENV);\n\n'

				yield self.INDENT(1) + '_RETURN(NULL);\n'
				yield self.INDENT() + '}\n'

			elif TYPE == 'predefine_lambda':

				name = NODE['predefined_name']

				yield 'SnapObject* ' + name + '(SnapObject* ENV, SnapObject* MSG){\n'

				yield '\n'
				yield self.INDENT(1) + '/* TODO: verify arguments and ENV is the MSG? */\n\n' # TODO unpack MSG into local ENV
				# TODO lambda is single statement so we can just return the output of the whole statement?

				SRC = NODE['__src__']

				body = self.fully_encode(SRC['body'])

				#yield self.INDENT() + '_lambdef(' + name + ');\n'
				yield self.INDENT(1) + '_RETURN(' + body + ');\n'
				yield self.INDENT() + '};\n'

			elif TYPE == 'predefine_bool_operation':

				SRC = NODE['__src__']

				#print(SRC.keys())

				name = NODE['predefined_name']

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

			elif TYPE == 'predefine_comparison':

				SRC = NODE['__src__']

				yield self.INDENT() + 'SnapObject* ' + NODE['predefined_name'] + '(SnapObject* ENV){\n\n'

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


			# COMPREHENSIONS
			elif TYPE in (
				'predefine_list_comprehension',
				'predefine_generator_comprehension',
				'predefine_set_comprehension',
				'predefine_dictionary_comprehension',
				'predefine_comprehension',
				):

				SRC = NODE['__src__']

				yield self.INDENT() + 'SnapObject* ' + NODE['predefined_name'] + '(SnapObject* ENV){\n\n'

				yield self.INDENT(1) + '/* TODO: ' + TYPE + ' ' + str(SRC.keys()) + '*/\n' # TODO

				yield self.INDENT() + '}\n'


			elif TYPE == 'predefine_try':

				SRC = NODE['__src__']

				yield self.INDENT() + 'SnapObject* ' + NODE['predefined_name'] + '(SnapObject* ENV){\n\n'

				# TODO local env

				for stmt in SRC['body']:
					yield self.INDENT(1) + self.fully_encode(stmt) + '\n'

				yield self.INDENT(1) + '/* TODO try ' + str(SRC.keys()) + ' */\n'

				# TODO check for error and handle via exception blocks and call finally no matter what

				yield self.INDENT() + '}\n'


			elif TYPE == 'predefine_for':

				SRC = NODE['__src__']

				yield 'SnapObject* ' + NODE['predefined_name'] + '(SnapObject* ENV){\n\n'

				# TODO register start and end function, on block

				# TODO start does assign of variables to ENV

				yield self.INDENT(1) + '/* TODO for ' + str(SRC.keys()) + ' */\n\n'

				yield self.INDENT() + '}\n'

			# XXX import logic will be external to this module (includes)
			elif TYPE == 'predefine_import':
				pass
			elif TYPE == 'predefine_import_from':
				pass

			else:
				raise TypeError('unknown type', repr(TYPE))


		def encode(self, JSON):
			# encodes the abstract ast (postprocessed) from python syntax (python_decoder.py) into a python-like c mapping (not directly c syntax)

			assert JSON['__type__'] == 'module', 'only module type supported right now...'

			self.__op_index__ = 0

			#wrapped = wrap_tree(JSON)
			self.preprocess(JSON)
			for s in self.encode_element(JSON):
				yield s

			self.__op_index__ = -1



		def reset(self):

			self.settings['indent_level'] = 0
			self.imports = []
			self.stack = []
			self.predefs = {}

		def __init__(self, **SETTINGS):

			# TODO indent stack?  the we push and pull for 'current context' rather than creating new context?  context is now self...

			self.settings = {
				'indent_level':0,
				'indent_token':'\t',
				}
			self.imports = []
			self.stack = [] # list of json nodes, maybe stored in another dict so other info can be added...
			self.predefs = {}

			if SETTINGS:
				self.set(**SETTINGS)

	ENV.SnapCCompiler = SnapCCompiler

def main(ENV):

	import os
	THISDIR = os.path.realpath(os.path.dirname(__file__))

	PATH = os.path.join(THISDIR, 'language/python/test/everything.py')

	EXAMPLE = """
x = 1
	"""

	if 0:
		with open(PATH, 'r') as openfile:
			EXAMPLE = openfile.read()

	j = ENV.LANGUAGE.python.decode(EXAMPLE, generalize=True)
	#printout(j)

	#sys.exit(0)

	outfile = os.path.join(THISDIR, 'test.c')

	with open(outfile, 'w') as openfile:

		c = ENV.SnapCCompiler(filepath=PATH)
		for s in c.encode(j):
			#print(s, end='')
			openfile.write(s)

	ENV.snap_out('output saved to', outfile)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	ENV = SnapEnv()
	if not getattr(ENV, 'SnapCCompiler', None):
		build(ENV)
	main(ENV)

