
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

	if not ENV.extern.Qt5.HAS_OPENGL and not __GL_IS_INIT__[0]:
		init(show=False)
		__GL_IS_INIT__[0] = True

	class SnapOpenGLEngine(SnapEngine):

		__slots__ = []

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

			delattr(ENV.graphics, '__current_graphics_build__')

			# TODO default/engine shaders


	ENV.SnapOpenGLEngine = SnapOpenGLEngine
	return SnapOpenGLEngine
