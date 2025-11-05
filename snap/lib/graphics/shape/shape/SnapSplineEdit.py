
def build(ENV):

	class SnapSplineEditor(object):

		# TODO instead of this we could just initialize a new spline as a copy of the first one, as a SnapSpline, and then push it back to the engine when done...

		__slots__ = ['__spline__']

		def linear(self, MSG):
			# (self, *pts, **SETTINGS):
			'points can be as many as possible, but should be axis aligned (% axes == 0)'

		def bezier(self, MSG):
			#(self, *pts, **SETTINGS):
			'SETTINGS.degree?  then points must align'

		def rectangle(self, MSG):
			# (self, x,y,w,h, **SETTINGS):
			# TODO can also define rectangle as origin and 'diameter' (square), or as two points?
			''

		def rect(self, MSG):
			return self.rectangle.__direct__(MSG)

		def square(self, MSG):
			# (self, center, radius, **SETTINGS):
			''

		def circle(self, MSG):
			# (self, *args, **SETTINGS):
			''

		def ellipse(self, MSG):
			# (self, *args, **SETTINGS):
			''

		def arc(self, MSG):
			# (self, *args, **SETTINGS):
			''

		def star(self, MSG):
			# (self, *args, **SETTINGS):
			'num points'

		# TODO triangle (which is really just a 3 point polygon, maybe make this equilateral triangle specifically...?

		def polygon(self, MSG):
			# (self, *args, **SETTINGS):
			''

		def add_text(self, TEXT):
			'convert text graphic to path, get the description and add it locally'

		# TODO make apply_matrix() assign the shape matrix to the points and then set the shape matrix to 0...?


		def __init__(self, SPLINE):

			# TODO this could be thought of more like a compiler...  just as a stream of commands that will output a result...
			# the shapes are best returned as descriptions we can add in...
			# changing a spline means keeping everything the same except the part you want to change...  so iter the segments...
			# TODO use segments as a property?
			# TODO include ability to insert, remove segments at indices?  'L' indice would be by axes count?  or all are?

			self.__spline__ = SPLINE

	ENV.SnapSplineEditor = SnapSplineEditor
