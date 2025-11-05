
import os, subprocess
import json

THISDIR = os.path.realpath(os.path.dirname(__file__))

# https://stackoverflow.com/questions/15800230/how-can-i-dump-an-abstract-syntax-tree-generated-by-gcc-into-a-dot-file
# https://gcc.gnu.org/onlinedocs/gcc/Developer-Options.html
# https://icps.u-strasbg.fr/~pop/gcc-ast.html
# https://www.codingwiththomas.com/blog/accessing-gccs-abstract-syntax-tree-with-a-gcc-plugin

# or use clang? https://lwn.net/Articles/629259/
# https://bastian.rieck.me/blog/2015/baby_steps_libclang_ast/
# https://stackoverflow.com/questions/59102944/how-to-represent-clang-ast-in-json-format
#clang -Xclang -ast-dump=json -fsyntax-only example.c
# with span info (could use json to help navigate this):
#clang -Xclang -ast-dump -fsyntax-only example.c

# https://clang.llvm.org/docs/index.html
	# https://clang.llvm.org/docs/IntroductionToTheClangAST.html
#https://clang.llvm.org/doxygen/ (or search "clang <name>" of nodes)

# https://github.com/llvm/llvm-project
# https://github.com/llvm/llvm-project/blob/main/clang/lib/AST/JSONNodeDumper.cpp


"""

The Clang Abstract Syntax Tree (AST) does not have a single, unified list of "kinds" because its nodes are structured in a class hierarchy without a common ancestor. Instead, the AST is built upon several core hierarchies, primarily centered around Declarations (Decl), Statements (Stmt), and Types (Type). Expressions (Expr) are also a subclass of Stmt.
Therefore, the "kinds" of Clang AST nodes are numerous and correspond to the various specialized classes within these hierarchies. Some prominent examples include:
Declaration Kinds (derived from Decl):
TranslationUnitDecl, FunctionDecl, VarDecl, CXXRecordDecl (for classes and structs), EnumDecl, TypedefDecl, ParmVarDecl, FieldDecl, and NamespaceDecl.
Statement Kinds (derived from Stmt, including Expr):

    CompoundStmt
    IfStmt
    ForStmt
    WhileStmt
    ReturnStmt
    BinaryOperator (e.g., +, -, *)
    CallExpr
    DeclRefExpr (reference to a declared entity)
    MemberExpr (accessing a member of a class/struct)
    ImplicitCastExpr
    MaterializeTemporaryExpr

Type Kinds (derived from Type):
BuiltinType (e.g., int, char, float), PointerType, RecordType, FunctionProtoType, ArrayType, and ElaboratedType.
This is not an exhaustive list, but it illustrates the diversity of AST node kinds within Clang. The specific kind of a node can be retrieved at runtime using methods like getTypeClass() for Type objects, or through runtime type information for Decl and Stmt objects. Tools like AST Matchers and RecursiveASTVisitor are used to navigate and identify these various node kinds within the AST.

"""

"""
TranslationUnitDecl
FunctionDecl
VarDecl
CXXRecordDecl (classes and structs)
EnumDecl
TypedefDecl
ParmVarDecl
FieldDecl
NamespaceDecl
Stmt
	Expr
	CompoundStmt
	IfStmt
	ForStmt
	WhileStmt
	ReturnStmt
	BinaryOperator (+, -, *, ...)
	CallExpr
	DeclRefExpr (reference to a declared entity)
	MemberExpr (acessing a member of a class/struct)
	ImplicitCastExpr
	MaterializeTemporaryExpr
Type
	BuiltinType (int, char, float, ...)
	PointerType
	RecordType
	FunctionProtoType
	ArrayType
	ElaboratedType
	
"""

"""
"list of all clang ast types"

The Clang Abstract Syntax Tree (AST) represents the parsed structure of C-family languages. It's built upon a class hierarchy, primarily centered around statements (Stmt) and declarations (Decl), with expressions (Expr) being a specific type of statement. Additionally, there's a distinct hierarchy for Type nodes, which describe the types of variables, expressions, and functions.
Key Clang AST Node Categories:

    Declarations (Decl): Represent declared entities in the code.
        TranslationUnitDecl: The root of the AST, representing the entire translation unit.
        FunctionDecl: Represents a function declaration.
        VarDecl: Represents a variable declaration.
        ParmVarDecl: Represents a function parameter declaration.
        EnumDecl: Represents an enumeration declaration.
        EnumConstantDecl: Represents an enumerator within an enum.
        RecordDecl (and its subclasses like CXXRecordDecl, ClassTemplateDecl): Represent class, struct, or union declarations.
        NamespaceDecl: Represents a namespace declaration.
        TypedefDecl/TypeAliasDecl: Represents type definitions.
        FieldDecl: Represents a member variable within a class/struct.
        ObjCInterfaceDecl, ObjCImplementationDecl, ObjCProtocolDecl, ObjCMethodDecl: Specific to Objective-C. 
    Statements (Stmt): Represent executable code blocks.
        CompoundStmt: A block of statements enclosed in braces.
        Expr: All expressions are a subclass of Stmt.
            DeclRefExpr: Reference to a declared entity.
            CallExpr: A function call.
            BinaryOperator/UnaryOperator: Binary/unary operations (e.g., +, -, *, /, ++).
            ImplicitCastExpr/CXXFunctionalCastExpr: Various types of casts.
            MemberExpr: Accessing a member of a class/struct.
            ArraySubscriptExpr: Array indexing.
            IntegerLiteral/FloatingLiteral/StringLiteral: Literal values.
            CXXConstructExpr: Constructor calls. 
        IfStmt, ForStmt, WhileStmt, DoStmt, SwitchStmt: Control flow statements.
        ReturnStmt: A return statement.
        BreakStmt, ContinueStmt: Loop control statements. 
    Types (Type): Describe the nature of data.
        BuiltinType: Fundamental types like int, char, float.
        PointerType/ReferenceType: Pointers and references.
        FunctionType: Represents function signatures.
        RecordType: The type corresponding to a RecordDecl.
        ElaboratedType: A type with a keyword (e.g., struct S).
        TypedefType: The type corresponding to a TypedefDecl.
        TemplateTypeParmType: Template type parameters.
        ObjCObjectType/ObjCInterfaceType: Objective-C object and interface types.

This is not an exhaustive list, as the Clang AST is extensive and includes many specialized nodes for various language features and extensions. The RecursiveASTVisitor class in Clang's tooling provides a structured way to traverse and interact with these different node types.

"""

OPERATORS = {

	'+':'add',
	'-':'subtract',
	'*':'multiply',
	'/':'divide',
	# // not in c
	'%':'modulo',
	# ** power not in c

	'<':'less_than',
	'>':'greater_than',
	
	'<<':'bitwise_left_shift',
	'>>':'bitwise_right_shift',
	'&':'bitwise_and',
	'|':'bitwise_or',
	'^':'bitwise_xor',
	'||':'and', # ?
	'!':'not', # ?
	'~':'bitwise_invert',
}

def DATATYPE(TYPE):

	if isinstance(TYPE, dict):
		if 'desugaredQualType' in TYPE:
			STRING = TYPE['desugaredQualType']
		else:
			STRING = TYPE['qualType']
	else:
		ENV.snap_warning('string input for DATATYPE', TYPE)
		
	# TODO rename * pointer to count?  like ** is ptr2?


	if STRING in ('int', 'long', 'long int', 'size_t'): return 'integer'
	elif STRING in ('double', 'long double'): return 'floating_point'
	# TODO string char*? or char[]?
	else:
		#print('unknown data type', repr(STRING))
		return STRING

# TODO map DATATYPES?

def build(ENV):

	SnapProgrammingLanguageDecoder = ENV.SnapProgrammingLanguageDecoder

	class SnapCLanguageDecoder(SnapProgrammingLanguageDecoder):

		__slots__ = []

		__VERSION_TABLE__ = {
			# TODO
			(0,0,0):[],
		}
		__VERSION_TABLE__ = {name:k for k,v in __VERSION_TABLE__.items() for name in v}


		__LANGUAGE_TABLE__ = {
			'c':['c','h'],
			'c++':['cpp', 'c++', 'c_plus_plus', 'cxx', 'hpp'],
		}
		__LANGUAGE_TABLE__ = {name:k for k,v in __LANGUAGE_TABLE__.items() for name in v}

		EXTENSIONS = [k for k in __LANGUAGE_TABLE__.keys()]

		@ENV.SnapProperty
		class language:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['language'] or 'c'

			def set(self, MSG):
				"(str!)"
				# basically just upgrade to cpp if cpp language feature is used...
				language = MSG.args[0]
				if language in ('cpp','c++','c_plus_plus'):
					self.__snap_data__['language'] = 'c_plus_plus'


######## ROOT NODES:
		def convert_TranslationUnitDecl(self, N):
			N['__type__'] = 'module'
			N['body'] # -> everything....
			return N

######## TYPES:
		def convert_AutoType(self, N):
			return N # TODO

		def convert_BuiltinType(self, N):
			# TODO just convert to python type: int, float, ... deal with other keywords later?  TODO support unsigned?
			return N

		def convert_ConstantArrayType(self, N):
			return N # TODO

		def convert_FunctionType(self, N):
			# https://clang.llvm.org/doxygen/classclang_1_1FunctionType.html#details
			"the common base class of FunctionNoProtoType and FunctionProtoType"
			#  ExtQualsTypeCommonBase -> Type -> this
			# TODO predeclaration
			raise NotImplementedError() # unused?

		def convert_QualType(self, N):
			# TODO
			return N

		def convert_PointerType(self, N):
			return N # TODO

		def convert_RecordType(self, N):
			# TODO
			return N

		def convert_TypedefType(self, N):
			raise NotImplementedError() # doesn't seem to be used...  see TypedefDecl
			return N

######## DECLARATIONS:
		def convert_AccessSpecDecl(self, N):
			# https://clang.llvm.org/doxygen/classclang_1_1AccessSpecDecl.html#details
			# Decl -> this
			"an access specifier followed by colon ':'"
			raise NotImplementedError()

		def convert_EnumDecl(self, N):
			return N # TODO

		def convert_FriendDecl(self, N):
			self['language'] = 'c++'
			return N # TODO this is just access permisson stuff, we can setup the class definitions to forbid certain accesses...

		def convert_FunctionDecl(self, N):
			#ENV.snap_out([(k,v) for k,v in N.items() if k != 'body'], 'body' in N)

			if 'previousDecl' in N:
				p_id = int(N.pop('previousDecl'), 16)
				#ENV.snap_warning('function', repr(N['name']), 'redeclared!', p_id)
				# TODO search the function with same id (and name, why not) and add own elements to it (don't check it, assume the c parser already did that...)

			N['__type__'] = 'function_definition'
			N['name']
			N['decorators'] = [] # N/A in C
			if 'mangledName' in N:
				del N['mangledName']
			if 'isUsed' in N:
				del N['isUsed'] # we don't care, we'll just define it anyway
			N['data_type'] = DATATYPE(N.pop('type')) # NOTE: this is considered to be the return type of the function

			#if 'body' not in N or not N['body']:
			#	N['predeclaration'] = True # ? TODO or we could just resolve this here in the generalized ast...  find the first occurrence and then assign the full definition to it...  TODO pass a context in to this, and keep track of these things...

			N['arguments'] = []
			# I don't understand why the function arguments aren't considered part of the function declaration...?
			while 'body' in N and N['body'] and N['body'][0]['__type__'] == 'ParmVarDecl':
				arg = N['body'].pop(0)
				# TODO rename qualtype to valid names, * becomes ptr and & becomes ref? then just implement ptr and ref as types? ptr(var) or ref(var) or even ptr(ptr(var)) etc?  then the access of the pointer is implemented as a special function operation?
				# TODO create unique type for each pointer or reference so we can just do a simple type check?
				# TODO include line info?
				arg['__type__'] = 'argument'
				arg['data_type'] = DATATYPE(arg.pop('type'))
				if 'isUsed' in arg: del arg['isUsed']
				N['arguments'].append(arg)

			# NOTE: encoder can enforce strict typing by doing isinstance() check after unpacking message (in function header)
			# if argument has 'data_type' then compiler should do an instance check of that argument against that type...

			#ENV.snap_out({k:v for k,v in N.items() if k != 'body'})
			return N

		def convert_FunctionNoProtoType(self, N):
			"clang: warning: a function declaration without a prototype is deprecated"
			"in all versions of C and is treated as a zero-parameter prototype in C23"
			# like: int func(); -> use int func(void); for proper declaration
			# also: this does not appear in JSONNodeDumper.cpp
			raise NameError('deprecated; functions must be declared with (void) if empty')

		def convert_FunctionProtoType(self, N):
			# https://github.com/llvm/llvm-project/blob/main/clang/lib/AST/JSONNodeDumper.cpp#L622
			# TODO forward declaration of a function...  compiler needs to pre-process and handle this...
			# TODO actually this appears to not do anything, only FunctionDecl gets called...
			# TODO does this have to be in a header file?
			ENV.snap_warning(N, N.keys())
			return N # TODO

		def convert_ParmVarDecl(self, N):
			return N # handled by FunctionDecl

		def convert_RecordDecl(self, N):
			return N # TODO
		
		def convert_TypeAliasDecl(self, N):
			# google AI: represents the declaration of a type alias using the C++11 using syntax. This is distinct from clang::TypedefDecl, which represents a typedef declaration from C.
			# version = c++11
			# TODO
			return N

		def convert_TypedefDecl(self, N):
			# google AI: TypedefType represents a type that has been introduced using the typedef keyword in C or C++
			# TODO ENV['type_b'] = ENV['type_a'] or 'assign' type with names?
			if 'isReferenced' in N:
				'' # TODO
			return N

		def convert_UsingDecl(self, N):
			# TODO this localizes an element from ENV into a new local ENV assigned to the using name...
			return N

		def convert_VarDecl(self, N):
			# TODO this is all that is needed, make an assign for each one at the top-level of the expression?
			#N['__type__'] = 'variable_declaration' # TODO assign?
			if 'body' not in N:
				''
				# TODO do we need to preserve the idea of variables that haven't been 'initialized'?  otherwise this is just assigning a new instance of the type to the ENV[name]
			else:
				'new initialized type?' # body should be a single value of the type...  this is an assign?
			return N

######## LITERALS:
		def convert_CharacterLiteral(self, N):
			N['__type__'] = 'constant'
			#ENV.snap_out(TYPE, N.keys(), N['value'], N['type'])
			N['value']
			N['data_type'] = 'integer' # char?
			N.pop('type')
			del N['valueCategory']
			return N

		def convert_FixedPointLiteral(self, N):
			raise NotImplementedError("TODO: fixed point literal isn't standard, but we could support it...")
			return N

		def convert_FloatingLiteral(self, N):
			N['__type__'] = 'constant'
			N['data_type'] = 'floating_point'
			del N['type']
			del N['valueCategory']
			N['value'] = float(N.pop('value'))
			return N

		def convert_IntegerLiteral(self, N):
			N['__type__'] = 'constant'
			N['value'] = int(N['value'])
			N['data_type'] = 'integer' # always
			del N['type']
			del N['valueCategory']
			return N

		def convert_StringLiteral(self, N):
			N['__type__'] = 'constant'
			del N['valueCategory'] # TODO assert is 'prvalue'?
			N['data_type'] = 'string' # always
			del N['type']
			N['value'] = N['value'].strip('"\'')
			return N

######## EXPRESSIONS:
		def convert_AddrLabelExpr(self, N):
			# https://clang.llvm.org/doxygen/classclang_1_1AddrLabelExpr.html
			# Stmt -> ValueStmt -> Expr -> this
			"The GNU address of label extension, representing &&label"
			raise NotImplementedError()

		def convert_AtomicExpr(self, N):
			N['__type__'] = 'atomic_expression'
			# arguments: the pointer to the variable, the value to add, and the memory order
			"""
			__atomic_exchange
			__atomic_fetch_* (e.g., __atomic_fetch_add, __atomic_fetch_sub)
			__atomic_load
			__atomic_store
			__atomic_compare_exchange_* (e.g., __atomic_compare_exchange_n)
			"""
			# TODO we'll just compile some backend for atomic behaviour and then the user can just access it via the ENV...
			# maybe also in combination with defining a type for the atomic int or whatever?  need to research how this stuff works...
			# TODO define an atomic type?  or backend library to use for atomic operations?
			return N

		def convert_CallExpr(self, N):
			# TODO
			return N

		def convert_CastExpr(self, N):
			# TODO
			return N

		def convert_ImplicitCastExpr(self, N):
			#N['__type__'] = 'TODO' # TODO this needs to be call?  to the cast typename...
			N['data_type'] = DATATYPE(N.pop('type'))
			N['body']
			value_category = N.pop('valueCategory') # prvalue TODO
			castKind = N.pop('castKind')
			if 'isPartOfExplicitCast' in N:
				'' # TODO

			# TODO keep the types as they are, this just puts a(b()) together
			return N

		def convert_InitListExpr(self, N):
			# we could make this 'list' type, BUT c kinda treats arrays differently...
			# TODO if it is a list of char then return as string?
			# TODO for {'a','b','c','\0'}; strings, each element is a char(int('x')) passed into array()?  or just use list()?

			# TODO make it a thing that if list is all the same type, then create a new element of that type with a bytearray of the entries?  so all types can implicitly extend?  if it's a base type?  otherwise we would use SnapObject type to store anything arbitrarily (and the base type itself would be that type)  -- so we would assign as a list of SnapObject(char(int(c))) ints, but they would internally be converted into a single array of char type?
			#	-- TODO except that integer types could be various byte sizes...  so only char can do this?
			return N

######## OPERATORS:

		def convert_BinaryOperator(self, N):
			op = N.pop('opcode')
			if op == '=':
				N['__type__'] = 'binary_operation'
				# TODO c thinks of assignment differently, it is only between 2 operands, and has a return!
				# TODO should we just implement this using the binary operator?  if left is _attr() then the assign will be to the variable...  otherwise result goes onto the stack for evaluation...?
				#print('assign', N.keys())
			else:
				N['__type__'] = 'binary_operation'
				try:
					N['operator'] = OPERATORS[op]
				except:
					raise ValueError('unknown binary operator', op)

			del N['valueCategory']
			del N['type'] # return type will be handled in the compiler implementation

			values = N.pop('body')
			assert len(values) == 2, '{}: incorrect format?'.format(N['__type__'])
			N['left'],N['right'] = values
			return N

		def convert_CompoundAssignOperator(self, N):
			return N # TODO

		def convert_UnaryOperator(self, N):
			# https://clang.llvm.org/doxygen/classclang_1_1UnaryOperator.html
			# Stmt -> ValueStmt -> Expr -> this
			# TODO 'x++' = 'x += 1' but we have to handle evaluation before '++x' or after 'x++'
			# TODO parent node needs to find it...
			N['__type__'] = 'unary_operation'
			assert len(N['body']) == 1, 'expected single body element for {}'.format(N['__type__'])
			N['operand'] = N.pop('body')[0]
			N['operator'] = {'-':'unary_subtract', '+':'unary_add', '*':'???', '~':'bitwise_invert', '!':'not'}[N.pop('opcode')] # TODO '*'?
			N['data_type'] = DATATYPE(N.pop('type'))
			N.pop('valueCategory')
			if 'isPostfix' in N: # TODO isPrefix can occur? like --x
				del N['isPostfix'] # TODO ++x or x++ # TODO make a wrapping function to do incr_before, incr_after?
			if 'canOverflow' in N:
				del N['canOverflow']
			return N

######## STATEMENTS:
		def convert_DeclStmt(self, N):
			# TODO this is just N['__type__'] = 'expression', N['value'] = N.pop('body')
			#ENV.snap_out(N.keys())
			# TODO this is statement?
			return N

		def convert_DefaultStmt(self, N):
			# TODO default: in switch stmt? TODO handle in switch statement?
			return N

		def convert_CaseStmt(self, N):
			# TODO if?  or special implementation?  compiler could do it...  jumping to the answer?
			return N

		def convert_CompoundStmt(self, N):
			# a series of Stmt between '{' and '}'
			# TODO make this 'expression_group' as a new concept?  has it's own namespace?
			if 'body' in N:
				N['__type__'] = 'expression' # TODO?  return value?  this seems to be the code between '{' and '}'
				#ENV.snap_out(N['__type__'], [n['__type__'] for n in N['body']])
				N['value'] = N.pop('body') # TODO or make it just whatever the child is?
				# TODO turn all DeclStmt -> VarDecl into assign of the type?
				# TODO assign can have multiple targets, wrapped in tuple...  just do that, either from a constant or a new type?
			else:
				N['__type__'] = 'pass'
				for x in list(N.keys()):
					if x in ('__type__', '__line_info__'): continue
					ENV.snap_warning('del', N['__type__'], x)
					del N[x]
			# TODO does this apply to any '{}' namespace?  or just functions?
			return N

		def convert_GotoStmt(self, N):
			# https://en.cppreference.com/w/cpp/language/goto.html
			"The goto statement must be in the same function as the label it is referring,"
			"it may appear before or after the label"
			N['__type__'] = 'jump' # TODO implement this concept in compiler
			N['id'] = int(N.pop('targetLabelDeclId'), 16)
			return N

		def convert_IfStmt(self, N):
			N['__type__'] = 'if'
			N['body']
			N['test'] = N['body'].pop(0)
			if len(N['body']) > 1:
				N.pop('hasElse')
				assert len(N['body']) == 2, 'incorrect if format?'
				N['else'] = N['body'].pop(-1)
			else:
				N['else'] = None
			
			assert len(N['body']) == 1, '{}: bad format'.format(N['__type__'])

			return N

		def convert_LabelStmt(self, N):
			# https://clang.llvm.org/doxygen/classclang_1_1LabelStmt.html
			# Stmt -> ValueStmt -> this
			N['__type__'] = 'jump_destination'
			N['name']
			N['id'] = int(N.pop('declId'), 16)
			N['body']
			return N

		def convert_ReturnStmt(self, N):
			N['__type__'] = 'return'
			body = N.pop('body')
			N['value'] = body[0] if body else None
			return N

		def convert_WhileStmt(self, N):
			N['__type__'] = 'while'
			N['test'] = N['body'].pop(0)
			N['body']
			N['else'] = None # unsupported in c
			return N

######## ATTRIBUTES:
		def convert_ConstAttr(self, N):
			# TODO this is _attr(ENV, "name") ?  or "name" in python...
			return N




		def decode_ast_node(self, AST_NODE):

			if not (isinstance(AST_NODE, dict) and 'kind' in AST_NODE):
				print('warning: raw value?', AST_NODE)
				return AST_NODE

			N = {}
			TYPE = N['__type__'] = AST_NODE['kind']

			for attr,value in AST_NODE.items():
				if attr == 'kind': continue
				elif attr in ('loc','range'): continue

				elif attr == 'id':
					N['__id__'] = int(value, 16)

				elif attr == 'inner':
					N['body'] = [self.decode_ast_node(e) for e in value]
				else:
					assert attr not in ('body', '__id__', '__type__'), 'name collision: {}'.format((TYPE, repr(attr)))
					N[attr] = value

				# https://en.cppreference.com/w/cpp/language/value_category.html

			
			self['version'] = N
			self['language'] = self.__LANGUAGE_TABLE__.get(TYPE, 'c')

			with_span_info = self['with_span_info']
			if with_span_info:

				
				rnge = AST_NODE.get('range')
				if rnge and rnge['begin'] and rnge['end']:

					# the structure is rather arbitrary, so we'll just walk and find the min/max offset
					def search(NAME, compare):
						x = None
						QUEUE = [rnge[NAME]]
						while QUEUE:
							check = QUEUE.pop(0)
							for k,v in check.items():
								if k == 'offset':
									if x is None or compare(x, v):
										x = v
										continue
								if isinstance(v, dict):
									QUEUE.append(v)
						return x

					start = search('begin', lambda a,b: a > b)
					end = search('end', lambda a,b: a < b)


					assert isinstance(start, int) and isinstance(end, int), '{}: invalid start({}) or end({})'.format(AST_NODE['kind'], start, end)
					N['__line_info__'] = {'span':[start, end+1]}

			if 'range' not in AST_NODE:
				'ignore?' # TODO includes don't have line info...  we can ignore them, we just want the local stuff...  this also means that sub calls to self.decode_ast_node() need to watchout for a None return...


			self['version'] = N
			self['language'] = self.__LANGUAGE_TABLE__.get(TYPE, 'c')

			if with_span_info and self['preserve_spacing'] and 'body' in N:
				''#N = add_spacing(N, SETTINGS['__source_text__'])

			if self['generalized']:

				ORIGINAL = N.copy()

				converter = getattr(self, 'convert_' + TYPE, None)
				if not converter:
					ENV.snap_warning('no converter for', repr(TYPE))
					#raise NotImplementedError('convert_' + TYPE)
				else:
					N = converter(N)

				#N['__original__'] = ORIGINAL

			return N
		
		def parse(self, TEXT, extension='c'):
			INPUT_TEXT = TEXT.encode() # to bytes

			try:
				self.__LANGUAGE_TABLE__[extension]
			except KeyError:
				raise TypeError('extension must be for c or c++, not:', repr(extension))
			# TODO we'll have to pass in includes... get from local property?
			p = subprocess.Popen(['clang', '-Xclang', '-ast-dump=json', '-fsyntax-only', '-x'+extension, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
			out,err = p.communicate(input=INPUT_TEXT)
			if err:
				raise Exception('parse error', repr(err))
			return json.loads(out.decode('utf8'))

	ENV.SnapCLanguageDecoder = SnapCLanguageDecoder


def main(ENV):

	ENV.__build__('snap.lib.programming.language.SnapProgrammingLanguageDecoder')
	build(ENV)

	EXAMPLE = """
	// main.c
	//#include <stdlib.h>

	int main(void) {
		char greetings[] = {'H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', '!', 65};
	}
	"""

	#EXAMPLE = 'fprintf("hello world");'

	#path = './example.c'
	#path = '/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/core/parsing/github.com py-pdf pypdf/Makefile'
	#with open(path, 'r') as openfile:
	#	j = decode(openfile.read())
	#c = ENV.SnapCLanguage()
	dec = ENV.SnapCLanguageDecoder()
	if 1:
		TESTS = os.path.join(THISDIR, 'test')
		TEST_NAME = 'VarDecl'
		with open(TESTS + os.sep + TEST_NAME + '.c', 'r') as openfile:
			EXAMPLE = openfile.read()

	j = dec.decode(EXAMPLE)

	#print('j', j)
	print(json.dumps(j, indent=4))

	#print(repr(EXAMPLE[124:132]))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

