
def build(ENV):

	SnapTextMetrics = ENV.SnapTextMetrics

	Qt5 = ENV.extern.Qt5

	ENGINE = ENV.graphics.__current_graphics_build__

	snap_extents_t = ENV.snap_extents_t


	class SnapQt5TextMetrics(SnapTextMetrics):

		__slots__ = []


		def glyph_at_position(self, X, Y):

			# using binary search algorithm

			string = self.__parent__['text']
			qtext = self.__parent__['__engine_data__']

			# TODO start and end can be negative, meaning from the end...
			if start is None:
				start = 0
			elif start < 0:
				start = len(string) - abs(start)

			assert isinstance(start, int) and isinstance(end, int), 'start/end range must be int type if provided'

			cursor = qtext.textCursor()

			L = 0
			R = len(string)-1

			while R >= L:
				C = (L + R) // 2

				cursor.setPosition(C)
				rect = qtext.cursorRect(cursor)

				x,y,h = rect.x(),rect.y(),rect.height()

				# compare line/y first, once it succeeds, then proceed to comparing glyph/x
				if Y < y:
					R = C - 1
				elif Y > y + h:
					L = C + 1

				# then compare glyph/x, once Y is in line range...
				elif X < x:
					R = C - 1
				elif X > x:
					# now we need to verify we are within the glyph, not just the min
					# (or it will advance to the next position!)
					cursor.setPosition(C + 1)
					rect = qtext.cursorRect(cursor)
					if rect.y() > y:
						# make sure new rect is still on same line,
						# we don't want the next line, we want the rightmost
						# glyph/x in this one...
						return C
					if X < rect.x():
						# this is the glyph
						return C
					else:
						# glyph is still to the right (but in this line/y)
						L = C + 1
				else:
					R = C - 1
					continue # run to end / closest match

			return L # run to end / closest match

		def line_at_position(self, X, Y):

			glyph_idx = self.glyph_at_position(X,Y)

			qtext = self.__parent__['__engine_data__']

			cursor = qtext.textCursor()

			cursor.setPosition(glyph_idx)
			block = cursor.block()

			s = block.position()
			e = s + block.length()

			return s,e

		def subline_at_position(self, X, Y):
			line_span = self.line_at_position(X,Y)

			# TODO then we want to find each wrapped line, but from the cursor...

			raise NotImplementedError()

		def glyph_extents(self, INDEX):

			qtext = self.__parent__['__engine_data__']

			cursor = qtext.textCursor()
			cursor.setPosition(INDEX)
			#cursor.setPosition(INDEX+1, QTextCursor.KeepAnchor)

			first_rect = qtext.cursorRect(cursor)

			cursor.setPosition(INDEX+1)

			second_rect = qtext.cursorRect(cursor)

			return [first_rect.x(), first_rect.y(), 0, second_rect.x(), first_rect.y() + second_rect.height(), 0]


		def line_extents(self, START, END):

			qtext = self.text

			cursor = qtext.textCursor()

			cursor.setPosition(START)
			block = cursor.block()
			cursor.setPosition(block.position())
			rect = qtext.cursorRect(cursor)

			minpoint = [rect.x(), rect.y()]

			cursor.setPosition(END)
			block = cursor.block()
			cursor.setPosition(block.position() + block.length())
			rect = qtext.cursorRect(cursor)

			print('line ext', repr(self.string[START:END]), [minpoint[0], minpoint[1], 0, minpoint[0]+rect.x(), minpoint[1]+rect.height(), 0])
			return [minpoint[0], minpoint[1], 0, minpoint[0]+rect.x(), minpoint[1]+rect.height(), 0]


		def __init__(self, *a, **k):
			SnapTextMetrics.__init__(self, *a, **k)

	ENGINE.SnapQt5TextMetrics = SnapQt5TextMetrics




def main(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	GFX = ENV.GRAPHICS

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

		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"

			action,device,source = MSG.unpack('action', None, 'device', None, 'source', None)
			if isinstance(device, ENV.SnapDevicePointer):
				if action == 'press':
					local_position = MSG.kwargs['local_position']
					buttons = device.get('buttons')
					if source == buttons.get('left'):
						ENV.snap_out('left click')
						# set max extents corner of text (or set to min if below)
						#text = self['text']
						#ext = text['extents']
						x,y = local_position
						self['text']['extents'] = snap_extents_t(0,0,0, max(0, x), max(0, y),0)
					elif source == buttons.get('right'):
						ENV.snap_out('right click')
						# set wrap width (and draw line above)
						self['text']['word_wrap_width'] = local_position[0]
					elif source == buttons.get('middle'):
						ENV.snap_out('middle click')
						# clear extents and word wrap
						self['text']['word_wrap_width'] = self['text']['extents'] = None
			

		def draw(self, CTX):
			ext = self['text']['extents']
			if ext:
				CTX.cmd_stroke_extents(GFX.Color(0,0,0,1.), ext)
			return SnapContainer.draw(self, CTX) # text is rendered after


		def animated_outlines(self):

			#ENV.snap_out("called iter begin")

			GFX = ENV.GRAPHICS

			line_outline = GFX.Spline(stroke=GFX.Color(.5,.5,.5,1.))
			glyph_outline = GFX.Spline(stroke=GFX.Color(0., .8, .3, 1.))

			text = self['text']
			m = text['metrics']

			self['children'] = [text, line_outline, glyph_outline]


			def animate_newlines():

				#ENV.snap_out('loop')

				while 1:

					for start,end in m.newlines():
						#ext = m.text_extents(max(0, start-1),end)
						ext = m.text_extents(max(0, start-1),end)
						x1,y1 = ext[0],ext[1]
						x2,y2 = ext[3],ext[4]
						line_outline['description'] = ['S',x1,y1, x2,y1, x2,y2, x1,y2, 'C']
						yield

			def animate_glyphs():

				while 1:

					idx = 0
					while idx < len(text['text']):
						ENV.snap_out(idx, repr(text['text'][idx:idx+1]))
						ext = m.text_extents(idx, idx+1)
						x1,y1 = ext[0],ext[1]
						x2,y2 = ext[3],ext[4]
						glyph_outline['description'] = ['S',x1,y1, x2,y1, x2,y2, x1,y2, 'C']
						idx += 1
						yield

			animations = [animate_newlines(), animate_glyphs()]

			while 1:
				for anim in animations:
					next(anim)
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
					
left
			"""
			#text = "\t\thello\t\tthere"
			#text = 'abc'

			self['text'] = GFX.Text(text=text)#, extents=snap_extents_t(0,0,0, 100,480,0))

			#ENV.snap_out('text extents', self['text']['extents'][:])

			self['children'] = [self['text']]

			self['timer'] = ENV.SnapTimer(self.animated_outlines, seconds=.5)#, repeat=True)

			

	ENV.__run_gui__(Test)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv(graphics='QT5'))

