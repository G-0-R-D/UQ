
import os

def build(ENV):

	SnapContainer = ENV.SnapContainer

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
					c = ENV.GRAPHICS.Color(0.85, 0.85, 0.85, 1.0)
				return c

		@ENV.SnapProperty
		class text_graphic:

			def get(self, MSG):
				"()->SnapText"
				return self.__snap_data__['text_graphic']

		def next(self):

			target = self.__snap_data__['animation_target']
			if target is None:
				return

			'calculate next animation frame, and set accordingly'

		def animate(self, **MSG):
			"()"
			# TODO move this to actual animation system...
			# TODO calculate amount of change for one frame, save that for each channel?
			self.__snap_data__['animation_target'] = MSG

		def draw(self, CTX):

			# TODO filename title...

			ext = self['extents']
			bg_color = self['background_color']
			CTX.cmd_fill_extents(bg_color, ext)

			# TODO render highlight blocks

			text_graphic = self['text_graphic']
			if text_graphic:
				CTX.cmd_draw_text(text_graphic)

		def lookup(self, CTX):
			return SnapContainer.lookup(self, CTX)
			

		def __init__(self, FILE_INFO, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			self.__snap_data__['__file_info__'] = FILE_INFO

			self['extents'] = snap_extents_t(0,0,0, 850,1100,0)

			module_info = FILE_INFO.get('module_info')
			if module_info and 'language' in module_info:
				name = module_info['language']['name']
				# TODO background_color for language name
			

	ENV.SnapProjectLayoutFile = SnapProjectLayoutFile
