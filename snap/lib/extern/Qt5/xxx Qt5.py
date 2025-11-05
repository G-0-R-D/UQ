
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import * #QApplication, QPushButton
try:
	from PyQt5.QtOpenGL import *
	HAS_OPENGL = QGLFormat.hasOpenGL
except:
	HAS_OPENGL = lambda : False

def build(EXTERN):

	# XXX don't build, just import and assign the module itself to the ENV...

	class Qt5(object):

		_app_ = QApplication([]) # so it is always around if Qt5 is used at all (engine or gui)...

		def has_opengl(self):
			# NOTE: this can only be called after application is initialized
			return HAS_OPENGL()

		def _run_widget(self, WIDGET, *args, **kwargs):
			app = QApplication([])
			#print('has', self.has_opengl())
			w = WIDGET(*args, **kwargs)
			w.show()
			app.exec()

		def __init__(self):

			self.QApplication = QApplication

			self.QWidget = QWidget
			self.QDesktopWidget = QDesktopWidget # to get the screen size

			self.QEvent = QEvent
			self.QTimer = QTimer
			self.Qt = Qt

			self.QColor = QColor

			self.QImage = QImage
			self.QPixmap = QPixmap

			self.QPainter = QPainter
			self.QPainterPath = QPainterPath

			self.QStaticText = QStaticText
			self.QTextDocument = QTextDocument
			self.QTextCursor = QTextCursor
			self.QTextEdit = QTextEdit
			self.QFont = QFont
			self.QTextCharFormat = QTextCharFormat
			self.QFontDatabase = QFontDatabase

			self.QPen = QPen
			self.QBrush = QBrush

			self.QMatrix = QMatrix4x4
			self.QTransform = QTransform

			self.QRect = QRect




	EXTERN.Qt5 = Qt5()


if __name__ == '__main__':

	from snap.lib.core import SNAP_GLOBAL_ENV as ENV
	build(ENV)

	# TODO test basic window...

	Qt5 = ENV.Qt5

	Qt5._run_widget(QPushButton, 'Hello World')

	#print('opengl supported', Qt5.has_opengl())
