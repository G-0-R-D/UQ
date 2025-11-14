
import os
THISDIR = os.path.realpath(os.path.dirname(__file__))

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


image = QImage(os.path.join(THISDIR, 'composite_learning.py_test.png'))

render_image = QImage(640, 480, QImage.Format_ARGB32)
ctx = QPainter(render_image)

x,y,w,h = 0,0,image.width(),image.height()
print(QRectF(x,y,w,h))

ctx.drawImage(QRectF(x,y,w,h), image)

render_image.save(os.path.join(THISDIR, 'qt_test.png'))

