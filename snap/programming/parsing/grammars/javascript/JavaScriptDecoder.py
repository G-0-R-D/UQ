
def build(ENV):

	class JavaScriptDecoder(ParseqDecoder):
		def __init__(self):
			ParseqDecoder.__init__(self)

			# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Lexical_grammar

			hashbang = AND(POSITION(0), '#!', REPEAT(NOTANY('\n'), min=0, name='hashbang_value'),
				name='hashbang')

			single_line_comment = AND('//', REPEAT(NOTANY('\n'), min=0), # TODO OR('#', AND('/','/'))
				name='single_line_comment')
			multi_line_comment = AND('/*', REPEAT(NOT('*/'), min=0), OR(AND('*/'), ERROR),
				name='multi_line_comment')
			COMMENT = OR(single_line_comment, multi_line_comment,
				name='COMMENT', capture=False, suppress=True))

			single_line_string = OR(
				AND("'", REPEAT(OR("\\'", NOTANY("'", '\n')), min=0, capture=True), OR("'", ERROR)),
				AND('"', REPEAT(OR('\\"', NOTANY('"', '\n')), min=0, capture=True), OR('"', ERROR)),
				name='single_line_string')
