
# display for any code type, with render or code display options (if it has a draw then render calls the draw and displays it in the window area provided by this graphic -- think node display of an element so it can appear in a space -- this is the renderable element in the space and it can be ANYTHING!)

def build(ENV):

	SnapContainer = ENV.SnapContainer

	class UQGraphic(SnapContainer):

		__slots__ = []

		@ENV.SnapProperty
		class object:

			def get(self, MSG):
				"()->object"
				return self.__snap_data__['object']

			def set(self, MSG):
				"(object!)"
				# TODO make shaders for each object type and then load the appropriate shader to display the object...
				# basic code structures like object, function, etc...
				# or renderable structures that implement draw() etc...

				# make a corner display for node or render view # TODO SnapProperty: view_mode


				data = self.__snap_data__

				obj = MSG.args[0]
				
				current = data['object']
				data['object'] = obj


				# TODO create a dict/json representation of all the inputs/outputs (properties and channels) or any other datatypes...  then we just need to render them with the current style...  so the shader for this object just renders the shaders for the others...

				if current is not obj:
					self.changed(object=obj)
				else:
					self.update() # call it anyway


		@ENV.SnapProperty
		class compact:

			def get(self, MSG):
				"()->bool"
				return bool(self.__snap_data__['compact'])

			def set(self, MSG):
				"(bool!)"
				value = bool(MSG.args[0])
				existing = self.__snap_data__['compact']
				self.__snap_data__['compact'] = value

				if existing != value:
					self.changed(compact=value)

				self.update()
				


		@ENV.SnapProperty
		class view_mode:

			def get(self, MSG):
				"()->str"
				return self.__snap_data__['view_mode'] or 'NODE'

			def set(self, MSG):
				"(str!)"
				mode = MSG.args[0]
				if mode is None:
					mode = 'NODE'
				else:
					mode = mode.upper()
					assert mode in ('NODE','VIEWER'), 'unsupported view mode: {}'.format(repr(mode))

				self.__snap_data__['view_mode'] = mode
				self.changed(view_mode=mode)

				self.update()



		@ENV.SnapChannel
		def update(self, MSG):
			"()"

			# TODO make types for each of the display configurations, nodules, etc...
			#	-- handle config with ['display'] = dict() so if settings aren't supported with this graphic it's not an issue...

			IS_COMPACT = bool(self['compact'])
			VIEW_MODE = self['view_mode'] or 'NODE'
			OBJECT = self['object']

			if VIEW_MODE == 'VIEWER':
				assert hasattr(OBJECT, 'draw') # TODO?
				'basically just draw a rectangle and then jump into the draw call of object'
				#	-- make a window if it isn't a window, same as gui...

				# if compact only do the render
				# otherwise also draw the input/output nodules if any

			elif VIEW_MODE == 'NODE':
				'do a display for the channels and properties (or methods/attrs if object)'

			else:
				raise ValueError(VIEW_MODE)

			# graphics can be shapes drawn with colors or images swapped out...
			#	-- shape with color or image fill, image can be sequence...

			# TODO this will create graphical representation for whatever self['node'] is, which must be some object type, and we'll crawl it...
			# if it's a SnapNode then display the node api, otherwise if it's a generic object then crawl the dir() and display the types, methods, attrs, ... in a way that is clear
			#	-- allow connections between components even if they aren't explicitly obvious, use inspect to list args?  or if source is available we can peruse the ast ourselves...

			# TODO get the graphics from ENV.STYLING, so they can be changed
			# TODO the scene would listen to STYLING for changes and update all the contained nodes if the styling is changed...
			# TODO graphic = ENV.STYLING.Graphic(**display) or ENV.STYLING.Undefined(**display)
			#	-- TODO consider the graphic as a container for the renderable, which can be animated as a series?
			#		-- renderable similar to timeline?  with ability to swap to another graphic?
			#		-- renderable can have image sequence...?  maybe make image sequence a graphic/renderable type?
			#		-- sequences for shapes and colors can also be useful... animation key sets?  pass in info as series of dicts?
			# display is either a single dict or a list of dicts?  and then blendshape kind of data can be in one dict...
			#	-- keyframes can be in each dict?


		def draw(self, CTX):
			return SnapContainer.draw(self, CTX)

		def lookup(self, CTX):
			return SnapContainer.lookup(self, CTX)


		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)


	ENV.UQGraphic = UQGraphic


def main(ENV):

	ENV.__run_gui__(ENV.UQGraphic(object=ENV))
