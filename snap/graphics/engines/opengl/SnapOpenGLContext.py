
from OpenGL.GL import *

def build(ENV):

	SnapContext = ENV.SnapContext

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLContext(SnapContext):

		__slots__ = []

		# TODO BLENDMODES?

		@ENV.SnapProperty
		class image:

			def get(self, MSG):
				"()->SnapOpenGLImage"
				return self.__snap_data__['image']

			def set(self, MSG):
				"(SnapOpenGLImage!)"

				IMAGE = MSG.args[0]

				if not self.__snap_data__['__fbo__']:
					self.__snap_data__['__fbo__'] = glGenFramebuffers(1)
				if not self.__snap_data__['__rbo__']:
					self.__snap_data__['__rbo__'] = glGenRenderbuffers(1)

				self.__snap_data__['image'] = IMAGE

				glBindFramebuffer(GL_FRAMEBUFFER, self.__snap_data__['__fbo__'])
				glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, IMAGE['__engine_data__'], 0) # GLint = mipmap level
				#glBindRenderbuffer(GL_RENDERBUFFER, self._rbo_)
				#glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, *IMAGE.size())
				#glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self._rbo_) # depth and stencil buffers

				if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
					raise Exception('framebuffer error!')

				self.reset()

				self.changed(image=IMAGE)

		@ENV.SnapProperty
		class shader:

			def get(self, MSG):
				"()->int"
				return self.__snap_data__['__shader_id__']

			def set(self, MSG):
				"(int!)"
				INT = MSG.args[0]
				glUseProgram(INT)
				self.__snap_data__['__shader_id__'] = INT
				#self._set_matrix(self._ctm_)


# CMD ################################################################################################

		#def cmd_set_transform(self, MATRIX):
		#	raise NotImplementedError()

		def cmd_set_matrix(self, MATRIX):
			'' # TODO:
			#location = glGetUniformLocation(self.__snap_data__['__shader_id__'], 'OFFSET')
			#glUniformMatrix4fv(location, 1, GL_FALSE, MATRIX)

		"""

		def cmd_transform(self, MATRIX):
			# MATRIX is the change to apply to self._matrix_
			m = snap_matrix_t()
			snap_matrix_multiply(MATRIX['matrix'], self['matrix'], m) # TODO local?
			self['engine_context'].setWorldTransform(QTransform(m[0], m[4], m[1], m[5], m[3], m[7]))
		"""

		def cmd_apply_matrix(self):
			# because engine context matrix doesn't actually have to be set until we use it
			# this is always the first call of a shader...
			m = self['matrix']
			#TODO:
			#location = glGetUniformLocation(self.__snap_data__['__shader_id__'], 'OFFSET')
			#glUniformMatrix4fv(location, 1, GL_FALSE, m)


		#def cmd_clip(self, SHAPE):

		#def cmd_clip_extents(self, EXTENTS):


		# TODO other primitives?  arc?  triangle?  rect?


		#def cmd_draw_text(self, TEXT):

		#def cmd_fill_spline(self, PAINT, PATH):

		#cmd_fill_shape = cmd_fill_spline

		#def cmd_fill_mesh(self, PAINT, MESH):

		# cmd_fill_rect just use this:
		#def cmd_fill_extents(self, PAINT, EXTENTS):

		#def cmd_fill_circle(self, PAINT, x,y, radius):

		#def cmd_fill_ellipse(self, PAINT, x,y, w,h):


		#def cmd_stroke_spline(self, PAINT, PATH):

		#cmd_stroke_shape = cmd_stroke_spline

		#def cmd_stroke_mesh(self, PAINT, MESH):

		#def cmd_stroke_extents(self, PAINT, EXTENTS):

		#def cmd_stroke_circle(self, PAINT, x,y, radius):

		#def cmd_stroke_ellipse(self, PAINT, x,y, w,h):

		#def cmd_set_blendmode(self, MODE):




		#def cmd_set_line_width(self, UNITS):
			# 0.0->1.0?

		#def cmd_set_line_miter(self, MODE):

		#def cmd_set_line_miter_limit(self, LIMIT):

		#def cmd_set_line_join(self, MODE):

		#def cmd_set_line_cap(self, MODE):

		#def cmd_set_fill_rule(self, MODE) XXX make this engine specific only...


		def cmd_set_dash(self, POINTS):
			raise NotImplementedError()

		def cmd_restore(self, **SAVES):
			raise NotImplementedError()

		def cmd_save(self, *NAMES):
			raise NotImplementedError()

		def cmd_draw_text(self, *TEXT):
			raise NotImplementedError()

		def cmd_set_antialias(self, PERCENTAGE):
			raise NotImplementedError()

		def cmd_set_dash(self, DASH_INFO):
			raise NotImplementedError()

		def cmd_set_fill_rule(self, RULE):
			raise NotImplementedError()

		def cmd_set_source(self, SOURCE):
			raise NotImplementedError()

		def cmd_fill_extents(self, PAINT, EXTENTS):
			raise NotImplementedError()

		def cmd_set_blendmode(self, STRING):
			raise NotImplementedError()

		def cmd_check_interact(self, threshold=255, **EXTRAS):
			'' # TODO this can't be the method used in opengl...?
			raise NotImplementedError()

		@ENV.SnapChannel
		def activate(self, MSG):
			"()"
			# TODO
			fbo = self.__snap_data__['__fbo__']
			if fbo is not None:
				glBindFramebuffer(GL_FRAMEBUFFER, fbo)

		@ENV.SnapChannel
		def reset(self, MSG):
			"()"
			fbo = self.__snap_data__['__fbo__']
			if fbo is not None:
				glBindFramebuffer(GL_FRAMEBUFFER, self.__snap_data__['__fbo__'])

				#glClearDepth(1.0)
				glDepthFunc(GL_LEQUAL)#GL_LESS)
				glEnable(GL_DEPTH_TEST)
				glShadeModel(GL_SMOOTH)

				glPolygonMode(GL_FRONT, GL_FILL)
				#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # wireframe render
				glFrontFace(GL_CW) #GL_CW, GL_CCW
				#glCullFace(GL_BACK) # GL_FRONT, GL_FRONT_AND_BACK
				glCullFace(GL_FRONT)
				#glDisable(GL_CULL_FACE)
				glEnable(GL_CULL_FACE)

		@ENV.SnapChannel
		def finish(self, MSG):
			"()"
			# TODO
			#raise NotImplementedError()

		@ENV.SnapChannel
		def clear(self, MSG):
			"()"
			image = self['image']
			if image is not None:
				# TODO should there be a bind call in here?
				w,h = image['size']
				glViewport(0,0,w,h)
				glClearColor(0,0,0,0)
				glClearDepth(1.0)
				glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)

		# TODO set?

		def __init__(self, **SETTINGS):
			SnapContext.__init__(self, **SETTINGS)

		def __del__(self):
			fbo = self.__snap_data__['__fbo__']
			rbo = self.__snap_data__['__rbo__']
			if fbo:
				glDeleteFramebuffers(1, [fbo])
				del self.__snap_data__['__fbo__']
			if rbo:
				glDeleteRenderbuffers(1, [rbo])
				del self.__snap_data__['__rbo__']



	ENGINE.SnapOpenGLContext = SnapOpenGLContext
	return SnapOpenGLContext

