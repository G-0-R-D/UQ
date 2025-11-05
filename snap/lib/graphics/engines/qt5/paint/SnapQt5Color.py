
# TODO _snap_engine_data_ is QColor?
# QColor.setRgbF|getRgbF

def build(ENV):

	SnapColor = ENV.SnapColor

	SnapMessage = ENV.SnapMessage

	Qt5 = ENV.extern.Qt5
	QColor = Qt5.QColor

	ENGINE = ENV.graphics.__current_graphics_build__

	class SnapQt5Color(SnapColor):

		__slots__ = []

		@ENV.SnapProperty
		class engine:
			def get(self, MSG):
				"""()->SnapQt5Engine"""
				return ENGINE


		@ENV.SnapProperty
		class data:

			def get(self, MSG):
				"""()->list(4 * float)"""
				qt_color = self['__engine_data__']
				if qt_color is not None:
					return [qt_color.redF(), qt_color.greenF(), qt_color.blueF(), qt_color.alphaF()]
				return [0.,0.,0.,1.]

			def set(self, MSG):
				"""(list(4 * float)!)"""

				rgba = MSG.args[0]
				assert rgba is not None and isinstance(rgba, list) and len(rgba) == 4, 'wrong format'
				clamp = lambda v: max(0.0, min(v, 1.0))

				qt_color = self['__engine_data__']
				if qt_color is None:
					qt_color = QColor()
				qt_color.setRedF(clamp(rgba[0]))
				qt_color.setGreenF(clamp(rgba[1]))
				qt_color.setBlueF(clamp(rgba[2]))
				qt_color.setAlphaF(clamp(rgba[3]))
				self.__snap_data__["__engine_data__"] = qt_color

				self.changed(data=rgba)

		"""
		def _as(self, MSG):

			KEY = MSG.unpack('key', 'RGBA')

			color = self.__engine_data__()
			if color is None:
				return SnapColor._reformat(self, SnapMessage(KEY, [0.,0.,0.,1.]))

			if not isinstance(color, QColor):
				raise TypeError('engine data not a qt5 type?')

			arr = [color.redF(), color.greenF(), color.blueF(), color.alphaF()]
			return SnapColor._reformat(self, SnapMessage(KEY, arr))


		def set(self, MSG):

			changed = False

			color = self._as('RGBA')

			for attr,value in MSG.kwargs.items():

				color = SnapColor._decode_setting(self, SnapMessage(attr, value, color))
				if color is not None:
					qt_color = self.data().get('__engine_data__')
					if qt_color is None:
						qt_color = self.data()['__engine_data__'] = QColor()

					qt_color = QColor()
					qt_color.setRedF(max(0., min(1., color[0])))
					qt_color.setGreenF(max(0., min(1., color[1])))
					qt_color.setBlueF(max(0., min(1., color[2])))
					qt_color.setAlphaF(max(0., min(1., color[3])))
					self.data()['__engine_data__'] = qt_color

					changed = True

				else:
					SnapColor.set(self, SnapMessage(**{attr:value}))

			if changed:
				self.changed(color=color, format='rgba')
		"""

		def __init__(self, *args, **kwargs):
			SnapColor.__init__(self, *args, **kwargs)


		def __delete__(self):
			''
			#if self._snap_engine_data_:
			#	self._snap_engine_data_ = None


		def __del__(self):
			self.__delete__()

	ENGINE.SnapQt5Color = SnapQt5Color
	return SnapQt5Color


def main(ENV):

	ENV.graphics.load('QT5')

	c = ENV.GRAPHICS.SnapQt5Color(0., .25, .5, 1.0)
	print(c._as('bagr'))

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())

