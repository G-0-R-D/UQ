
def build(ENV):

	SnapEngineData = ENV.SnapEngineData

	class SnapShape(SnapEngineData):

		__slots__ = []

		@ENV.SnapChannel
		def update(self, MSG):
			"()"

			# if fill or stroke:

			# TODO update draw and lookup ins

			# TODO lookup could be fill/stroke/both # TODO default behaviour is to render both and then check, but using just black?  or make interaction threshold an option?

			# TODO also, lookup should add the parent, not this one?  we need to separate the idea of element and handler...

		@ENV.SnapChannel
		def changed(self, MSG):
			self.update()
			return SnapEngineData.changed(self, MSG)

		def __init__(self, **SETTINGS):
			SnapEngineData.__init__(self, **SETTINGS)

	ENV.SnapShape = SnapShape

def main(ENV):

	shape = ENV.SnapShape()

	shape['line'] = dict(dash='dash', thick=1.0, over=True)


if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

