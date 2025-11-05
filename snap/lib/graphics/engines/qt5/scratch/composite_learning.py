
def main(ENV):

	#from snap.lib.core import SNAP_GLOBAL_ENV as ENV
	#from snap.lib import extern, graphics
	#extern.build(ENV)
	#graphics.build(ENV)
	#ENV.__LOCAL_ENGINE__ = None
	#build(ENV)

	import os
	THISDIR = os.path.realpath(os.path.dirname(__file__))

	Qt5 = ENV.extern.Qt5

	W,H = 640,480

	img = Qt5.QImage(W,H, Qt5.QImage.Format_ARGB32)

	with Qt5.QPainter(img) as ptr:

		ptr.fillRect(0,0,W,H, Qt5.QColor(255,255,255,255))

		ptr.setWorldTransform(Qt5.QTransform())

		m = Qt5.QTransform()
		print([getattr(m,a)() for a in ('m11', 'm12', 'm13', 'm21', 'm22', 'm23', 'm31', 'm32', 'm33')])

		margin = 25
		while (H/2)-margin > 0:
			ptr.drawRect(margin,margin,W-(2*margin), H-(2*margin))
			margin += 25

		# TODO figure out a compositing example (for alpha blending)
		# https://doc.qt.io/qtforpython-5/overviews/qtwidgets-painting-imagecomposition-example.html#image-composition-example
		output = Qt5.QImage(W,H, Qt5.QImage.Format_ARGB32)
		with Qt5.QPainter(output) as comp:

			a = Qt5.QImage()
			a.load(os.path.join(THISDIR, 'www.freepngimg.com png 176-eagle-png-image-with-transparency-download.png'))
			a = a.scaled(W,H, aspectRatioMode=Qt5.Qt.KeepAspectRatio, transformMode=Qt5.Qt.FastTransformation)
			b = Qt5.QImage()
			b.load(os.path.join(THISDIR, 'welearnls.com the-importance-of-transparency.jpg'))
			b = b.scaled(W,H, aspectRatioMode=Qt5.Qt.KeepAspectRatio, transformMode=Qt5.Qt.FastTransformation)
			#ptr.drawImage(0,0, a)

			comp.setCompositionMode(Qt5.QPainter.CompositionMode_Source)
			comp.fillRect(output.rect(), Qt5.Qt.transparent)

			comp.setCompositionMode(Qt5.QPainter.CompositionMode_SourceOver)
			comp.drawImage(0, 0, a)
			comp.setCompositionMode(Qt5.QPainter.CompositionMode_SourceIn) # TODO change this one
			comp.drawImage(0, 0, b)
			#comp.setCompositionMode(Qt5.QPainter.CompositionMode_DestinationOver)
			#comp.fillRect(output.rect(), Qt5.Qt.white)

		ptr.drawImage(0,0, output)

	img.save(__file__+'_test.png')

	print(Qt5.QColor.black)

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv(engine='QT5'))

