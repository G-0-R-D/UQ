
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import * #QApplication, QPushButton
from PyQt5.QtMultimedia import *

from weakref import ref as weakref_ref

#QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts) # one context across all gl windows...?
_app_ = QApplication([]) # so it is always around if Qt5 is used at all (engine or gui)...

try:
	from PyQt5.QtOpenGL import *
	# NOTE: this can only be called after application is initialized
	HAS_OPENGL = QGLFormat.hasOpenGL()
	from OpenGL.GL import glViewport
except:
	HAS_OPENGL = False

__SNAP_OPENGL_WINDOW__ = [None] # only one



class SnapQt5Widget(QWidget):
	__slots__ = []


	@property
	def snap_window(self):
		try:
			return self._snap_window_()
		except:
			return None

	@snap_window.setter
	def snap_window(self, WINDOW):
		if WINDOW is not None:
			WINDOW = weakref_ref(WINDOW)
		self._snap_window_ = WINDOW

	def paintEvent(self, EVENT):
		w = self.snap_window
		if w is not None:
			return w.paintEvent(self)

	def eventFilter(self, SOURCE, EVENT):
		w = self.snap_window
		if w is not None:
			return w.eventFilter(SOURCE, EVENT)
		return False

	def __init__(self, SNAP_WINDOW=None):
		QWidget.__init__(self)

		self.setMouseTracking(True)

		self.installEventFilter(self)

		if SNAP_WINDOW is not None:
			self.snap_window = SNAP_WINDOW

if HAS_OPENGL:
	class SnapQt5OpenGLWidget(QGLWidget):

		__slots__ = []


		@property
		def snap_window(self):
			try:
				return self._snap_window_()
			except:
				return None

		@snap_window.setter
		def snap_window(self, WINDOW):
			if WINDOW is not None:
				WINDOW = weakref_ref(WINDOW)
			self._snap_window_ = WINDOW

		def resizeGL(self, W, H):
			glViewport(0,0,W,H)

		def initializeGL(self):
			pass

		def paintGL(self):
			w = self.snap_window
			if w is not None:
				return w.paintGL(self)

		def closeEvent(self, EVENT):
			# there is only one of these window types, and it will stay open for the entire runtime
			self.setGeometry(0,0,1,1)
			self.hide()

			snap_window = self.snap_window
			if snap_window is not None:
				windows = snap_window.GUI['windows']
				if windows and len(windows) > 1:
					self.setGeometry(0,0,1,1)
					self.hide()
					EVENT.ignore()
					return
			EVENT.accept()

		def eventFilter(self, SOURCE, EVENT):
			w = self.snap_window
			if w is not None:
				return w.eventFilter(SOURCE, EVENT)
			return False

		def __init__(self, SNAP_WINDOW=None):
			QGLWidget.__init__(self)

			self.setMouseTracking(True)

			self.installEventFilter(self)

			if SNAP_WINDOW is not None:
				self.snap_window = SNAP_WINDOW

# TODO else?  make a normal widget?  then it just uses the regular paintEvent? XXX the caller would try to obtain the unused gl window, otherwise just create normal ones...  check user engine?




__SNAP_OPENGL_NEEDS_INIT__ = [True]
def __SNAP_OPENGL_INIT__():
	assert HAS_OPENGL, 'Qt has no opengl backend'
	if not __SNAP_OPENGL_NEEDS_INIT__[0]:
		return
	# create the first (and only) opengl window / context
	window = SnapQt5OpenGLWidget()
	window.setGeometry(0,0,1,1)
	window.show()
	window.hide()
	__SNAP_OPENGL_WINDOW__[0] = window
	__SNAP_OPENGL_NEEDS_INIT__[0] = False

