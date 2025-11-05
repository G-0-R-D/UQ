
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import * #QApplication, QPushButton
try:
	from PyQt5.QtOpenGL import *
	# NOTE: this can only be called after application is initialized
	HAS_OPENGL = QGLFormat.hasOpenGL
except:
	HAS_OPENGL = lambda : False

_app_ = QApplication([]) # so it is always around if Qt5 is used at all (engine or gui)...

