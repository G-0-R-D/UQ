
try:
	import bashlex
except ImportError:
	raise ImportError('install bashlex with "python -m pip install bashlex"')

#try:
#	from ast_grep_py import SgRoot
#except ImportError:
#	raise ImportError('install ast-grep with "python -m pip install ast-grep-py"')

# py -m pip install bashlex

# https://github.com/idank/bashlex

# https://stackoverflow.com/questions/52666511/create-an-ast-from-bash-in-c

# https://github.com/idank/bashlex/blob/master/examples/commandsubstitution-remover.py
# https://github.com/idank/bashlex/blob/master/bashlex/ast.py
#	-- take a look at _dump() function...  use that to do ast conversion

# https://github.com/ast-grep/ast-grep
# python -m pip install ast-grep-cli
# https://ast-grep.github.io/guide/api-usage/py-api.html

# bash grammar:
# https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_10_02

#root = SgRoot('ls', 'bash').root()

node = bashlex.ast.node

"""
with open('bash.sh', 'r') as openfile:
	parts = bashlex.parse(openfile.read())#'true && cat <(echo $(echo foo))')
	for ast in parts:
		print(ast)#.dump())


		# ast grammar from here:
		# https://github.com/idank/bashlex/blob/master/bashlex/parser.py
"""

def build(ENV):
	'' # TODO

