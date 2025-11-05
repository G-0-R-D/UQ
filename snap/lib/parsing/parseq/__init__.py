
#from snap.lib.parsing.parseq.ParseqDecoder import *
#from snap.lib.parsing.parseq.ParseqEncoder import *

#from snap.lib.core import SNAP_GLOBAL_ENV
"""

from snap.lib.parsing.parseq import (
	ParseqResult as ParseqResultModule,
	ParseqSequence as ParseqSequenceModule,
	ParseqDebugger as ParseqDebuggerModule,
	ParseqRules as ParseqRulesModule,
	ParseqLayer as ParseqLayerModule,
	ParseqDecoder as ParseqDecoderModule,
	ParseqEncoder as ParseqEncoderModule,
	)

def build(ENV):

	ParseqResultModule.build(ENV)
	ParseqSequenceModule.build(ENV)
	ParseqDebuggerModule.build(ENV)
	ParseqRulesModule.build(ENV)
	ParseqLayerModule.build(ENV)
	ParseqDecoderModule.build(ENV)
	ParseqEncoderModule.build(ENV)

	# then grammars are imported and added to ENV as needed...  (grammars are typically used directly for specific purposes)

build(SNAP_GLOBAL_ENV)
"""

#from snap.lib.core import SNAP_GLOBAL_ENV
#from snap.lib.parsing.parseq import ParseqEncoder as ParseqEncoderModule

def build(ENV):

	B = ENV.__build__

	B('snap.lib.parsing.parseq.ParseqDebugger')
	B('snap.lib.parsing.parseq.ParseqSequence')
	B('snap.lib.parsing.parseq.ParseqResult')
	B('snap.lib.parsing.parseq.ParseqRules')

	B('snap.lib.parsing.parseq.ParseqLayer')

	B('snap.lib.parsing.parseq.ParseqDecoder')	
	B('snap.lib.parsing.parseq.ParseqEncoder')
	#ParseqEncoderModule.build(ENV)

#build(SNAP_GLOBAL_ENV)
#print(dir(SNAP_GLOBAL_ENV))
