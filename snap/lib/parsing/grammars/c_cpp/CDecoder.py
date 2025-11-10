
import os

from snap.lib.parsing.parseq import *
from snap.lib.parsing.parseq.grammars.ebnf.EBNFDecoder import *

THISDIR = os.path.realpath(os.path.dirname(__file__))

# TODO use the yacc/lex decoder?  or is it worth it?

class CDecoder(ParseqDecoder):

	def __init__(self, *args, **kwargs):
		ParseqDecoder.__init__(self, *args, **kwargs)

		single_line_comment = AND('/','/', REPEAT(NOTANY('\n')),
			name='single_line_comment')
		multi_line_comment = AND('/*', REPEAT(NOT('*/'), min=0), OR(AND('*/'), self.ERROR),
			name='multi_line_comment')
		COMMENT = OR(multi_line_comment, single_line_comment,
			name='COMMENT', capture=False, suppress=True)


		DIGIT = RANGE('0', '9', name='DIGIT')
		LETTER = OR(RANGE('a','z'), RANGE('A','Z'), '_', name='LETTER')
		HEX_VALUE = OR(RANGE('a','f'), RANGE('A','F'), DIGIT, name='HEX_VALUE')

		ebnf = EBNFDecoder()
		if 1:
			single_input = ebnf.decode_file(
				os.path.join(THISDIR, 'c_ebnf_grammar'),
				#definitions = {k:ParseqLayerITEM(name=k) for k in (
				#	'STRING','NAME','NUMBER','NEWLINE','INDENT','DEDENT')} # no more BACKTICKS
				)

			out('ebnf out', single_input)

		sublayer = ebnf.sublayer()
		with open(os.path.join(THISDIR, 'c_ebnf_grammar'), 'r') as openfile:
			sequence = ParseqSequence(openfile.read())
		while 0:
			result = sublayer.search_with_result(sequence)
			if not result:
				break

			if result.name() == 'ERROR':
				snap_warning("error", result, result.line_info())
			else:
				if result.name() == 'declaration':
					out('okay', result.name(), repr(result.value()))#, result.line_info())

		if 0:
			declaration = sublayer.find_subrule('declaration')

			print(declaration.print_tree())

			while 1:
				result = declaration.search_with_result(sequence)
				if not result:
					break
				print(result, repr(result.value()))#, result.line_info())



if __name__ == '__main__':

	CDecoder()
