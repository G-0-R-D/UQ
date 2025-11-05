
def build(ENV):


	SnapNode = ENV.SnapNode

	class SnapParsingModule(SnapNode):

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self, **SETTINGS)

			ENV.__build__('snap.lib.parsing.parseq') # doesn't include grammars
			ENV.__build__('snap.lib.parsing.parseq.grammars.ebnf') # TODO make this lazy load when accessed...  in parseq.grammars module...

			#ENV.__build__('snap.lib.parsing.language')

	ENV.parsing = SnapParsingModule()


	# XXX build into ENV space
	"""
	class ParsingModule(object):

		def __init__(self):
			''
	ENV.parsing = ParsingModule()
	"""

