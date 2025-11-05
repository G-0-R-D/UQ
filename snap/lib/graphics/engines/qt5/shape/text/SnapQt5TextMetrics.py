
def build(ENV):

	SnapTextMetrics = ENV.SnapTextMetrics

	Qt5 = ENV.extern.Qt5

	ENGINE = ENV.graphics.__current_graphics_build__

	snap_extents_t = ENV.snap_extents_t

	def text_extents_using_glyphruns(self, start=None, end=None):
		

		text = self.__parent__['text']
		qtext = self.__parent__['__engine_data__']

		#print(dir(qtext))

		#qtext.setFixedWidth(300)
		#qtext.adjustSize()
		#qtext.document().documentLayout()

		#widget = Qt5.QWidget()
		
		#window = Qt5.QWidget()
		#layout = Qt5.QVBoxLayout()

		#text_edit.setFixedWidth(200) # Set a fixed width to force wrapping
		#text_edit.append("This is a very long line of text that will definitely wrap multiple times within the fixed width widget.")
		#text_edit.append("Here is another paragraph.")

		#layout.addWidget(qtext)
		#window.setLayout(layout)
		#window.show()
		#layout.removeWidget(qtext)

		#print('begin', dir(qtext))
		#qtext.adjustSize()
		#return snap_extents_t(0,0,0,0,0,0)

		# TODO do word wrap by just getting metrics of unwrapped text and then generating another text with newlines assigned?

		# TODO start and end can be negative, meaning from the end...
		if start is None:
			start = 0
		elif start < 0:
			start = len(text) + start

		assert isinstance(start, int) and isinstance(end, int), 'start/end range must be int type if provided'

		# https://stackoverflow.com/questions/47038001/get-wrapped-lines-of-qtextedit

		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextBlock.html
		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextLine.html
		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QGlyphRun.html

		ext = snap_extents_t(0,0,0, 0,0,0)

		if start >= end:
			return ext

		ENV.snap_warning('start', start, 'end', end)

		xs = []
		ys = []

		y_offset = 0

		text_block = qtext.document().begin()
		while 1:
			if not text_block.isValid():
				break
			
			layout = text_block.layout()
			if not layout:
				text_block = text_block.next()
				continue

			block_start, block_end = text_block.position(), text_block.position() + text_block.length()-1 # ignore the next newline character
			block_text = text_block.text()#[line.textStart():line.textStart()+line.textLength()]

			#print('block text', repr(block_text))

			#if block_start > end:
			#	break

			#if start >= (block_start-1) and block_start < end:
			#	rect = layout.boundingRect()
			#	print(repr(block_text), rect.height())
				#return snap_extents_t(rect.x(), y_offset + rect.y(), 0, rect.x() + rect.width(), y_offset + rect.y() + rect.height(), 0)
			#	xs.append(rect.x())
			#	xs.append(rect.x() + rect.width())
			#	#ys.append(y_offset + rect.y())
			#	ys.append(y_offset + rect.y() + rect.height())

			#y_offset += layout.boundingRect().height()
			#print('y_offset', y_offset)

			if 1:

				num_lines = layout.lineCount()
				idx = 0
				while idx < num_lines:
					
					line = layout.lineAt(idx)
					line_text = text_block.text()[line.textStart():line.textStart()+line.textLength()]

					#print('line', idx, repr(line_text), layout.boundingRect(), line.naturalTextWidth(), line.height())

					line_start, line_end = block_start+line.textStart(), block_start+line.textStart()+line.textLength()

					if start > line_end:
						y_offset += line.height()

					elif line_start > end:
						break

					elif start >= (line_start-1) and line_start < end:
						#print('in range?', line_start, line_end, line_end-line_start, repr(line_text))

						local_start = max(0, start - line_start)
						local_end = end - line_start
						#print('local start', local_start, 'local end', local_end)
						runs = line.glyphRuns(local_start,local_end)
						if 0:#runs:
							for run in runs:
								rect = run.boundingRect()
								xs.append(rect.x())
								xs.append(rect.x() + rect.width())
								#ys.append(y_offset + rect.y())
								ys.append(y_offset + rect.y() + rect.height())
								#print('rect', rect, xs, ys)
						else:
							#rect = line.rect()
							rect = layout.boundingRect()
							xs.append(rect.x())
							xs.append(rect.x() + rect.width())
							ys.append(y_offset + rect.y() + rect.height())
							#print('rect', rect)

					idx += 1

			text_block = text_block.next()

		if not xs:
			xs = [0]
		if not ys:
			ys = [0]

		return snap_extents_t(min(xs), y_offset, 0, max(xs), max(ys), 0)




	class SnapQt5TextMetrics(SnapTextMetrics):

		__slots__ = []

		def text_extents(self, start=None, end=None):
			'' # TODO return lookup by line start for binary search, with text_block
			# XXX instead of cache just return what is needed for the requested range

			return text_extents_using_glyphruns(self, start, end)

			text = self.__parent__['text']
			qtext = self.__parent__['__engine_data__']

			# TODO start and end can be negative, meaning from the end...
			if start is None:
				start = 0
			elif start < 0:
				start = len(text) + start

			assert isinstance(start, int) and isinstance(end, int), 'start/end range must be int type if provided'

			# https://stackoverflow.com/questions/47038001/get-wrapped-lines-of-qtextedit

			# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextBlock.html
			# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextLine.html
			# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QGlyphRun.html

			ext = snap_extents_t(0,0,0, 0,0,0)

			if start >= end:
				return ext

			print('start', start, 'end', end)

			xs = []
			ys = []

			y_offset = 0

			ENV.snap_warning('begin')

			font_metrics = qtext.fontMetrics()
			#line_height = font_metrics.size(0, text).height() # TODO get this per line section...? line.height()!
			text_block = qtext.document().begin()
			total_line_idx = 0
			while 1:
				if not text_block.isValid():
					break

				s,e = text_block.position(),text_block.position()+text_block.length()-1 # ignore the next newline character
				layout = text_block.layout()
				if not layout:
					text_block = text_block.next()
					continue

				#ENV.snap_out('text block', s,e, repr(text[s:e]))#, layout.maximumWidth(), layout.minimumWidth(), layout.boundingRect(), dir(layout))

				num_lines = layout.lineCount()
				idx = 0
				while idx < num_lines:
					line = layout.lineAt(idx)
					line_start,line_end = s+line.textStart(), s+line.textStart()+line.textLength()
					line_text = text_block.text()[line.textStart():line.textStart()+line.textLength()]
					#print('\nline', idx, [line_start, line_end], repr(line_text), line.rect(), line.height())

					if start >= (line_start-1) and end <= line_end:
						# size is within the line, return glyph size
						local_start = start - line_start
						local_end = end - line_start
						#print('local start', local_start, 'local_end', local_end, line.textStart(), line.textLength())
						#xs = []
						#ys = []
						#print('select before', xs, ys)
						for run in line.glyphRuns(local_start, local_end):
							rect = run.boundingRect()
							print('bounding rect', y_offset, rect)#, dir(run))
							xs.append(rect.x())
							xs.append(rect.x() + rect.width())
							ys.append(y_offset + rect.y())
							ys.append(y_offset + rect.y() + rect.height())

						if not xs:
							xs = [0]
						if not ys:
							ys = [0]
						#assert len(glyphs) == 1, 'incorrect?'
						#rect = glyphs[0].boundingRect()
						#print('select', xs, ys)
						return snap_extents_t(min(xs), min(ys), 0, max(xs), max(ys), 0)
						
					elif start >= (line_start-1) and line_start < end:
						'include line metrics'
						rect = line.rect()
						#xs.append(rect.x())
						#xs.append(rect.x() + rect.width())
						#ys.append(y_offset + rect.y())
						#ys.append(y_offset + rect.y() + rect.height())
						#print('include', rect, xs, ys, repr(line_text))
						for run in line.glyphRuns(-1,-1):
							''#print(run.boundingRect())

					elif line_start >= end:
						break
						'collect line size in list, then find min/max after?'
						# break if line_start > end
						# if start >= (line_start-1) and line_start < end: include line, add to xs

					y_offset += line.height()
					#print('y_offset', y_offset)

					# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QGlyphRun.html
					#glyphs = line.glyphRuns(-1, -1) # local start and end
					#for run in glyphs:
					#	''#print('glyphs', run, run.boundingRect())

					#ENV.snap_out('line', font_metrics.size(0, line_text), line.height(), span, repr(line_text))
					idx += 1
					total_line_idx += 1
				#ENV.snap_out('text block', num_lines, text_block.text())#, text_block.size())
				text_block = text_block.next()

			if not xs:
				xs = [0]
			if not ys:
				ys = [0]

			return snap_extents_t(min(xs), min(ys), 0, max(xs), max(ys), 0)

		def __get_data__(self, START, END):
			'return the engine data ready to analyze internally'
			# newlines (textblock), sublines (lines), glyph sizes?

			# TODO just calculate the text size ourselves referring to markups?

			parent = self.__parent__
			if not parent:
				return None

			if parent['__needs_update__']:
				parent.update()
			qtext = parent['__engine_data__']
			if not qtext:
				return None

		def __init__(self, *a, **k):
			SnapTextMetrics.__init__(self, *a, **k)

	ENGINE.SnapQt5TextMetrics = SnapQt5TextMetrics




def main(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	class Test(SnapContainer):

		# TODO update extents to resize the graphic and metric display...

		# TODO use the metrics to make some words interactive like SPLAT?  and make an animated explosion graphic?

		#def draw(self, CTX):
		#	''
		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"()->SnapText"
				return self.__snap_data__['text']

			def set(self, MSG):
				"(SnapText|str)"
				text = MSG.args[0]
				if isinstance(text, str):
					text = ENV.GRAPHICS.Text(text=text)
				if text is not None:
					assert isinstance(text, ENV.GRAPHICS.Text), 'must be engine text type'
				self.__snap_data__['text'] = text
				self.changed(text=text)

		def timer_tester(self):
			while 1:
				yield

		def animated_outlines(self):

			#ENV.snap_out("called iter begin")

			GFX = ENV.GRAPHICS

			while 1:

				#ENV.snap_out('loop')

				text = self['text']
				if text is None:
					break

				m = text['metrics']

				for start,end in m.newlines():
					ext = m.text_extents(start,end)
					x1,y1 = ext[0],ext[1]
					x2,y2 = ext[3],ext[4]
					outline = GFX.Spline(description=['S',x1,y1, x2,y1, x2,y2, x1,y2, 'C'], stroke=GFX.Color(.5,.5,.5,1.))

					self['children'] = [text, outline]

					yield
				

		def __init__(self, *a, **k):
			SnapContainer.__init__(self, *a, **k)

			ENV.snap_out('begin extents', self['extents'][:])

			GFX = ENV.GRAPHICS

			text = """
		one day
		I looked up at the sky
		and...
				*SPLAT*!
			"""

			self['text'] = GFX.Text(text=text, extents=snap_extents_t(0,0,0, 800,480,0))

			ENV.snap_out('text extents', self['text']['extents'][:])

			self['children'] = [self['text']]

			self['timer'] = ENV.SnapTimer(self.animated_outlines, seconds=.5)#, repeat=True)

			

	ENV.__run_gui__(Test)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	#SnapEnv().__run__(__file__)
	#SnapEnv().__run__('snap.lib.graphics.engines.qt5.shape.text.SnapQt5TextMetrics')
	main(SnapEnv(graphics='QT5'))

