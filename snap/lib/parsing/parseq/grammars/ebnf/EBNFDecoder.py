
#from snap.lib.parsing.parseq import *
import json
def print_dict(DICT):
	print(json.dumps(DICT, indent=1))

# https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form
# https://dwheeler.com/essays/dont-use-iso-14977-ebnf.html
	# https://www.w3.org/TR/xml/#sec-notation
"""
definition 	= :
concatenation 	,
termination 	;
alternation 	|
optional 	[ ... ]
repetition 	{ ... }
grouping 	( ... )
terminal string 	" ... "
terminal string 	' ... '
comment 	(* ... *)
special sequence 	? ... ?
exception 	! -

"""

def build(ENV):

	ParseqDecoder = ENV.ParseqDecoder
	ParseqSequence = ENV.ParseqSequence

	snap_binary_search = ENV.snap_binary_search

	snap_out = ENV.snap_out
	snap_warning = ENV.snap_warning
	snap_error = ENV.snap_error
	snap_debug = ENV.snap_debug

	ITEM = ENV.ParseqITEM
	AND = ENV.ParseqAND
	OR = ENV.ParseqOR
	NOT = ENV.ParseqNOT
	REPEAT = ENV.ParseqREPEAT
	ANY = ENV.ParseqANY
	OPTIONAL = ENV.ParseqOPTIONAL
	RANGE = ENV.ParseqRANGE
	UNDEFINED = ENV.ParseqUNDEFINED
	LAYER = ENV.ParseqLayer
	BEHIND = ENV.ParseqBEHIND
	POSITION = ENV.ParseqPOSITION

	ERROR = ENV.PARSEQ_ERROR

	class EBNFDecoder(ParseqDecoder):

		# turns text into ParseqRule tree

		def decode_result(self, RESULT, PREDEFINITIONS, **SETTINGS):

			# TODO option to add optional OR(..., ERROR) when it makes sense (?) for precise parsing error feedback...
			
			if not RESULT:
				self.report_bad_result(RESULT)
				raise ValueError('empty result')

			name = RESULT.name()

			# NOTE: this only returns dict representations of the rules (to get around the dependency issues...)

			if name == 'statement':

				first = RESULT.find('declaration').subs()[0]
				if first.name() == 'name':
					decl_name = first.value()
				elif first.name() == 'string':
					# this allows redefinition of a string (so when string is referred in grammar it can mean something other than an item literal)

					print('redefine', name)
					# TODO does this create a cyclic dependency if this defines it's own string?
					decl_name = '"'+first.value()[1:-1]+'"'
				else:
					raise TypeError('declaration start invalid?', RESULT.line_info())

				#decl_name = RESULT.find('declaration','name').value()
				assert decl_name != None, 'invalid declaration name: "{}"'.format(decl_name)
				if decl_name in PREDEFINITIONS and 'type' in PREDEFINITIONS[decl_name]:
					raise NameError('decl name {} already exists; redefined'.format(repr(decl_name)), RESULT.line_info())
				existing = PREDEFINITIONS[decl_name] = PREDEFINITIONS.get(decl_name, {'name':decl_name})
				if not existing.get('rule') and not existing.get('type'): # including defined as None
					# then define, otherwise leave it alone
					expr = RESULT.subs()[-1]
					n = self.decode_result(expr, PREDEFINITIONS)
					expr_name = n.get('name')
					if not expr_name:
						# take on the assign as own identity (hence update())
						assert n.get('refcount',0) <= 1, 'trying to merge shared rule into statement; oops'
						try: del n['refcount']
						except: pass
						existing.update(n)
					else:
						# add as child (either is named or has no type)
						#snap_warning("add as child", decl_name, expr_name, n.get('type'))
						existing.update({'type':'AND', 'children':[n]})
						if expr_name == decl_name and 'refcount' in n:
							n['refcount'] -= 1 # don't incref self TODO full tree scan for self?

			elif name == 'name':
				token = RESULT.value()
				rulemap = PREDEFINITIONS[token] = PREDEFINITIONS.get(token, {'name':token})
				rulemap['refcount'] = rulemap.get('refcount',0) + 1
				return rulemap

			elif name == 'string':
				value = RESULT.value()[1:-1] # without quotes
				strname = '"' + value + '"' # force double quotes as only used ones (quoted to prevent name collisions with non-items)
				rulemap = PREDEFINITIONS[strname] = PREDEFINITIONS.get(strname, {'type':'ITEM', 'name':strname, 'settings':{'value':value}})
				rulemap['refcount'] = rulemap.get('refcount',0) + 1
				return rulemap

			elif name == 'and_list':
				subs = RESULT.subs()
				if len(subs) == 1:
					return self.decode_result(subs[0], PREDEFINITIONS)
				return {
					'type':'AND',
					'children':[self.decode_result(r, PREDEFINITIONS) for r in subs],
					'refcount':1,
				}

			elif name == 'or_list':
				# group all the strings into ANY? and then add anything else? -- make sure the result is in length order or we have to split it up further...
				subs = RESULT.subs()
				return {
					'type':'ANY' if all([s.name() == 'string' for s in subs]) else 'OR',
					# TODO make sure children are in match order?  (length)  TODO do that when constructing the rule?
					'children':[self.decode_result(r, PREDEFINITIONS) for r in subs],
					'refcount':1,
				}

			elif name == 'optional':
				return {
					'type':'OPTIONAL',
					'children':[self.decode_result(r, PREDEFINITIONS) for r in RESULT.subs()],
					'refcount':1,
				}

			elif name == 'group':
				# NOTE: parse would fail if group is empty, so we can assume it isn't
				subs = RESULT.subs()
				if len(subs) == 1:
					# return sub?  would be name, string, or another list of its own type...
					return self.decode_result(subs[0], PREDEFINITIONS)
				else: # > 1
					return {
						'type':'AND',
						'children':[self.decode_result(r, PREDEFINITIONS) for r in subs],
						'refcount':1,
					}

			elif name == 'repeat_term':
				subs = RESULT.subs()
				assert subs, 'repeat without subs??'
				assert len(subs) == 2, 'repeat subs != 2'
				minimum = 0 if subs[-1].name() == '*' else 1 # '+'
				if subs[0].name() == 'group':
					# don't bother with subgroup, since REPEAT itself is a grouping...
					subs = subs[0].subs()
				else:
					subs = [subs[0]]
				return {
					'type':'REPEAT',
					'settings':{'min':minimum},
					'children':[self.decode_result(r, PREDEFINITIONS) for r in subs],
					'refcount':1,
				}

			elif name == 'not_term':
				# TODO if all string use NOTANY?  to force ANY could put into subgroup...? or use a different symbol like !~ for NOTANY
				return {
					'type':'NOT',
					'children':[self.decode_result(r, PREDEFINITIONS) for r in RESULT.subs()],
					'refcount':1,
				}

			elif name == 'range_term':

				assert all([s.name() == 'string' for s in RESULT.subs()]), 'non-string in range? {}'.format(RESULT.subs())
				assert len(RESULT.subs()) == 2, 'incorrect string args for {}'.format(repr(name))

				strings = [self.decode_result(r, PREDEFINITIONS) for r in RESULT.subs()]

				assert all([len(s['settings']['value']) == 1 for s in strings]), 'only single character strings are supported for ranges right now {}'.format(RESULT.subs())

				return {
					'type':'RANGE',
					'children':strings,
					'refcount':1,
				}

			else:
				snap_warning("unhandled result", RESULT, repr(RESULT.value()), '\n\t', RESULT.line_info())
				raise ValueError(RESULT) # can't return None, it's a disaster!

		def walk_rulemap(self, ROOT, **SETTINGS):

			if not ROOT:
				return

			#topdown = SETTINGS.get('topdown', True) # XXX not needed
			algorithm = SETTINGS.get('algorithm', 'DFS')
			assert algorithm in ('DFS', 'BFS'), 'unknown algorithm: {}'.format(algorithm)
			
			# rootpath and children, to make it easy to initialize all child nodes and assign them in one set(items=) call
			SEEN = []
			QUEUE = [[[ROOT], ROOT.get('children',[])[:]]]
			while QUEUE:

				rootpath,children = QUEUE.pop(0)
				idx = snap_binary_search(SEEN, id(rootpath[-1]), lambda x: id(x), True)
				if idx < len(SEEN) and id(SEEN[idx]) == id(rootpath[-1]):
					continue
				SEEN.insert(idx, rootpath[-1])
				yield rootpath,children

				next_list = [[rootpath + [child], child.get('children',[])[:]] for child in children]			

				if algorithm == 'DFS':
					QUEUE = next_list + QUEUE
				else:
					QUEUE = QUEUE + next_list


		def print_rulemap(self, ROOT, **SETTINGS):

			if not ROOT:
				print('<NULL>')
				return

			indent = SETTINGS.get('indent', '  ')

			for rootpath,children in self.walk_rulemap(ROOT):
				root = rootpath[-1]

				const_keys = ('name','type','refcount')

				main = [k + ':' + str(root.get(k)) for k in const_keys if root.get(k)]
				extras = [k + ':' + str(v) for k,v in root.items() if k not in const_keys and k != 'children']
				if children:
					extras.append('children:(' + str(len(children)) + ')')

				print(indent * (len(rootpath)-1) + '<' + ' '.join(main + extras) + '>')

		def rulemap_evaluation_length(self, ROOT, **SETTINGS):

			SEEN = SETTINGS.get('seen', [])

			length = 0
			for rootpath,children in self.walk_rulemap(ROOT):
				root = rootpath[-1]

				idx = binary_search(SEEN, id(root), lambda x: id(x), True)
				if idx < len(SEEN) and id(SEEN[idx]) == id(root):
					continue
				SEEN.insert(idx, root)

				rule_type = root.get('type')

				if rule_type in ('OR','ANY'):
					# just add length of longest one...
					assert len(children) > 0, 'no children {}'.format(root)
					length += max([self.rulemap_evaluation_length(child, seen=SEEN) for child in children])
					del children[:]
					continue

				elif rule_type == 'REPEAT':

					min = root['settings']['min']
					if min > 0:
						length += min * sum([self.rulemap_evaluation_length(child, seen=SEEN) for child in children])
					del children[:]
					continue

				elif rule_type == 'ITEM':
					length += len(root['settings']['value'])

				elif not rule_type or rule_type in ('OPTIONAL','AND','NOT'):
					continue

				#length += 1 # just consider each rule a thing, probably over simplistic, but...

			return length
				

		def check_declaration_count(self, SEQUENCE):
			# for debugging
			original_pos = SEQUENCE.position()
			original_sublayer_pos = self.sublayer().position()

			result_count = 0
			while 1:
				result = self.search_with_result(SEQUENCE)
				if not result:
					break
				#print(result, repr(result.value()))
				result_count += 1

			SEQUENCE.set(position=original_pos)

			snap_out('sub pos', self.sublayer().position(), original_pos)
			declaration = self.sublayer().get_named('declaration')
			count = 0
			while 1:
				result = declaration.search(SEQUENCE)
				if not result:
					break
				count += 1

			SEQUENCE.set(position=original_pos)
			snap_out('sub pos', self.sublayer().position(), original_pos)
			self.sublayer().set(position=original_sublayer_pos) # TODO find a way to make this less confusing!  (SEQUENCE should decide position...)

			if count == result_count:
				snap_out('total results:', count, '==', result_count)
			else:
				snap_error('total results:', count, '!=', result_count, '(count mismatch!)')
			#assert count == result_count, 'count mismatch: {} != {}'.format(count, result_count)
			return count
			

		def decode(self, sequence=None, **SETTINGS):

			assert isinstance(sequence, ParseqSequence) and isinstance(sequence.source(), str), 'text input must be string'

			#self.check_declaration_count(sequence)

			# user can define ANY rule themselves (not just undefined ones)
			user_definitions = SETTINGS.get('definitions',{})

			# if user rule has children? then user rule must be able to accept children, 
			# that is it's responsibility... undefined rules will by definition not have
			# children since a statement is required to assign them!
			PREDEFINITIONS = {k:{'type':'USER', 'name':k, 'rule':v} for k,v in user_definitions.items()}

			while 1:
				result = self.search_with_result(sequence)
				if not result:
					break
				self.decode_result(result, PREDEFINITIONS)


			ROOTS = []

			#roots = [rulemap for rulemap in PREDEFINITIONS.values() if not rulemap.get('refcount')] 
			for key,rulemap in PREDEFINITIONS.items():
				rule_name = rulemap.get('name')
				if not rulemap.get('refcount'): # includes refcount 0
					if rule_name and rule_name in user_definitions:
						snap_warning("not assigning user rule to roots", rule_name)
						continue
					#print('root: "{}"'.format(rule_name))
					ROOTS.append(rulemap)
				if key != rule_name:
					snap_warning("name mismatch?", key, rule_name)

				#if key in ('[',']','{','}'):
				#	print(rulemap)

			assert ROOTS, 'no root??' # TODO single rule that references itself?

			CHILD_ASSIGN = []

			# first pass, create all rules
			for root in ROOTS:

				for rootpath,children in self.walk_rulemap(root):
					rulemap = rootpath[-1]

					# TODO assign to CHILD_ASSIGN here
					if children:
						idx = snap_binary_search(CHILD_ASSIGN, id(rulemap), lambda e: id(e[0]), True)
						if idx < len(CHILD_ASSIGN) and id(CHILD_ASSIGN[idx][0]) == id(rulemap):
							#print('already listed in child assign', rulemap.get('name'))
							pass
						else:
							CHILD_ASSIGN.insert(idx, (rulemap, children))

					if rulemap.get('rule'):
						continue

					rule_type = rulemap.get('type')
					if rule_type == 'USER':
						raise ValueError('rulemap has "USER" type, without pre-existing "rule" definition!', rulemap.get('name'))

					rule_name = rulemap.get('name')

					if not rule_type:
						#print('UNDEFINED "{}"'.format(rule_name))
						r = UNDEFINED(name=rule_name)
					else:
						r = {'ITEM':ITEM, 'AND':AND, 'OR':OR, 'NOT':NOT, 'REPEAT':REPEAT,'ANY':ANY, 'OPTIONAL':OPTIONAL, 'RANGE':RANGE}[rule_type]()

						if rule_name:
							r.set(name=rule_name)

						settings = rulemap.get('settings')
						if settings:
							r.set(**settings)

						# NOTE: ANY does it's own sorting, and OR... kind of up to the user?
						#if rule_type in ('ANY','OR') and 'children' in rulemap:
						#	children = rulemap['children'][:]
						#	children.sort(key=lambda x: self.rulemap_evaluation_length(x) * -1)
						#	print('sorted', rule_name, rule_type, [r.get('name') for r in children])

					rulemap['rule'] = r

			# assign children in secondary pass, so all rules already exist
			for parent,children in CHILD_ASSIGN:
				parent['rule'].set(items=[child['rule'] for child in children])

			assert ROOTS, 'nothing found?'
			if len(ROOTS) > 1:
				return [r['rule'] for r in ROOTS] # let the caller decide what do with these
			return ROOTS[0]['rule'] # otherwise just return topnode




		def __init__(self, *args, **kwargs):
			ParseqDecoder.__init__(self, *args, **kwargs)

			# do a first pass to find all the names and their type, make them exist, then connect them?

			# TODO ERROR = OR(NOTANY(), POSITION(position=-1), POSITION(position=0)) ?
			#ERROR = NOTANY(name='ERROR', capture=True)

			multiline_comment = OR(
				AND('(*', REPEAT(NOT('*)'), min=0), OR(AND('*)'), ERROR)),
				AND('/*', REPEAT(NOT('*/'), min=0), OR(AND('*/'), ERROR)),
				name='multiline_comment')
			singleline_comment = AND('#', REPEAT(NOT('\n'), min=0),
				name='singleline_comment')
			comment = OR(multiline_comment, singleline_comment,
				name='comment', capture=False, suppress=True)

			string = OR(
				AND("'", REPEAT(NOT("'"), min=0), OR("'", ERROR)),
				AND('"', REPEAT(NOT('"'), min=0), OR('"', ERROR)),
				name='string')

			symbol = ANY(*[ITEM(name=s,value=s,capture=True) for s in (
				'(',')', # group
				'[',']', # optional
				'{','}', # repetition
				'?', # special
				'!', '-', # exception
				#'=',':', # definition (moved to own rule)
				#',', # concatenation # XXX use spaces (just add this to ignore)
				';', # termination
				'|', # alternation
				'+','*', # also-repetition
				'~', # range: 'a' ~ 'z'
				)],
				capture=False # let the symbols get captured themselves
				)

			name_continue = OR(RANGE('A','Z'), RANGE('a','z'), RANGE('0','9'), '_')
			name = AND(OR(RANGE('A','Z'), RANGE('a','z'), '_'), REPEAT(name_continue, min=0, max=-1),
				name='name')

			ignore = ANY(' ','\t','\n', ',',
				capture=False, suppress=True)

			declaration = AND(OR(BEHIND('\n'), POSITION(position=0)), OR(string, name), REPEAT(ANY(' ','\t','\n'), min=0), ANY('=',':'),
				name='declaration')

			sublayer = LAYER(

				comment,
				declaration,
				string,
				symbol,
				name,
				
				ignore,
				ERROR
				)
			self.set(sublayer=sublayer)


			# based on the pyparsing example in 'ref' folder (thanks!):

			l1 = sublayer.itemize()

			for item in l1.values():
				if item.name() in ('[',']','{','}','(',')','|','!','-',';','~'):
					# we need to not capture so it isn't in results, and we need to suppress the sublayer...
					item.set(capture=False, suppress=True)

			expr = OR(name='expr', capture=False)

			# ?:
			#special_sequence = AND(l1['?'], REPEAT(NOT(l1['?']), min=0, name='special_sequence'), OR(l1['?'], ERROR))
			#repetition = AND('{', REPEAT(NOT('}'), min=0, name='repetition'), OR('}', ERROR))

			optional = AND(l1['['], expr, OR(l1[']'], ERROR),
				name='optional')
			group = AND(l1['('], expr, OR(l1[')'], ERROR),
				name='group')

			term = OR(l1['name'], l1['string'], optional, group,
				name='term', capture=False)


			repeat_term = AND(term, OR(l1['*'], l1['+']),
				name='repeat_term')
			not_term = AND(OR(l1['!'], l1['-']), OR(repeat_term, term),
				name='not_term')

			range_term = AND(l1['string'], l1['~'], l1['string'],
				name='range_term')

			element = OR(not_term, repeat_term, range_term, term,
				name='element', capture=False)

			and_list = AND(element, REPEAT(element, min=0),
				name='and_list')

			or_list = AND(and_list, REPEAT(l1['|'], and_list, min=1),
				name='or_list')


			expr.set(items=[or_list, and_list])#, element])

			statement = AND(l1['declaration'], expr, OPTIONAL(l1[';']),
				name='statement')
			

			self.set(items=[

				statement,

				ERROR
				])

	ENV.EBNFDecoder = EBNFDecoder
	return EBNFDecoder

def main(ENV):

	build(ENV)

	import os

	THIS_DIR = os.path.dirname(os.path.realpath(__file__))

	GRAMMAR_FILE = os.path.join(THIS_DIR, 'PythonGrammar')

	decoder = ENV.EBNFDecoder()
	
	single_input = decoder.decode_file(
				GRAMMAR_FILE,
				#definitions = {k:ParseqLayerITEM(name=k) for k in (
				#	'STRING','NAME','NUMBER','NEWLINE','INDENT','DEDENT')} # no more BACKTICKS
				)
	single_input.print_tree()

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

