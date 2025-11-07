
import os, json
THISDIR = os.path.realpath(os.path.dirname(__file__))

# TODO display of text, syntax hightlighting, etc... for an open file in a project

def build(ENV):

	SnapProjectFileShader = ENV.SnapProjectFileShader

	GFX = ENV.GRAPHICS

	UNKNOWN = GFX.Color(.5,.5,.5,1.)
	HIGHLIGHTS = {
		# TODO default highlight colors
	}


	def highlight(STRING_TEXT, AST_NODE, rendered_line_height=None):

		if rendered_line_height is None:
			'' # TODO get from GFX.Text('xX')['text_extents']

		newline_count = 0

		QUEUE = [AST_NODE]
		while QUEUE:
			current = QUEUE.pop(0)

			'append body'

			# assign the highlight graphics to the ast nodes themselves...


	def get_highlight_color(self, AST_NODE):
		highlights = self.__snap_data__['highlights']
		if highlights is not None:
			color = highlights.get(AST_NODE['__type__'])
			if color is not None:
				return color
		color = HIGHLIGHTS.get(AST_NODE['__type__'])
		if color is not None:
			return color
		return UNKNOWN # TODO unknown draw with just a line, not a fill?

	class SnapProjectOpenFileShader(SnapProjectFileShader):

		__slots__ = []

		@ENV.SnapProperty
		class filepath: # XXX not the shaders job to open the file, just assign the text and highlights...

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['filepath']

			def set(self, MSG):
				"(str!)"
				filepath = MSG.args[0]
				if filepath is not None:
					assert isinstance(filepath, str) and os.path.exists(filepath), 'invalid filepath: {}'.format(repr(filepath))
					# TODO

		@ENV.SnapProperty
		class text:

			# NOTE: this doesn't have to be the text for the entire file, it could be just parts or a section (based on visibility)
			#	-- that will be handled by the parent context...

			def get(self, MSG):
				"()->SnapText"
				# TODO just return the text for rendering...  or make a blank one...

		@ENV.SnapProperty
		class highlights:

			# TODO this is [(NODE, [(color,span), ...]), ...] for each ast type (generated elsewhere, assigned to here)
			# TODO and then we can include backing blocks as a calculation here...

			def get(self, MSG):
				"()->dict"
				# TODO generate the highlights and then iter through them here?

			def set(self, MSG):
				"(dict!)"
				# TODO assign the ast node? # TODO assign ast elsewhere, this is highlight colors dict?  to override defaults

				# TODO with open(os.path.join(THISDIR, 'highlight_colors.json'), 'r') as openfile:
				#	highlights = json.loads(openfile.read())

				# TODO highlight = {'name':'identifier -- probably __type__', 'text':[('key', color, span), ...], 'blocks':[('key', color, span), ...]}
				#	-- then we could have keywords highlighted with 'keyword' color like try: except: and have outlining blocks but recognize them as being part of the same set...

		@ENV.SnapProperty
		class highlight_colors:

			'' # TODO assign locally for override

		def highlight_color_for_ast_node(self, NODE):
			# XXX generate the highlights elsewhere, in recursive call (just need a list of [(color, span), ...]) in the visible area...  sorted by span or just yield from top to bottom?
			'get from local assign to self.__snap_data__["highlights"][NODE["__type__"]]'
			'get from HIGHLIGHTS[NODE["__type__"]] global'
			return UNKNOWN

		def draw(self, CTX):
			'' # render the text and any syntax highlighting blocks...  (maybe make the syntax blocks assignable from the parent?  but as a dict of descriptions?)

		def lookup(self, CTX):
			'' # TODO device_event highlight color under mouse...

		@ENV.SnapChannel
		def update(self, MSG):
			"()"

			

			pass

		def __init__(self, **SETTINGS):
			SnapProjectFileShader.__init__(self, **SETTINGS)

			# TODO we can use binary search with the spans to find a random point in a file!  like visible lines...
			#	-- just add the extents info for each node?  or atleast the main ones, with a body or expression?

			# TODO keep the text as single document, when we want to do things like 'pull out a section' of text, we can just set the text invisible in the markup and duplicate it into a new text object for just that section...

			# figure out the span for each node by just taking the slice, assigning it to a QTextEdit and getting the metrics...

	return SnapProjectOpenFileShader

 # TODO this doesn't open the file, just accept string text and ast
