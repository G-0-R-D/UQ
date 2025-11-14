
def highlight(TEXT, AST_NODE):

	TYPE = AST_NODE['__type__']

	if TYPE == 'module':
		'' # TODO we need just the spans, not the colors!  colors get from a dict of ['__type__']:GFX.Color()
		# this needs to be the node with all the highlights involved...  maybe give them sub-names?  keyword?

def highlights(TEXT, AST_NODE):
	''
