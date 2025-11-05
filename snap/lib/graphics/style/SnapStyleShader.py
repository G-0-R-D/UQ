
def build(ENV):

	SnapShaderProgram = ENV.SnapShaderProgram

	class UQStyleShader(SnapShaderProgram):

		__slots__ = []

		# TODO __getitem__ get base_color from ENV.STYLE
		def set(self, **X):
			raise NotImplementedError('use update(parent)')

		def __init__(self, *a, **k):
			SnapShaderProgram.__init__(self, *a, **k)

	ENV.UQStyleShader = UQStyleShader
