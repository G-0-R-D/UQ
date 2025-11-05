
def build(ENV):

	B = ENV.__build__
	
	B('snap.lib.parsing.parseq.grammars.ebnf.EBNFDecoder')
	B('snap.lib.parsing.parseq.grammars.ebnf.EBNFEncoder')

