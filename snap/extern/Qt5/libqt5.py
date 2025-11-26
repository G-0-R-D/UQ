
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import * #QApplication, QPushButton

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts) # one context across all gl windows...
_app_ = QApplication([]) # so it is always around if Qt5 is used at all (engine or gui)...

try:
	from PyQt5.QtOpenGL import *
	# NOTE: this can only be called after application is initialized
	HAS_OPENGL = QGLFormat.hasOpenGL()
except:
	HAS_OPENGL = False

if HAS_OPENGL:
	# this initializes the gl context so it can be used
	__GL_DUMMY = QGLWidget()
	__GL_DUMMY.setGeometry(0,0,1,1)
	__GL_DUMMY.show()
	__GL_DUMMY.hide()

