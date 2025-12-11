
from OpenGL import GL, GLUT
from OpenGL.GL import *

# https://khronos.org/registry/OpenGL-Refpages/gl4/
# http://pyopengl.sourceforge.net/documentation/manual-3.0/

__GL_IS_INIT__ = [False] # once for the entire runtime


def init(show=False):

	# initialize an opengl context for rendering to work

	GLUT.glutInit(1, [])#len(sys.argv), sys.argv) # TODO: move to app?

	GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH | GLUT.GLUT_ALPHA)


	if show:
		GLUT.glutInitWindowSize(640,480)
	else:
		GLUT.glutInitWindowSize(1,1)
	GLUT.glutInitWindowPosition(0,0)

	WINDOW_ID = GLUT.glutCreateWindow('')#bytestring('{}'.format(sys.argv[0])))

	GLUT.glutSetWindow(WINDOW_ID)

	if not show:
		GLUT.glutHideWindow()

	#print('OpenGL has been initialized!')


def build(ENV):

	SnapEngine = ENV.SnapEngine

	if ENV.extern.Qt5.HAS_OPENGL:
		# init opengl using qt window
		ENV.extern.Qt5.__SNAP_OPENGL_INIT__()
	elif not __GL_IS_INIT__[0]:
		# attempt to fallback to initializing opengl with glut
		init(show=False)
		__GL_IS_INIT__[0] = True

	class SnapOpenGLEngine(SnapEngine):

		__slots__ = []

		def do_lookup(self, *a, **k):
			# TODO look into Shader Storage Buffer Objects (SSBOs), apparently they can be written to?
			# another idea might be to pass in the uv/location and then we indicate based on visibility to the output render of that pixel?
			#	or create a new pixel buffer for each draw call...  but that's kinda brutal
			#	-- it might be the best option...  but we also need a framebuffer for each one, or to re-bind it...
			#	-- we could max-out the framebuffer with 1 pixel buffers...
			# but we need to be able to render a series of elements and THEN check pixel color...
			#	-- could we implement a shader program that checks the input pixel color, indicates somehow whether it's a hit, and then writes a blank pixel to clear it?  how to feedback?
			#	-- 2 output buffers, 1 width, x height for however many checks to support, we keep swapping them, and the other is used as input, we pass id (index) and only render the output to the chosen pixel, otherwise we render the previous one...

			return []

		def __init__(self, **SETTINGS):
			SnapEngine.__init__(self, **SETTINGS)

			ENV.graphics.__current_graphics_build__ = self

			# TODO fill in the types

			ENV.__build__('snap.graphics.engines.opengl.paint.SnapOpenGLColor')
			self.Color = self.SnapOpenGLColor

			ENV.__build__('snap.graphics.engines.opengl.paint.SnapOpenGLGradient')
			self.Gradient = self.SnapOpenGLGradient

			ENV.__build__('snap.graphics.engines.opengl.paint.SnapOpenGLTexture')
			self.Texture = self.SnapOpenGLTexture

			ENV.__build__('snap.graphics.engines.opengl.shape.SnapOpenGLSpline')
			self.Spline = self.SnapOpenGLSpline

			ENV.__build__('snap.graphics.engines.opengl.shape.SnapOpenGLMesh')
			self.Mesh = self.SnapOpenGLMesh

			ENV.__build__('snap.graphics.engines.opengl.shape.SnapOpenGLImage')
			self.Image = self.SnapOpenGLImage

			#ENV.__build__('snap.graphics.engines.opengl.shape.text.SnapOpenGLTextMetrics')
			#self.TextMetrics = self.SnapOpenGLTextMetrics

			ENV.__build__('snap.graphics.engines.opengl.shape.SnapOpenGLText')
			self.Text = self.SnapOpenGLText

			ENV.__build__('snap.graphics.engines.opengl.SnapOpenGLContext')
			self.Context = self.SnapOpenGLContext

			ENV.__build__('snap.graphics.engines.opengl.shader.SnapOpenGLShaderComponent')
			self.ShaderComponent = self.SnapOpenGLShaderComponent

			ENV.__build__('snap.graphics.engines.opengl.shader.SnapOpenGLShader')
			self.Shader = self.SnapOpenGLShader

			self.Matrix = ENV.SnapMatrix # TODO

			delattr(ENV.graphics, '__current_graphics_build__')

			# TODO default/engine shaders


	ENV.SnapOpenGLEngine = SnapOpenGLEngine
	return SnapOpenGLEngine
