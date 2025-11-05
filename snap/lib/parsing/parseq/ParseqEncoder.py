

def build(ENV):

	#ENV.__import_and_build__('snap.lib.core.parsing.parseq.ParseqDecoder')

	#SnapObject = ENV.SnapObject

	class ParseqEncoder(object):

		# TODO make default behaviour to encode from rule tree?  or implement like walk, just re-define how to find subs?

		def __init__(self, *args, **kwargs):
			pass

	ENV.ParseqEncoder = ParseqEncoder
	return ParseqEncoder

