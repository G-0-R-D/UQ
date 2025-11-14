
from weakref import ref as weakref_ref

def build(ENV):

	SnapContainer = ENV.SnapContainer
	SnapShader = ENV.SnapShader

	snap_extents_t = ENV.snap_extents_t

	GFX = ENV.GRAPHICS


	# TODO so BG_COLOR would be relative color of ENV.STYLE['base_color']?
	# TODO also, we just need the string/text of the code!  the variables will stay the same!
	#	-- we can make a shader program subclass for styling, which has access to style variables as well...
	#	-- make it so it tries to access bg_color from uservars, and if not there it gets from style?

	# TODO pass button into ShaderProgram init (special version?) and then update() will pull the necessary info from the button to the local variables for the render

	# TODO style assigns shaders by name (so we can use mro to resolve?) -- maybe by purpose to, code view vs gui widgets...
	#	-- colors are assigned by type name as well?  if no type name then base color of style itself is used?  and local can override the type...

	class SnapButtonShader(SnapShader):

		__slots__ = []


		# properties: background(paint), foreground(paint), press(0.0->1.0), pull(0.0->1.0), select(0.0->1.0), hover(0.0->1.0)
		# direction(x,y,z) for lean?
		# clip shape, bordered/outline(dashes?)

		# animation = drive properties (like animate the color outside the shader), or use the shader to swap buffers like image sequences...

		# TODO this needs to implement hover,push,pull,select so that it can be handled in here (whether it's simple color change or queue of an animation of image sequences!)
		#	-- XXX we pass in the button and get the hover,push,pull,select,... status from there...

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"()->snap_extents_t"
				# TODO get from shape?  or we can assign to use for rect drawing...
				ext = self.__snap_data__['extents']
				if ext is None:
					ext = self.__snap_data__['extents'] = snap_extents_t(0,0,0, 50,20,0)
				return ext

			def set(self, MSG):
				"(snap_extents_t!)"
				# TODO this is the crop/allocate...  resize shape or assign rect?
				return SnapContainer.extents.set(self, MSG)

		@ENV.SnapProperty
		class shape:

			def get(self, MSG):
				"()->SnapPath|SnapMesh"
				# TODO make sure it exists if not assigned...
				return GFX.Path(description=['S',0,0, 100,0, 100,100, 0,100, 'C'])

			def set(self, MSG):
				"(SnapPath|SnapMesh)"
				# TODO

		@ENV.SnapProperty
		class base_color:

			def get(self, MSG):
				"()->SnapColor"
				color = self.__snap_data__['base_color']
				if color is None:

					# TODO ENV.STYLE['SnapButton.base_color'] ?

					try: color = ENV.STYLE['base_color']
					except: pass
				if color is None:
					color = GFX.Color(.5,.5,.5,1.)
				return color

			def set(self, MSG):
				"(SnapColor!)"
				# TODO

		@ENV.SnapProperty
		class background_color:

			'' # TODO relative to base_color
			def get(self, MSG):
				"()->SnapColor"
				return self.__snap_data__['background_color'] or GFX.Color(.5, .5, .5, 1.)

		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"()->SnapText"
				return self.__snap_data__['text']

			def set(self, MSG):
				"(str|SnapText!)"
				# TODO

		# TODO bordered/outline (thickness? (relative) color?)
		# TODO clipping?  y/n?  just accept a json description of options?

		# TODO use ENV.STYLE for any unassigned defaults?


		def update(self, BUTTON, **SETTINGS):
			'' # TODO make sure shape fits the source size

			# TODO check hover, push, pull, direction, and select and update shapes accordingly?

			# TODO this basically just uses the extents and draws inside of it, so we resize and allocate the shapes...

			#ENV.snap_out('UPDATE!')
			ext = snap_extents_t(*BUTTON['extents'])
			margin = 0
			ext[3] -= margin
			ext[4] -= margin
			ext[0] += margin
			ext[1] += margin
			self['extents'] = ext

			base_value = .5

			pressure = BUTTON['pressure']
			if pressure < 0:
				base_value = .75 + (pressure * .2)
			elif pressure > 0:
				base_value = .25 - (abs(pressure) * .2)

			hover = BUTTON['hover']
			if hover > 0:
				base_value += .1

			if BUTTON['selected']:
				base_value += .1

			self.__snap_data__['background_color'] = GFX.Color(base_value, base_value, base_value, 1.0)

		def draw(self, CTX):
			#CTX.cmd_fill_path(self['background_color'], self['shape'])
			CTX.cmd_fill_extents(self['background_color'], self['extents'])
			#ENV.snap_out(CTX['image']['pixels']['data'][(640*40*4)+50:])
			#import os
			#if not os.path.exists('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/draw_out.png'):
			#	#ENV.snap_out('image size', CTX['image']['size'])
			#	CTX['image']['__engine_data__'].save('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/draw_out.png')

		def lookup(self, CTX):
			#ENV.snap_out('perform lookup', CTX['matrix'][:], self['extents'][:])
			#CTX.cmd_apply_matrix()
			CTX.cmd_fill_extents(self['background_color'], self['extents'])
			CTX.cmd_check_interact()
			#ENV.snap_out('lookup results', CTX['lookup_results'])

		def __init__(self, *a, **k):
			SnapShader.__init__(self, *a, **k)

	ENV.SnapButtonShader = SnapButtonShader

	class SnapButton(SnapContainer):

		__slots__ = []


		# TODO XXX all visibility done through ShaderProgram, with relative color variables, and everything else, ENV.STYLE['SnapButton'] for default
		# make ShaderProgram instance for each style mode ('bubblegum', 'monster truck', etc...) and then we can say 'bubblegum.SnapButton' or 'monster_truck.SnapButton' or other identifiers could be assigned for specific implementations...
		# the shader implementation should provide generalized properties, for setting background color and border options...?
		# so no matter what shader is assigned we can just forward the color assignment from here, and use relative color?

		@ENV.SnapProperty
		class shader:

			def get(self, MSG):
				"()->SnapButtonShader"
				shader = self.__snap_data__['shader']
				if shader is None:
					'get from ENV.STYLE[self.__class__.mro()] -> find first match' # TODO
					'get from ENV.STYLE["default"][self.__class__.mro()]' # TODO
					shader = SnapButtonShader() # local default (failsafe)
					self.__snap_data__['shader'] = shader
					#shader.update(self)
					self.changed(shader=shader)
				return shader

			def set(self, MSG):
				"(SnapShader!)"
				shader = MSG.args[0]
				if shader is not None:
					assert isinstance(shader, SnapButtonShader), 'button only accepts SnapButtonShader type, not: {}'.format(type(shader))
				self.__snap_data__['shader'] = shader
				self.changed(shader=shader)
			

		@ENV.SnapProperty
		class extents:

			def get(self, MSG):
				"()->snap_extents_t"
				ext = self.__snap_data__['extents']
				if ext is None:
					ext = self.__snap_data__['extents'] = snap_extents_t(0,0,0, 50,25,0)
				return ext					

			def set(self, MSG):
				"(snap_extents_t!)"
				# assign to self
				ext = MSG.args[0]
				#if ext is None:
				#	ext = snap_extents_t(0,0,0,50,25,0)
				#ENV.snap_out('extents', ext[:])
				self.__snap_data__['extents'] = ext
				self.changed(extents=ext)


		@ENV.SnapProperty
		class text:

			def get(self, MSG):
				"()->str"
				# TODO

			def set(self, MSG):
				"(str)"
				# TODO
				text = MSG.args[0]
				ENV.snap_out("set button text", text)


		@ENV.SnapProperty
		class selected:
			# TODO select() means a collection, selected refers to bool state

			def get(self, MSG):
				"()->float" # float so we can have range of selected behaviour (kind of selected?)
				return self.__snap_data__['selected'] or 0.

			def set(self, MSG):
				"(bool|float!)"
				value = float(MSG.args[0] or 0.) # True or False become 1.0 or 0.0
				existing = self['selected']
				self.__snap_data__['selected'] = value
				if existing != value:
					self.changed(selected=value)

		@ENV.SnapProperty
		class hover:

			def get(self, MSG):
				"()->float"
				return self.__snap_data__['hover'] or 0.

			def set(self, MSG):
				"(bool|float!)"
				value = float(MSG.args[0] or 0.)
				existing = self['hover']
				self.__snap_data__['hover'] = value
				if existing != value:
					self.changed(hover=value)


		@ENV.SnapProperty
		class pressure:
			# can be positive (press down) or negative (pull up)

			def get(self, MSG):
				"()->float"
				return self.__snap_data__['pressure'] or 0.

			def set(self, MSG):
				"(bool|float!)"
				value = float(MSG.args[0] or 0.) # TODO clamp to -1.0 -> 1.0
				existing = self['pressure']
				self.__snap_data__['pressure'] = value
				if existing != value:
					self.changed(pressure=value)

					if value == 1.0:
						self.press.emit()
					elif value == 0.0:
						self.release.emit()
						self.click.emit()
					elif value == -1.0:
						self.pull.emit()


		@ENV.SnapChannel
		def device_event(self, MSG):
			action, device, source = MSG.unpack('action', None, 'device', None, 'source', None)
			#ENV.snap_out("device event", action, MSG.kwargs)#list(MSG.kwargs.keys()))

			#lookup_results = MSG.unpack('lookup_results', None)
			#ENV.snap_out('lookup_results', lookup_results)

			if isinstance(device, ENV.SnapDevicePointer):

				if action == 'proximity':
					self['hover'] = MSG.unpack('state', False)

				elif action == "press":
					#ENV.snap_out('press', MSG.unpack('local_position',None))
					self.press()
					return True

				elif action == "release":
					#ENV.snap_out('release', MSG.unpack('local_position',None), source.get('delta'))
					self.release()
					#return True


		@ENV.SnapChannel
		def changed(self, MSG):

			shader = self['shader']
			if shader is not None:
				shader.update(self)

			return SnapContainer.changed(self, MSG)
				

		@ENV.SnapChannel
		def press(self, MSG):
			"()"
			self['pressure'] = 1.0 # press event sent here

		@ENV.SnapChannel
		def release(self, MSG):
			"()"
			self['pressure'] = 0.0 # release event sent here

		@ENV.SnapChannel
		def pull(self, MSG):
			"()"
			self['pressure'] = -1.0

		@ENV.SnapChannel
		def click(self, MSG):
			"()"
			self.press()
			self.release()

		# TODO make the graphic component an attachment and pass it instructions on how to display...?  highlight, animate, ...?
		#	-- press (pressure? count?), release

		# TODO button graphic accepts: press 0.0->1.0, release 0.0->1.0, hover 0.0->1.0, select 0.0->1.0, ...
		#	-- and multiple can be active at once like press, hover, and selected...

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			#self['shader'] = SnapButtonDefaultShader() # TODO get from ENV.STYLE.shader['SnapButton']?  TODO self.__DEFAULT_SHADER__ if not in ENV.STYLING?  or make default_shader a property that returns new instance?  or just make the default shader check if shader is none, and if it is it gets from styling, otherwise returns the default directly
			#	-- local assigned, or styling assigned (in theme by name), or styling default, or local default!

			#self.changed()

			#self['extents'] = snap_extents_t(0,0,0, 640,480.0)


	ENV.SnapButton = SnapButton
	return SnapButton


def main(ENV):
	# TODO ?
	build(ENV)
	ENV.__run_gui__(ENV.SnapButton, text='push me!')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


