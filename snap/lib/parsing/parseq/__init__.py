
def build(ENV):

	ENV.__build__('snap.lib.parsing.parseq.ParseqDebugger')
	ENV.__build__('snap.lib.parsing.parseq.ParseqSequence')
	ENV.__build__('snap.lib.parsing.parseq.ParseqResult')
	ENV.__build__('snap.lib.parsing.parseq.ParseqRules')

	ENV.__build__('snap.lib.parsing.parseq.ParseqLayer')

	ENV.__build__('snap.lib.parsing.parseq.ParseqDecoder')	
	ENV.__build__('snap.lib.parsing.parseq.ParseqEncoder')

	ENV.__build__('snap.lib.parsing.parseq.ParseqGuiDebugger')

