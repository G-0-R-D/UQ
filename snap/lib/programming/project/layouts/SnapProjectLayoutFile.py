
import os

def build(ENV):

	SnapContainer = ENV.SnapContainer

	snap_extents_t = ENV.snap_extents_t

	class SnapProjectLayoutFile(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class animating:

			def get(self, MSG):
				"()->bool"
				return bool(self.__snap_data__['animation_target'])
				

		@ENV.SnapProperty
		class is_module:

			def get(self, MSG):
				"()->bool"
				f = self.__snap_data__['__file_info__']
				if f:
					return 'module_info' in f
				return False

		@ENV.SnapProperty
		class background_color:

			def get(self, MSG):
				"()->SnapColor"
				c = self.__snap_data__['background_color']
				if not c:
					c = ENV.GRAPHICS.Color(0.5, 0.5, 0.5, 1.0)
				return c

		@ENV.SnapProperty
		class text_graphic:

			def get(self, MSG):
				"()->SnapText"
				return self.__snap_data__['text_graphic']

		@ENV.SnapProperty
		class title_graphic:

			def get(self, MSG):
				"()->SnapText"
				return self.__snap_data__['title_graphic']

		@ENV.SnapProperty
		class render_items:

			def get(self, MSG):
				"()->SnapNode[]"
				return [self['text_graphic'], self['title_graphic']]

		def next(self):

			target = self.__snap_data__['animation_target']
			if target is None:
				return

			'calculate next animation frame, and set accordingly'

		def animate(self, position=None, background_color=None, duration=None, **MSG):
			
			if MSG:
				ENV.snap_warning('extra animation options', MSG.keys())

			if duration is None:
				duration = 2 # seconds

			if position:
				''
				pos = self['position']
				ENV.snap_out('current position', pos, 'target', position)

			if background_color:
				''
			# TODO move this to actual animation system...
			# TODO calculate amount of change for one frame, save that for each channel?
			#self.__snap_data__['animation_target'] = MSG

		def draw(self, CTX):

			ext = self['extents']
			bg_color = self['background_color']
			CTX.cmd_fill_extents(bg_color, ext)

			return SnapContainer.draw(self, CTX)

			# TODO render highlight blocks

			text_graphic = self['text_graphic']
			if text_graphic:
				CTX.cmd_draw_text(text_graphic)

			title = self['title_graphic']
			if title:
				CTX.cmd_draw_text(title)

		def lookup(self, CTX):
			return SnapContainer.lookup(self, CTX)
			

		def __init__(self, FILE_INFO, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			self.__snap_data__['__file_info__'] = FILE_INFO

			w,h = 850,1100

			self['extents'] = snap_extents_t(0,0,0, w*.75,h*.75,0)

			with open(FILE_INFO['filepath'], 'r') as openfile:
				self.__snap_data__['text_graphic'] = ENV.GRAPHICS.Text(text=openfile.read().replace('\t', ' '*6), extents=self['extents'])

			title = self.__snap_data__['title_graphic'] = ENV.GRAPHICS.Text(text=os.path.basename(FILE_INFO['filepath']))
			title.translate(0,-27)
			title.scale(2,2,2)
			

	ENV.SnapProjectLayoutFile = SnapProjectLayoutFile
