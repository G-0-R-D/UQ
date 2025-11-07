
import os
from weakref import ref as weakref_ref

def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	snap_binary_search = ENV.snap_binary_search

	GFX = getattr(ENV, 'GRAPHICS', None) # TODO run headless

	def line_range(LINE_METRICS, START, END):
		start_idx = snap_binary_search(LINE_METRICS, START, key=lambda x: x[0], run_to_end=True)
		end_idx = snap_binary_search(LINE_METRICS, END, key=lambda x: x[0], run_to_end=True)
		return start_idx, end_idx

	def x_offset(LINE_DATA, START, TEXT_GRAPHIC):
		# LINE_DATA is entry from LINE_METRICS
		if LINE_DATA:
			''

		# TODO this is just TEXT_GRAPHIC['text'] = TEXT[LINE_DATA[0]:START]


	# XXX put these on AST_NODE class?  
	def calc_block(LINE_METRICS, START, END, mode):
		if mode is None:
			mode = 'full'

		first_line_idx, last_line_idx = line_range(LINE_METRICS, START, END)
		''

		# TODO now binary search the START in the LINE_METRICS for newline before, and then after for END (clamp start to found start)

	def calc_highlight():
		'use text markup' # TODO represent highlights with local nodes so we can remove them easily by just losing the reference?  and it edits the source...  assign this to the ast nodes themselves...

	def block_and_highlight_filter(PROJECT_FILE, NODE):
		''

	def walk_ast(ROOT, mode=None):
		# return ast nodes that are returned from filter

		if mode is None:
			mode = 'DFS'

		if mode == 'DFS':
			enqueue = lambda q, n: q + n
		elif mode == 'BFS':
			enqueue = lambda q, n: n + q
		else:
			raise AssertionError('invalid mode:', repr(mode))

		QUEUE = [ROOT]
		while QUEUE:
			node = QUEUE.pop(0)
			if not isinstance(node, dict):
				continue
			elif '__type__' in node:
				yield node
				
			for k,v in node.items():
				if k == '__original__': continue
				if isinstance(v, dict) and '__type__' in v:
					QUEUE = enqueue(QUEUE, [v])
				elif isinstance(v, list):
					QUEUE = enqueue(QUEUE, v)


	COLORS = {
	}
		

	class SnapProjectFile(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['text_graphic']['text']


		@ENV.SnapProperty
		class ast:

			def get(self, MSG):
				"()->dict"
				ast = self.__snap_data__['ast']
				if ast is not None:
					return ast

				ext = self['extension']
				lang = ENV.LANGUAGE.get_by_extension(ext)
				if ext is None or lang is None:
					return None

				# TODO get ast fresh, assign locally, emit changed

				# XXX TODO pass self to language.get_module_info(self.__snap_data__['__project__'](), self)

				self.changed(ast=ast)
				return ast

		@ENV.SnapProperty
		class filepath:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['filepath']

		@ENV.SnapProperty
		class extension:

			def get(self, MSG):
				"()->str"
				filepath = self['filepath']
				if filepath:
					split = os.path.basename(filepath).split('.')
					if len(split) > 1:
						return split[-1]
				return None

		@extension.alias
		class ext: pass


		@ENV.SnapProperty
		class line_metrics:

			def get(self, MSG):
				"()->list"

				existing = self.__snap_data__['line_metrics']
				if existing is not None:
					return existing

				text = self['text']
				measure_text = GFX.Text() # TODO

				newlines = self.__snap_data__['line_metrics'] = [] # [(start_index, y_offset, snap_extents_t(<line metrics>), ...]

				if not text:
					return newlines

				check = self.__snap_data__['check'] = []

				y_offset = 0 # store with each newline so we can navigate through a bit faster...

				idx = 0
				while 1:
					try:
						next_idx = text[idx:].index('\n')
						measure_text['text'] = text[idx:idx+next_idx]
						ext = measure_text['text_extents'][:]
						newlines.append((idx, y_offset, ext))
						ENV.snap_out('idx', idx, 'next_idx', next_idx, repr(text[idx:idx+next_idx]), ext)
						check.append([snap_extents_t(0,0,0, ext[3], ext[4],0), GFX.Text(text=text[idx:idx+next_idx])])
						idx = idx + next_idx + 1 # to ignore the newline
						y_offset += ext[4]
					except ValueError:
						break

				if idx < len(text):
					measure_text['text'] = text[idx:]
					newlines.append((idx, y_offset, measure_text['text_extents']))

				return newlines
				

		def draw(self, CTX):

			# TODO blocks and backing shapes...
			"""
			ast = self['ast']
			if ast is not None:
				for node in walk_ast(ast, mode='DFS'):
					if '__render__' not in node:
						continue

					block = node['__render__'].get('block')
					if not block:
						continue

					CTX.cmd_stroke_extents(GFX.Color(0,0,0,1), block)
			"""

			GFX = ENV.GRAPHICS
			bg_color = self.__snap_data__['background_color']
			if not bg_color:
				bg_color = GFX.Color(.75, .75, .75, 1.)
			CTX.cmd_fill_extents(bg_color, self['extents'])

			check = self.__snap_data__['check'] or []
			if 0:#check:
				ext,text = check[3]
				CTX.cmd_stroke_extents(GFX.Color(0,0,0,1), ext)
				CTX.cmd_draw_text(text)
				#ENV.snap_debug('text', text['text'])

			#for block in (self.__snap_data__['blocks'] or []):
			#	CTX.cmd_stroke_extents(GFX.Color(0,0,0,1), block)

			text = self.__snap_data__['text_graphic']
			if text is not None:
				CTX.cmd_draw_text(text)


		@ENV.SnapChannel
		def update(self, MSG):
			"()"
			return # XXX TODO project make a selection and assigns to module '__display__'?  and then calls update() on the display to set the graphics?

			self.clear()

			ast = self['ast']
			if ast is None:
				return

			lm = self['line_metrics'] or []

			measure_text = GFX.Text() # TODO

			# TODO just keep a set() of all the lines, and then only use the lines that involve ast nodes... and then we have to re-position the ast nodes to their actual line...  so keep track of y_offset here...

			# TODO we need a filter callback to decide if ast nodes are to be included...  or maybe a list?  then just check each node if it is in the list?  if existing then animate to new position?  set the highlights once it has arrived?  do fade in with secondary graphic and then erase it and use original with full highlights?

			# default view just includes all lines and data, once we make a selection we exclude all lines that aren't explicitly part of the node range...

			self.__snap_data__['blocks'] = [snap_extents_t(0,offset,0, ext[3], offset+ext[4],0) for span,offset,ext in lm]

			for node in []:#XXX walk_ast(ast, mode='DFS'):
				render_data = {}
				if '__line_info__' in node:
					if 'body' in node:
						'block'
						start,end = node['__line_info__']['span']
						ai,zi = line_range(lm, start, end)
						first_line, last_line = lm[ai], lm[zi]
						line_start = first_line[0]
						if start > line_start:
							'add x offset'
							''
						ENV.snap_out(node['__type__'], ai, zi, start,end, first_line, last_line)
						ext = first_line[-1]
						y_offset = first_line[1]
						x1,y1 = 0, y_offset# + ext[1]
						ext = last_line[-1]
						y_offset = last_line[1]
						for line in lm[ai:zi]:
							print(line)
						print('line max', max([e[3] for s,o,e in lm[ai:zi+1]]))
						x2,y2 = max([e[3] for s,o,e in lm[ai:zi+1]]), y_offset + ext[4]
						render_data['block'] = snap_extents_t(x1,y1,0, x2,y2,0)
					else:
						'highlight'

				if render_data:
					node['__render__'] = render_data
					break
				elif '__render__' in node:
					del node['__render__']


			# open and format text for spacing (we aren't putting the text back into the source language, and even if we wanted to we would use the ast!  so changing the text is fine)
			# get the line metrics for the text based on text graphic
			# parse into generalized ast (previous is now available with __original__)
			# add blocks to any ast with a body, assign to __render__ param?  something with a draw() and lookup()?  maybe a custom shader?  or a button...
			# also highlight the text when it's not got a body

			# TODO


		@ENV.SnapChannel
		def clear(self, MSG):
			"()"

			ast = self['ast']
			if ast is None:
				return

			for node in walk_ast(ast, mode='DFS'):
				if '__render__' in node:
					del node['__render__']

		@ENV.SnapChannel
		def open(self, MSG):
			"()"

			filepath = self['filepath']
			if filepath is None:
				return None

			# NOTE: filepath would be assigned by project and won't be editable (atleast not here!)
			assert os.path.isfile(filepath), 'not a file: {}'.format(repr(filepath))

			with open(filepath, 'r') as openfile:
				text = self.__snap_data__['text'] = openfile.read().replace('\t', ' '*6)

			GFX = getattr(ENV, 'GRAPHICS', None)

			text_graphic = self.__snap_data__['text_graphic'] = GFX.Text(text=text)

			ext = self['ext']
			#try:
			lang = ENV.LANGUAGE.get_by_extension(ext)
			ENV.snap_out('lang', lang, ext)
			if lang is not None:
				color = COLORS.get(lang)
				if color is None:
					if lang['name'] == 'python':
						color = COLORS[lang] = GFX.Color(.3, 1, .7, 1.)
					elif lang['name'] == 'c':
						color = COLORS[lang] = GFX.Color(.8, .6, .4, 1.)
					else:
						ENV.snap_debug('no color defined for', lang, lang['name'])
						color = COLORS[lang] = GFX.Color(0, .25, 1., 1.)
				self.__snap_data__['background_color'] = color
					
			#except KeyError:
			#	ENV.snap_debug('not a recognized language:', filepath, repr(ext))
			#	return
			#self.__snap_data__['ast'] = lang.decode(text)

			#self.update()

		@ENV.SnapChannel
		def changed(self, MSG):

			# TODO update render / shader?

			return SnapContainer.changed(self, MSG)


		def __init__(self, PROJECT, filepath=None, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			self.__snap_data__['__project__'] = weakref_ref(PROJECT) if PROJECT is not None else None

			self.__snap_data__['filepath'] = filepath

			if filepath:
				self.open()

			self['extents'] = snap_extents_t(0,0,0, 850,1100,0)

			# TODO text graphic -> text on it?  or change the text to remove indents?

			# TODO NOTE: since we have metrics for each line, we can re-assign the text graphic text to show just selections, and know where to put the graphics!
			#	TODO this means we want to store the original text...  then we can assign which ast nodes are visible...?

			# TODO use general and original ast and match by spans and tree positions (when possible)?

			# TODO AstNode class just acts as interface to manipulate the data?  data is stored on ast dict itself?  or maybe make a separate dict for all the data, wrap the nodes?
			#	-- store all data on generalized ast, and maybe ast parser should implicitly pass back the reference of the __original__ node?

			# TODO to display ast, create list of nodes that are visible, and add the graphics to them, then we can just iterate the list and draw each shape -- no extra class needed!


			

	ENV.SnapProjectFile = SnapProjectFile
	return SnapProjectFile

