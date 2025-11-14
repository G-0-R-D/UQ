
import os, json
THISDIR = os.path.realpath(os.path.dirname(__file__))

def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapProjectSettings(SnapNode):

		__slots__ = []
	
		@ENV.SnapProperty
		class colors:

			def get(self, MSG):
				"()->dict"
				colors = self.__snap_data__['colors']
				if colors is None:
					with open(os.path.join(THISDIR, 'settings/colors.json'), 'r') as openfile:
						colors = self.__snap_data__['colors'] = json.loads(openfile.read())

					GFX = ENV.GRAPHICS
					QUEUE = [colors]
					while QUEUE:
						entry = QUEUE.pop(0)

						for k,v in entry.items():
							if isinstance(v, dict):
								QUEUE += [v]
							elif isinstance(v, list):
								entry[k] = GFX.Color(*v)
							else:
								ENV.snap_warning('unknown colors.json type', type(v))

				return colors


	ENV.SnapProjectSettings = SnapProjectSettings

