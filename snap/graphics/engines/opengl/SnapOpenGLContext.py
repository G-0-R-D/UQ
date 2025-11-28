
# TODO vertex and fragment shader for standard rendering operations, put it on the engine

def build(ENV):

	OpenGL = ENV.extern.OpenGL

	glGenFramebuffers = OpenGL.glGenFramebuffers
	glGenRenderbuffers = OpenGL.glGenRenderbuffers
	glBindFramebuffer = OpenGL.glBindFramebuffer
	glFramebufferTexture2D = OpenGL.glFramebufferTexture2D
	glCheckFramebufferStatus = OpenGL.glCheckFramebufferStatus
	glUseProgram = OpenGL.glUseProgram
	glClearDepth = OpenGL.glClearDepth
	glEnable = OpenGL.glEnable
	glShadeModel = OpenGL.glShadeModel
	glPolygonMode = OpenGL.glPolygonMode
	glFrontFace = OpenGL.glFrontFace
	glCullFace = OpenGL.glCullFace
	glViewport = OpenGL.glViewport
	glClearColor = OpenGL.glClearColor
	glClear = OpenGL.glClear
	glDepthFunc = OpenGL.glDepthFunc
	glDeleteFramebuffers = OpenGL.glDeleteFramebuffers
	glDeleteRenderbuffers = OpenGL.glDeleteRenderbuffers
	glFenceSync = OpenGL.glFenceSync
	glWaitSync = OpenGL.glWaitSync
	glDeleteSync = OpenGL.glDeleteSync
	glFlush = OpenGL.glFlush

	GLint = OpenGL.GLint

	GL_FRAMEBUFFER = OpenGL.GL_FRAMEBUFFER
	GL_COLOR_ATTACHMENT0 = OpenGL.GL_COLOR_ATTACHMENT0
	GL_TEXTURE_2D = OpenGL.GL_TEXTURE_2D
	GL_FRAMEBUFFER_COMPLETE = OpenGL.GL_FRAMEBUFFER_COMPLETE
	GL_LEQUAL = OpenGL.GL_LEQUAL
	GL_LESS = OpenGL.GL_LESS
	GL_SMOOTH = OpenGL.GL_SMOOTH
	GL_FRONT = OpenGL.GL_FRONT
	GL_FILL = OpenGL.GL_FILL
	GL_FRONT_AND_BACK = OpenGL.GL_FRONT_AND_BACK
	GL_LINE = OpenGL.GL_LINE
	GL_CW = OpenGL.GL_CW
	GL_CCW = OpenGL.GL_CCW
	GL_CULL_FACE = OpenGL.GL_CULL_FACE
	GL_COLOR_BUFFER_BIT = OpenGL.GL_COLOR_BUFFER_BIT
	GL_DEPTH_BUFFER_BIT = OpenGL.GL_DEPTH_BUFFER_BIT
	GL_STENCIL_BUFFER_BIT = OpenGL.GL_STENCIL_BUFFER_BIT
	GL_DEPTH_TEST = OpenGL.GL_DEPTH_TEST
	GL_SYNC_GPU_COMMANDS_COMPLETE = OpenGL.GL_SYNC_GPU_COMMANDS_COMPLETE
	GL_TIMEOUT_IGNORED = OpenGL.GL_TIMEOUT_IGNORED

	SnapContext = ENV.SnapContext
	SnapNode = ENV.SnapNode

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapOpenGLContextData(SnapNode):
		# frame and render buffers need to go somewhere persistent so they don't have to be destroyed and recreated
		# on every render, but context shouldn't really be re-usable either, context should be destroyed after each render
		# window shouldn't have a context, so that leaves image as a place to store this info
		# but the image itself shouldn't know about it, since this only applies to images that are rendered to...
		# so we'll put it in this container, and assign it to the image, and when the image is deleted this container will know
		# how to cleanup

		__slots__ = []

		@ENV.SnapChannel
		def image_changed(self, MSG):
			"()"
			# TODO just delete the framebuffer, it will be recreated by the context when needed

		def __del__(self):
			'' # TODO delete fbo and rbo

	class SnapOpenGLContext(SnapContext):

		__slots__ = []

		# TODO BLENDMODES?

		@ENV.SnapProperty
		class imageXXX:

			def get(self, MSG):
				"()->SnapOpenGLImage"
				return self.__snap_data__['image']

			def set(self, MSG):
				"(SnapOpenGLImage!)"

				ENV.snap_out('set image')

				IMAGE = MSG.args[0]

				if self.__snap_data__['__fbo__'] is None:
					self.__snap_data__['__fbo__'] = glGenFramebuffers(1)
				if self.__snap_data__['__rbo__'] is None:
					self.__snap_data__['__rbo__'] = glGenRenderbuffers(1)

				self.__snap_data__['image'] = IMAGE # TODO listen to image for changes!

				ENV.snap_out('image set', IMAGE, IMAGE['size'])

				glBindFramebuffer(GL_FRAMEBUFFER, self.__snap_data__['__fbo__'])
				glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, IMAGE['__engine_data__'], 0) # GLint = mipmap level
				#glBindRenderbuffer(GL_RENDERBUFFER, self._rbo_)
				#glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, *IMAGE.size())
				#glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self._rbo_) # depth and stencil buffers

				if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
					raise Exception('framebuffer error!')

				#glBindFramebuffer(GL_FRAMEBUFFER, 0)

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

		#def cmd_fill_spline(self, PAINT, SPLINE):

		#cmd_fill_shape = cmd_fill_spline

		#def cmd_fill_mesh(self, PAINT, MESH):

		# cmd_fill_rect just use this:
		#def cmd_fill_extents(self, PAINT, EXTENTS):

		#def cmd_fill_circle(self, PAINT, x,y, radius):

		#def cmd_fill_ellipse(self, PAINT, x,y, w,h):


		#def cmd_stroke_spline(self, PAINT, SPLINE):

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

		def activate(self):
			"()"
			# TODO
			#ENV.snap_out('activate context', ENV.extern.Qt5.QOpenGLContext.currentContext())
			#ENV.snap_out('render activate')
			fbo = self.__snap_data__['__fbo__']
			if fbo is not None:
				#ENV.snap_out('activate; bind framebuffer')
				glBindFramebuffer(GL_FRAMEBUFFER, fbo)

				#self.__snap_data__['SYNC'] = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
				#OpenGL.glGetError()
				#glFlush()


		def reset(self):
			"()"
			fbo = self.__snap_data__['__fbo__']
			if fbo is not None:
				glBindFramebuffer(GL_FRAMEBUFFER, fbo)

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

				glBindFramebuffer(GL_FRAMEBUFFER, 0)

		def finish(self):
			"()"
			# TODO detach image?

			SYNC = self.__snap_data__['SYNC']
			if SYNC is not None:
				#ENV.snap_out('SYNC', SYNC)
				glWaitSync(SYNC, 0, GL_TIMEOUT_IGNORED)

				glDeleteSync(SYNC)

			#ENV.snap_out('finish; unbind framebuffer')
			glBindFramebuffer(GL_FRAMEBUFFER, 0)
			#ENV.snap_out('render finish')


			import os
			THISDIR = os.path.realpath(os.path.dirname(__file__))
			filepath = os.path.join(THISDIR, 'finished.png')
			if not os.path.exists(filepath):
				''#self['image'].save(filepath)

		def clear(self):
			"()"
			image = self['image']
			if image is not None:
				# TODO should there be a bind call in here?

				glBindFramebuffer(GL_FRAMEBUFFER, self.__snap_data__['__fbo__'])

				w,h = image['size']
				glViewport(0,0,w,h)
				glClearColor(0,0,0,1)
				glClearDepth(1.0)
				glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)


		# TODO set?

		def __init__(self, **SETTINGS):
			SnapContext.__init__(self, **SETTINGS)


			IMAGE = self['image']

			# TODO maybe put these buffers on the window or something?  so we don't have to create and destroy them constantly!
			#	-- put them on image, if they are used on the image...
			#	-- TODO make a SnapRenderConfig class, assign it to the image, but it will handle cleanup when renderinfo is discarded for the image...
			if self.__snap_data__['__fbo__'] is None:
				self.__snap_data__['__fbo__'] = glGenFramebuffers(1)


				if IMAGE is not None:
					glBindFramebuffer(GL_FRAMEBUFFER, self.__snap_data__['__fbo__'])
					glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, IMAGE['__engine_data__'], 0) # GLint = mipmap level
					#glBindRenderbuffer(GL_RENDERBUFFER, self._rbo_)
					#glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, *IMAGE.size())
					#glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self._rbo_) # depth and stencil buffers

					if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
						raise Exception('framebuffer error!')
			if self.__snap_data__['__rbo__'] is None:
				self.__snap_data__['__rbo__'] = glGenRenderbuffers(1)

			# TODO listen to image for changes!

			#ENV.snap_out('image set', IMAGE, IMAGE['size'])


			self.reset()

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

