
#from snap.lib.graphics.SnapCamera import *
#from snap.lib.graphics.SnapContainer import *
#from snap.lib.graphics.SnapContext import *
#from snap.lib.graphics.SnapEngine import * # for instance check

#from snap.lib.core import *

def build(ENV):

	SnapNode = ENV.SnapNode
	SnapCamera = ENV.SnapCamera
	SnapContainer = ENV.SnapContainer
	SnapContext = ENV.SnapContext
	#SnapEngine = ENV.SnapEngine # for instance check XXX ENV.GRAPHICS (but lazy)

	SnapShader = ENV.SnapShader

	SnapMessage = ENV.SnapMessage

	snap_extents_t = ENV.snap_extents_t
	snap_matrix_t = ENV.snap_matrix_t
	SnapMatrix = ENV.SnapMatrix
	snap_matrix_invert = ENV.snap_matrix_invert
	snap_matrix_multiply = ENV.snap_matrix_multiply

	class SnapWindowSettings(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class scroll_size:

			'' # TODO the amount the mouse should scroll by

			# XXX TODO use a settings property, dict...  and use a default global if setting isn't locally defined...

	class SnapWindow(SnapContainer):

		__slots__ = []
		#__slots__ = ['_image_', '_texture_', '_camera_', '_ctx_', '__was_resized__', '__render_verified__']

		SETTINGS = SnapWindowSettings()

		@ENV.SnapProperty
		class camera:
			def get(self, MSG):
				"()->SnapCamera"
				cam = self.__snap_data__['camera']
				if cam is None:
					cam = self.__snap_data__['camera'] = SnapCamera()
					self.changed(camera=cam)
				return cam

			def set(self, MSG):
				"(SnapCamera!)"
				cam = MSG.args[0]
				if cam is not None:
					assert isinstance(cam, SnapCamera), 'not a camera type: {}'.format(repr(cam))
				self.__snap_data__['camera'] = cam
				self.changed(camera=cam)

		@ENV.SnapProperty
		class children:

			def get(self, MSG):
				"()->list(SnapNode*)"
				return self['camera']['children']

			def set(self, MSG):
				"(list|tuple(SnapNode*))"
				return self['camera'].children.set(*MSG.args, **MSG.kwargs)

		@ENV.SnapProperty
		class render_items:

			def get(self, MSG):
				"()->list(SnapNode*)"
				# TODO HUD, camera, background?
				return [self['camera']]

		@ENV.SnapProperty
		class lookup_items:

			def get(self, MSG):
				"()->list(SnapNode*)"
				# TODO HUD, camera, background?
				return [self['camera']]


		@ENV.SnapProperty
		class image:

			def get(self, MSG):
				"()->SnapImage"
				return self.__snap_data__['image'] # XXX TODO get from texture?

			def set(self, MSG):
				" " # disabled
				raise NotImplementedError('window cannot set image')

			"""
			def set(self, MSG):
				""(SnapImage!)""
				image = MSG.args[0]
				if image is not None:
					assert isinstance(image, ENV.SnapImage), 'not an image: {}'.format(repr(image))
				self.__snap_data__['image'] = image
				self.changed(image=image) # TODO update context?
			"""

		@ENV.SnapProperty
		class texture:

			def get(self, MSG):
				"()->SnapTexture"
				return self.__snap_data__['texture']

		#def engine(self, MSG):
		#	return getattr(ENV, 'GRAPHICS', None)

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"()->snap_extents_t"
				# XXX assign local size, make image secondary (ie. when extents are changed (set(extents)) then mark __was_resized__
				image = self['image']
				if image is not None:
					w,h = image['size']
					return snap_extents_t(0,0,0, w,h,0)
				else:
					return SnapContainer.extents.get(self, MSG)

			def set(self, MSG):
				'(snap_extents_t!)'
				image = self['image']
				if image is not None:
					ext = MSG.args[0]
					image['extents'] = ext
					#ENV.snap_out('TODO resize image')
					#self.__snap_data__['__ctx__'] = None
					cam = self['camera']
					if cam is not None:
						# TODO keep camera origin in same spot as window resizes?
						cam['extents'] = ext

					self.__snap_data__['__render_verified__'] = True

					self.changed(extents=image['extents']) # TODO this needs to update the gui blit texture...
				else:
					SnapContainer.extents.set(self, MSG)
				self.__snap_data__['__was_resized__'] = True

				

		@ENV.SnapChannel
		def device_event(self, MSG):
			"()"
			action, device, source = MSG.unpack('action', None, 'device', None, 'source', None)

			if isinstance(device, ENV.SnapDevicePointer):
				if action == 'scroll':

					# TODO make this a configurable behaviour, maybe attach a node representing hotkeys and inputs?

					if source['delta'] > 0:
						scale = 0.9
					elif source['delta'] < 0:
						scale = 1.1
					else:
						scale = None

					if scale != None:
						camera = self['camera']

						mat = snap_matrix_t(*camera['matrix'])

						# TODO make the origin the mouse position?  in local coordinates...  need either the window passed in, or local coordinates included in message... TODO just add local coordinates for now

						origin = snap_matrix_t(1,0,0,self['width'] / 2, 0,1,0,self['height']/2, 0,0,1,0, 0,0,0,1)
						snap_matrix_multiply(mat, origin, mat)

						self['camera'].scale(scale,scale,scale, parent=SnapMatrix(matrix=mat))
						
					#ENV.snap_out('after transform', self['camera']['matrix'][:])

				elif action in ('press', 'release') and source in (device.get('buttons') or []) and source['name'] == 'middle':

					local_delta = MSG.unpack('local_delta', None)

					#ENV.snap_out('middle button!', action, local_delta)

				elif action == 'drag' and source in (device.get('buttons') or []) and source['name'] == 'middle':

					local_delta = MSG.kwargs['local_delta']

					camera = self['camera']

					# TODO wrong scale?  negate camera?
					#ENV.snap_out('translate', [x * -1 for x in local_delta])
					camera.translate(*[x * -1 for x in local_delta], parent=camera)

					#ENV.snap_out('got drag!')
					'' # TODO camera.translate(x,y, parent=camera)


		def _do_resize(self):
			# the window resizes itself lazily (this will be called when render is ready to go)

			window_size = self['size']

			image = self['image']
			if image is None:
				#ENV.snap_warning("cannot resize window without an image!")
				return None

			image_size = image['size']

			if window_size != image_size:
				image.resize(width=int(window_size[0]), height=int(window_size[1]))#, mode="CROP")

			self['__was_resized__'] = False

			#ENV.snap_out('image resized', image)

			#snap_event(snap_getattr(self, "_ctx_"), "SET", "image", image); // XXX ctx should listen for image changes itself

			camera = self['camera']
			ENGINE = self['engine']
			axes = ENGINE['axes']
			if camera is not None and axes is not None and axes > 2:
				raise NotImplementedError('3D')
				"""
				m = snap_matrix_t(*SNAP_IDENTITY_MATRIX)
				#snap_perspective_matrix(45.0, window_size[0] / window_size[1], -1, 1, (double*)m);
				snap_perspective_matrix(window_size[1] / 45.0, window_size[0] / window_size[1], .1, 100., m)
				#snap_perspective_matrix2(window_size[0], window_size[1], .1, 100., (double*)m);
				#snap_out("do resize perspective matrix:");
				#snap_matrix_print(m);
				camera.set(perspective_matrix=m)
				"""

			return None

		def _make_renderable(self, ITEMS):
			# pass in items as list

			# to keep the SnapWindow engine neutral, the engine is determined from the renderable items
			# XXX tie into ENV.GRAPHICS now

			# draw can trigger render from submitted items, even though items are not assigned to window itself!

			ENGINE = self['engine']
			if ENGINE is None:
				#ENGINE = SnapContainer._find_engine(None, ITEMS)
				#self._engine_ = ENGINE
				ENV.snap_warning('no engine defined in Window')
				return False

			if ENGINE is not None and self['image'] is not None:
				return True # ready to go
			
			#if item_engine is None:
			#	return False # nothing to render yet?

			window_size = self['size']
			axes = ENGINE['axes']

			camera = self['camera']
			if camera is None:
				return False

			if axes > 2:
				raise NotImplementedError('3D')
				"""
				#snap_warning("window using perspective matrix");
				# WINDOW._camera_.set(perspective=True) XXX enabled when perspective matrix assigned to non-null?
				m = snap_matrix_t()
				# TODO angle argument to keep window fixed...
				#snap_perspective_matrix(45.0, window_size[0] / window_size[1], -1, 1, (double*)m);
				snap_perspective_matrix(window_size[1] / 45.0, window_size[0] / window_size[1], .1, 100., m)
				#snap_perspective_matrix2(window_size[0], window_size[1], .1, 100., (double*)m);
				camera.set(perspective_matrix=m)
				"""
			else:
				camera['use_perspective'] = False

			image = ENGINE.Image(width=int(window_size[0]), height=int(window_size[1]))
			texture = ENGINE.Texture(image=image)
			#shader = ENGINE.Shader(shape=image, fill_color=texture)

			#ctx = ENGINE.Context(image=image)

			data = self.__snap_data__

			data['image'] = image
			data['texture'] = texture
			#data['shader'] = shader
			#data['__ctx__'] = ctx
			#SnapNode_set(self, 'engine', item_engine)

			data['__was_resized__'] = False
			data['__render_verified__'] = True

			#self.changed(engine=ENGINE)

			return True

		def _prep_for_render(self, ITEMS):
			# pass in ITEMS as list

			if not self['__render_verified__']:
				assert self._make_renderable(ITEMS) # or not ready

			if self['__was_resized__']:
				# done right before render to minimize resize spam,
				# image does not actually need to be resized until it is used!
				self._do_resize()

			return None

		@ENV.SnapChannel
		def render(self, MSG):

			#ENV.snap_out('window render')

			items = self['render_items']

			# draw to self.image
			try:
				self._prep_for_render(items)
			except Exception as e:
				ENV.snap_debug('render not ready', ENV.snap_exception_info(e))
				return None

			ENGINE = self['engine']

			#ENV.snap_out("render", list(items))

			#camera = self['camera'] or SnapCamera()
			#m = camera['render_matrix']

			#ENV.snap_out("ctx.do_draw", self['image'], self['render_items'])
			ENGINE.do_draw(image=self['image'], items=self['render_items'])#, offset=m)

			#import os
			#pth = '/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/test_out.png'
			#if not os.path.exists(pth):
			#	self['image'].save(pth)

			return None


		def draw(self, CTX):
			# clipping and sub-render done by shader
			# TODO window serves as mediator between engines?  so we can create a window for an engine, add the items of the engine in to the window, and then this will check if the engine is different and if so do the buffer transfer and draw that?  TODO but we'd like to keep the buffer around for efficiency...

			# TODO if buffered then we just draw the window (maybe call render to make sure it is current?)
			# otherwise we can draw the scene

			CTX.cmd_save()
			CTX.cmd_clip_extents(self['extents'])
			CTX.cmd_render_subitems()
			CTX.cmd_restore()

			return None

		def lookup(self, CTX):

			CTX.cmd_save()
			CTX.cmd_clip_extents(self['extents'])
			CTX.cmd_render_subitems()
			CTX.cmd_restore()

			return None
			"""

			if len(MSG.args[0]) == 1:
				# draw onto context with clip

				CTX = MSG.args[0]

				CTX.save()
				CTX.cmd_clip_extents(self.extents()) # TODO extents...

				SnapContainer.lookup(self, MSG) # XXX CTX.cmd_render_subitems() ?  we don't render self XXX apply a lookup_shader that could also take a custom clip shape?  with a default to a rect?

				CTX.restore()

			else:
				# create new context

				x,y = MSG.unpack('x',0, 'y',0)

			ENGINE = self.engine()
			assert ENGINE is not None, 'indeterminable engine'

			items = self.lookup_items()

			camera = self.camera() or SnapCamera()
			m = camera.render_matrix()
			# TODO MSG offset: then matrix_multiply(MSG.offset, m, m);

			

			return ENGINE.lookup(x,y, items=items, offset=m)
			"""

		@ENV.SnapProperty
		class shader:
			def get(self, MSG):
				#raise NotImplementedError('shader not implemented on window (yet)') # TODO custom shader on window?
				"()->SnapShader"
				return self.__snap_data__['shader']

			#def set(self, MSG):
			#	raise NotImplementedError('shader on window')
			set = None


		@ENV.SnapChannel
		def allocateXXX(self, MSG): # XXX just set extents
			"""(extents=snap_extents_t)"""

			#ENV.snap_out("allocate called")

			extents = MSG.unpack('extents', None)
			# NOTE: SnapMetrics_event(self, "CROP", ...) will call snap_event(self, "SET", "extents", ...)
			# and that triggers the resize of the window buffer in the SET handler
			if extents is not None:
				self.set(extents=extents)
			
			return None


		@ENV.SnapChannel
		def set(self, MSG):
			"""(
			(camera=SnapCamera?),
			)"""
			return SnapContainer.set(self, MSG)
			"""
			data = self.data()

			ext = data.get('extents') or snap_extents_t()
			ext_changed = False

			for attr,value in MSG.kwargs.items():

				if attr == 'camera':
					if value:
						assert isinstance(value, SnapCamera), 'must be SnapCamera'
					data['camera'] = value # can be NULL

				elif attr in ('size', 'width', 'height', 'extents'):

					if value is not None:

						if attr == "size":
							ext[3] = value[0]
							ext[4] = value[1]

						elif attr == "width":
							ext[3] = value

						elif attr == "height":
							ext[4] = value

						elif attr == "extents":
							ext[:] = value[:]

					else:
						ext = snap_extents_t(0,0,0,1,1,1)

					ext_changed = True

					#ENV.snap_out(">> window resized!", ext)

				elif attr == "shader":
					ENV.snap_warning("TODO custom shader assignment for SnapWindow?")

				else:
					SnapContainer.set(self, SnapMessage(**{attr:value}))

			if ext_changed:
				# calls the superclass directly to set the variable there, not here!
				#snap_event_redirect(SnapMetrics_event, self, "SET", "extents", ext);
				data['extents'] = ext
				data['__was_resized__'] = True

			return None
			"""

		def __init__(self, *items, **SETTINGS):
			SnapContainer.__init__(self, *items, **SETTINGS)

			ENV.snap_out('window init')

			#include "snap/lib/graphics/SnapShader.h" // XXX until SnapRenderinfo organization is resolved, pull in here for definition...


			#ENV.snap_out('data', data.keys())

			#self['extents'] = snap_extents_t(0,0,0,1,1,1)

			data = self.__snap_data__

			data['image'] = None
			data['texture'] = None
			#data['__ctx__'] = None
			#self._engine_ = None
			#self['camera'] = SnapCamera()
			data['__was_resized__'] = True
			data['__render_verified__'] = False

			#self.set(**{k:v for k,v in SETTINGS.items() if k in ('camera',)})

	ENV.SnapWindow = SnapWindow

def main(ENV):

	ENV.__run_gui__(ENV.SnapWindow)
	ENV.snap_out('ok')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv(engine='QT5'))

