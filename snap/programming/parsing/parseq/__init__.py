
def build(ENV):

	ENV.__build__('snap.programming.parsing.parseq.ParseqDebugger')
	ENV.__build__('snap.programming.parsing.parseq.ParseqSequence')
	ENV.__build__('snap.programming.parsing.parseq.ParseqResult')
	ENV.__build__('snap.programming.parsing.parseq.ParseqRules')

	ENV.__build__('snap.programming.parsing.parseq.ParseqLayer')

	ENV.__build__('snap.programming.parsing.parseq.ParseqDecoder')	
	ENV.__build__('snap.programming.parsing.parseq.ParseqEncoder')

	ENV.__build__('snap.programming.parsing.parseq.ParseqGuiDebugger')

