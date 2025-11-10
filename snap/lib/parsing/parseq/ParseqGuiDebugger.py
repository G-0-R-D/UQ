
def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	ParseqSequence = ENV.ParseqSequence
	ParseqRule = ENV.ParseqRule

	GFX = ENV.GRAPHICS

	def walk_grammar(RULE, mode='DFS'):

		seen = set()

		QUEUE = [[0, [], RULE]]
		while QUEUE:
			x = QUEUE.pop(0)

			yield x

			rule = x[-1]
			if not rule or id(rule) in seen:
				continue
			seen.add(id(rule))

			children = rule.items()
			if children:
				next_depth = x[0] + 1
				root = x[1]
				if mode == 'BFS':
					QUEUE = QUEUE + [(next_depth, root + [rule], child) for child in children]
				else: #if mode == 'DFS':
					QUEUE = [(next_depth, root + [rule], child) for child in children] + QUEUE

	class ParseqRuleGraphic(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class render_items:

			def get(self, MSG):
				""

		@ENV.SnapProperty
		class rule:

			def get(self, MSG):
				"()->ParseqRule"
				return self.__snap_data__['rule']

			def set(self, MSG):
				"(ParseqRule!)"
				rule = MSG.args[0]
				if rule is not None:
					assert isinstance(rule, ParseqRule), 'wrong type, not a rule: {}'.format(type(rule))
				# TODO assign graphics, TODO set extents

		@ENV.SnapProperty
		class subitems:

			def get(self, MSG):
				"()->ParseqRuleGraphic[]"
				rule = self['rule']
				if rule is not None:
					children = rule.items()
					if children:
						return [ParseqRuleGraphic(rule=c) for c in children]
				return []

			set = None

	ENV.ParseqRuleGraphic = ParseqRuleGraphic

	class ParseqGrammarGraphic(SnapContainer):

		__slots__ = ['__graphics__']

		@ENV.SnapProperty
		class rule:

			def set(self, MSG):
				"(ParseqRule)"
				rule = MSG.args[0]

				# TODO create a graphic for each rule, assign the position based on tree

				seen = set()

				graphics = [] # list of dicts with graphic info in them

				tab = 10
				y_offset = 0
				for depth,root,rule in walk_grammar(rule):
					'' # TODO make graphic
					print('graphics', depth, root, rule)

					indent = tab * depth

					text = GFX.Text(text=repr(rule), matrix=ENV.snap_matrix_t(1,0,0,indent, 0,1,0,y_offset, 0,0,1,0, 0,0,0,1))

					print('text height', text['height'])

					info = {
						'rule':rule,
						'block':{
							'extents':snap_extents_t(indent,y_offset,0, indent+text['width'],y_offset+text['height'],0), # TODO text metrics?
							'color':GFX.Color(.2, .7, .4, 1.) if id(rule) not in seen else GFX.Color(1.,.1,.1, 1.),
						},
						'text':text,
					}
					print('indent', indent, 'y_offset', y_offset)
					graphics.append(info)

					y_offset += text['height'] # size of graphics

					seen.add(id(rule))

				self.__graphics__ = graphics

		def draw(self, CTX):
			ctx_matrix = CTX['matrix']
			saved_matrix = ENV.snap_matrix_t(*CTX['matrix'])#ENV.snap_matrix_t(*ctx_matrix)
			for info in getattr(self, "__graphics__", []):
				if 'block' in info:
					block = info['block']
					CTX.cmd_fill_extents(block['color'], block['extents'])
				if 'text' in info:
					text = info['text']
					matrix = text['matrix']
					ENV.snap_matrix_multiply(saved_matrix, matrix, ctx_matrix)
					CTX['matrix'] = ctx_matrix
					CTX.cmd_draw_text(info['text'])

				CTX['matrix'] = saved_matrix


	ENV.ParseqGrammarGraphic = ParseqGrammarGraphic
					


	class ParseqGuiDebuggerHUD(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class decode_button:

			def get(self, MSG):
				"()->SnapButton"
				B = self.__snap_data__['decode_button']
				if B is None:
					B = self.__snap_data__['decode_button'] = SnapButton(text='decode')
				return B

		@ENV.SnapProperty
		class render_items:

			def get(self, MSG):
				"()->SnapContainer[]"
				return [self['decode_button']]


		@ENV.SnapChannel
		def window_event(self, MSG):
			"()"
			# TODO crop
				

	class ParseqGuiDebugger(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class text:

			def set(self, MSG):
				"(str!)"
				text = MSG.args[0]
				if text is not None:
					text = ParseqSequence(source=text)
				self['sequence'] = text

		@ENV.SnapProperty
		class sequence:

			def set(self, MSG):
				"(ParseqSequence!)"
				seq = MSG.args[0]
				if seq is not None:
					assert isinstance(seq, ParseqSequence)
				self.__snap_data__['sequence'] = seq
				# reset
				self.changed(sequence=seq)

		@ENV.SnapChannel
		def window_event(self, MSG):
			"()"
			ENV.snap_out('window event', MSG.args, MSG.kwargs)

		@ENV.SnapChannel
		def run(self, MSG):
			''
				

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

	ENV.ParseqGuiDebugger = ParseqGuiDebugger


def main(ENV):

	build(ENV)

	ENV.__run_gui__(ENV.ParseqGrammarGraphic, rule=ENV.ParseqANY())

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


