
# TODO make different syntax options optional, for how to represent certain things like repetitions

# goes from ParseqRule tree into ebnf formatted text

def build(ENV):

	snap_warning = ENV.snap_warning

	ParseqEncoder = ENV.ParseqEncoder
	ParseqRule = ENV.ParseqRule

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

	class SnapEBNFEncoder(ParseqEncoder):

		def encode(self, ROOT):

			assert isinstance(ROOT, ParseqRule), 'root must be parseq rule type'

			# TODO separate out multiple layers!

			for s in self.encode_to_strings(ROOT):
				yield s

		
		def encode_to_strings(self, RULE):

			RULE_TYPE = type(RULE)

			if RULE_TYPE == ITEM:
				''

			elif RULE_TYPE == AND:
				''

			elif RULE_TYPE == OR:
				''
			
		
		def __init__(self):
			ParseqEncoder.__init__(self)

			ENV.snap_warning("not implemented", __file__)

	ENV.SnapEBNFEncoder = SnapEBNFEncoder


