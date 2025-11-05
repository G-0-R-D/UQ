
#from snap.lib.graphics.SnapEngine import *

"""
from snap.lib.graphics.engines.qt5.paint import (
	SnapQt5Color as SnapQt5ColorModule,
	SnapQt5Gradient as SnapQt5GradientModule,
	SnapQt5Texture as SnapQt5TextureModule,
	)

from snap.lib.graphics.engines.qt5.shape import (
	SnapQt5Image as SnapQt5ImageModule,
	SnapQt5Mesh as SnapQt5MeshModule,
	SnapQt5Path as SnapQt5PathModule,
	SnapQt5Text as SnapQt5TextModule,
	)

from snap.lib.graphics.engines.qt5.shader import (
	SnapQt5Shader as SnapQt5ShaderModule,
	# TODO other shaders
	)

from snap.lib.graphics.engines.qt5 import SnapQt5Context as SnapQt5ContextModule

from snap.lib.graphics import SnapProxy as SnapProxyModule

from snap.lib.graphics import SnapCamera as SnapCameraModule
from snap.lib.graphics import SnapContainer as SnapContainerModule
from snap.lib.graphics import SnapWindow as SnapWindowModule
"""

def build(ENV):

	Qt5 = ENV.extern.Qt5

	SnapEngine = ENV.SnapEngine

	class SnapQt5Engine(SnapEngine):

		#@ENV.SnapProperty
		#class name:
		#	def get(self, MSG):
		#		"""()->str"""
		#		return "QT5"

		@ENV.SnapProperty
		class axes:
			def get(self, MSG):
				"""()->int"""
				return 2

		def blit_gui_windowXXX(self, CTX, BLIT_TEXTURE):

			#SnapNode GUI_WINDOW = (SnapNode)snap_getattr_at(MSG, "window", 0);
			#SnapNode blit_texture = (SnapNode)snap_getattr_at(MSG, "blit_texture", 2);
			#cairo_t* cr = (cairo_t*)snap_getattr_at(MSG, "context", 4);

			#if (!cr){
			#	//snap_warning("no cairo context!");
			#	return (any)"ERROR";
			#}

			"""
			#SnapNode blit_texture = (SnapNode)snap_getattr_at(&GUI_WINDOW, "_blit_texture_", -1);
			engine_data = getattr(blit_texture, '_engine_data_', None)
			#cairo_pattern_t* engine_data = (cairo_pattern_t*)snap_getattr_at(&blit_texture, "_engine_data_", IDX_SnapEngineData__engine_data_);

			cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE)

			if engine_data:
				cairo_set_source(cr, engine_data)
			else:
				cairo_set_source_rgba(cr, 0,0,0,0)

			cairo_paint(cr)
			"""

			ENV.snap_warning("not implemented")

			return None

		def prep_gui_window(self, *args, **kwargs):
			pass # nothing for qt5 to do here

		def cleanup_gui_window(self, *args, **kwargs):
			pass # nothing for qt5 to do here

		



		def __init__(self, **SETTINGS):
			SnapEngine.__init__(self, **SETTINGS)

			ENV.graphics.__current_graphics_build__ = self

			ENV.__build__('snap.lib.graphics.engines.qt5.paint.SnapQt5Color')
			self.Color = self.SnapQt5Color

			ENV.__build__('snap.lib.graphics.engines.qt5.paint.SnapQt5Gradient')
			self.Gradient = self.SnapQt5Gradient

			ENV.__build__('snap.lib.graphics.engines.qt5.paint.SnapQt5Texture')
			self.Texture = self.SnapQt5Texture

			ENV.__build__('snap.lib.graphics.engines.qt5.shape.SnapQt5Spline')
			self.Spline = self.SnapQt5Spline

			ENV.__build__('snap.lib.graphics.engines.qt5.shape.SnapQt5Mesh')
			self.Mesh = self.SnapQt5Mesh

			ENV.__build__('snap.lib.graphics.engines.qt5.shape.SnapQt5Image')
			self.Image = self.SnapQt5Image

			ENV.__build__('snap.lib.graphics.engines.qt5.shape.text.SnapQt5TextMetrics')
			self.TextMetrics = self.SnapQt5TextMetrics

			ENV.__build__('snap.lib.graphics.engines.qt5.shape.SnapQt5Text')
			self.Text = self.SnapQt5Text

			ENV.__build__('snap.lib.graphics.engines.qt5.SnapQt5Context')
			self.Context = self.SnapQt5Context

			#ENV.__build__('snap.lib.graphics.engines.qt5.shader.SnapQt5Shader')
			#self.Shader = ENV.SnapQt5Shader

			ENV.__build__('snap.lib.graphics.engines.qt5.SnapQt5Window')
			self.Window = self.SnapQt5Window

			delattr(ENV.graphics, '__current_graphics_build__')

			# TODO CompositeShader, ParticleShader

			# TODO camera, container, even matrix and metrics?  put it all on the engine?

			self.PreferredShape = self.DefaultShape = self.Shape = self.Spline


			self['lookup_image'] = self.Image(width=1, height=1, format="RGBA", pixels=None)
			self['lookup_context'] = self.Context(image=self['lookup_image'])
			self.DEFAULT_FILL_COLOR = self.Color(0,0,0,1)
			self.DEFAULT_LINE_COLOR = self.Color(.5, .5, .5, 1)
			self.DEFAULT_PAINT_STYLE = "SOLID"

	# TODO if not ENV.__QT5_GFX__: ENV.__QT5_GFX__ = SnapQt5Engine() # XXX except this would be done on engine load...
	# -- make an engines module and put it there...
	# XXX or do something like ENV.__BUILDING_GFX__ = engine()?  and then assign back to None after engine is built...

	ENV.SnapQt5Engine = SnapQt5Engine
	return SnapQt5Engine

