
INSTRUCTIONS = """
lmb = set extents max corner
rmb = set line wrap x max
mmb = clear both
mouse position = highlights what is under mouse
"""

def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	GFX = ENV.GRAPHICS

	class TextMetrics(SnapContainer):


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
						self.text_graphic['extents'] = snap_extents_t(0,0,0, max(0, x), max(0, y),0)
					elif source == buttons.get('right'):
						ENV.snap_out('right click')
						# set wrap width (and draw line above)
						self.text_graphic['word_wrap_width'] = local_position[0]
					elif source == buttons.get('middle'):
						ENV.snap_out('middle click')
						# clear extents and word wrap
						self.text_graphic['word_wrap_width'] = self.text_graphic['extents'] = None

				elif action == 'motion':
					''#print('TODO: mouse move', MSG.kwargs)
					local_position = MSG.kwargs['local_position']
					#print('mouse move', local_position)
					index = self.text_graphic.glyph_at_position(*local_position)
					if index is not None and index < len(self.text_graphic['text']):
						self.current_hover_glyph = repr(self.text_graphic['text'][index])
						#ENV.snap_out('hover glyph', repr(self.current_hover_glyph))
						self.hover_glyph_ext = self.text_graphic.glyph_extents(index)
					else:
						#ENV.snap_warning('index', index, len(self.text_graphic['text']),self.text_graphic.glyph_extents(index)[:])
						self.current_hover_glyph = None
						self.hover_glyph_ext = self.text_graphic.glyph_extents(index)

		def animate(self):

			glyph_idx = 0
			newlines_idx = 0

			while 1:

				newlines = self.text_graphic.newlines()
				if not newlines_idx < len(newlines):
					newlines_idx = 0
				start,end = newlines[newlines_idx]
				ENV.snap_out('line', repr(self.text_graphic['text'][start:end]))
				self.animated_line_ext = self.text_graphic.text_extents(start,end)
				newlines_idx += 1

				string = self.text_graphic['text']
				if not glyph_idx < len(string):
					glyph_idx = 0
				self.animated_glyph_ext = self.text_graphic.glyph_extents(glyph_idx)
				self.current_animated_glyph = repr(string[glyph_idx])
				glyph_idx += 1

				yield


		def draw(self, CTX):

			CTX.cmd_draw_text(self.text_graphic)

			if self.text_graphic['extents'] is not None:
				CTX.cmd_stroke_extents(GFX.Color(0,0,0,1), self.text_graphic['extents'])

			if self.animated_glyph_ext:
				CTX.cmd_stroke_extents(GFX.Color(1,0,0,1), self.animated_glyph_ext)

			if self.animated_line_ext:
				CTX.cmd_stroke_extents(GFX.Color(0,0,1,1), self.animated_line_ext)

			if self.hover_glyph_ext:
				CTX.cmd_stroke_extents(GFX.Color(0,1,0,1), self.hover_glyph_ext)


			CTX.cmd_draw_text(self.instructions)


		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			text = """
hello world!
		how are you today?

that's great to hear!		
			"""
			self.text_graphic = GFX.Text(text=text)

			# TODO:FIXME: once SnapSubcontext() is functional...
			self.instructions = GFX.Text(text=('\n' * 13) + INSTRUCTIONS)

			self.current_hover_glyph = None
			self.hover_glyph_ext = None

			self.current_animated_glyph = None
			self.animated_glyph_ext = None

			self.animated_line_ext = None
			self.animated_subline_ext = None

			self.timer = ENV.SnapTimer(self.animate, seconds=.5)#, repeat=True)

	return TextMetrics


def main(ENV):

	ENV.__run_gui__(build(ENV))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv(graphics='QT5'))
