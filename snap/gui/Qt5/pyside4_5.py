
from snap.extern.ext_opengl import *
from PySide import QtCore, QtGui, QtOpenGL

import sys

import re

def split_case(STRING):	
	slices = [match.group(match.lastindex) for match in re.compile('([A-Z][^A-Z]+)|([A-Z])|([^A-Z]+)').finditer(STRING)]
	if not slices:
		return [STRING]
	return slices		

def screensize():
	SCREEN = QtGui.QDesktopWidget().screenGeometry()
	return [SCREEN.width(), SCREEN.height()]

def centered_window(WIDGET, **SETTINGS):
	alignmentx = SETTINGS.get('%x', 0.5)
	alignmenty = SETTINGS.get('%y', 0.5)
	scalex = SETTINGS.get('%w', 0.5)
	scaley = SETTINGS.get('%h', 0.5)

	width,height = screensize()
	
	#scalex, scaley = 0.9, 0.75
	#alignmentx, alignmenty = 0.5, 0.5
	WIDGET.setGeometry(
		alignmentx * (width - (width * scalex)), 
		alignmenty * (height - (height * scaley)), 
		width * scalex, height * scaley	)


def set_transparent(WIDGET):
	palette = WIDGET.palette()
	palette.setBrush(QtGui.QPalette.Base, QtCore.Qt.transparent)
	WIDGET.setPalette(palette)
	WIDGET.setAttribute(QtCore.Qt.WA_TranslucentBackground)

def get_events_dict():
	return {'EVENT_' + '_'.join(split_case(ename)).upper():getattr(QtCore.QEvent.Type, ename) for ename in dir(QtCore.QEvent.Type) if not ename.startswith('_') and type(getattr(QtCore.QEvent.Type, ename)) == QtCore.QEvent.Type}
globals().update(get_events_dict())

def build(CODES, CH, Relay, Container, Window, engines, animate, devices, interact, gui_utils, Matrix, draw, debug, **X):
	#for event in sorted(get_events_dict().keys()):
	#	print(event)

	KEYBOARD = devices.Device()
	devices.keyboard.register(KEYBOARD)
	KEYBOARD_emit = KEYBOARD.emit # TODO use event?

	POINTER = devices.Device()
	devices.pointer.register(POINTER)
	POINTER_emit = POINTER.emit

	qt_has_gl = QtOpenGL.QGLFormat.hasOpenGL
	#qt_has_gl = lambda:False

	def build_window(OWNER):

		OWNER_event = OWNER.event

		if qt_has_gl():
			QWIDGET = QtOpenGL.QGLWidget
		else:
			QWIDGET = QtGui.QWidget

		class PySideWindow(QWIDGET):

			# __slots__ TODO

			PREFERRED_ENGINE = 'opengl' # replace on load opengl?

			def __init__(self, **SETTINGS):
				if qt_has_gl():
					QWIDGET.__init__(self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers))
				else:
					QWIDGET.__init__(self)

				#self.display_texture = QtGui.QImage(self._app.renderbuffer.imagebuffer.pixels, w, h, QtGui.QImage.Format_ARGB32)
				#self.display_texture = QtGui.QImage()

				self.setWindowTitle(SETTINGS.get('title', sys.argv[0]))

				centered_window(self)
				if SETTINGS.get('transparent', True):
					set_transparent(self)


				#self.setWindowFlags(QtCore.Qt.FramelessWindowHint)# | QtCore.Qt.SplashScreen)

				self.setMouseTracking(True)

				self._is_fullscreen_ = 0

				#self._user_test_ = []#[Container(shader=engines.opengl.RhobidiumShader())]

				# XXX
				#self.timer = QtCore.QTimer()
				#self.timer.timeout.connect(self.timeout)
				#self.timer.start((1./30)*1000)

				"""
				self.img = QtGui.QImage(640, 480, QtGui.QImage.Format_ARGB32)
				self.ptr = self.img.bits()
				#print(dir(self.ptr), self.ptr)
				#self.ptr.setsize(self.img.byteCount())

				self.imagebuffer = numpy.asarray(self.ptr).reshape(self.img.height(), self.img.width(), 4)

				font_id = QtGui.QFontDatabase.addApplicationFont('graphics/assets/SaginawBold.ttf')
				assert font_id != -1, 'invalid font!'

				font_db = QtGui.QFontDatabase()
				self.font = QtGui.QFontDatabase.applicationFontFamilies(font_id)
				print('font', self.font[-1])

				self.rot = 0
				"""
				def null_func(*args, **kwargs):
					return
				self._render = null_func

				if qt_has_gl():
					self._trigger_update = self.updateGL
				else:
					self._trigger_update = self.update

				self.show()

			def set_fullscreen(self, STATE=None):

				if STATE == None:
					STATE = self.isFullScreen()

				if STATE:
					self.showNormal()
				else:
					self.showFullScreen()


			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			if qt_has_gl():
				def initializeGL(self):
					#print('initializeGL')
					self.GL_DATA = gui_utils.gen_opengl_blit_data()

				def paintGL(self):
					try: gui_utils.use_opengl_blit_data(OWNER._blit_data_, self.width(), self.height(), **self.GL_DATA)
					except: pass
			

				def resizeGL(self, w, h):
					#print('resizeGL', w, h)
					glBindFramebuffer(GL_FRAMEBUFFER, 0)
					glViewport(0,0,w,h)
					try: OWNER_event(CODES.RESIZE, ID=self, size=(w,h))
					except: pass

			else:

				def paintEvent(self, e):

					painter = QtGui.QPainter()
					painter.begin(self)

					try:

						#color = QtGui.QColor(255,150,0,int(.5*255))
						#painter.setBrush(color)
						#painter.setPen(color)
						#painter.drawRect(0,0,self.width(),self.height())

						img_src = OWNER._blit_data_.data['image']
						w,h = img_src.size()
						img = QtGui.QImage(img_src.data, w,h, QtGui.QImage.Format_ARGB32)
						painter.drawImage(0,0,img)

					finally:
						painter.end()
						#print('paint event complete')

				#def resize(self, w, h):
					#print('normal resize', w, h)
					#OWNER_event(CODES.RESIZE, window=self, size=(w,h))
					#return QWIDGET.resize(self, w,h)



			# EVENTS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

			

			def event(self, EVENT):

				etype = EVENT.type()

				if 0: pass

				# WINDOW
				elif etype == EVENT_MOVE:
					pos = EVENT.pos()
					oldpos = EVENT.oldPos()
					x,y = pos.x(), pos.y()
					cx,cy = x-oldpos.x(), y-oldpos.y()
					OWNER_event(CODES.MOVE, ID=self, position=(x,y), change=(cx,cy))

				elif etype == EVENT_RESIZE:
					size = EVENT.size()
					w,h = size.width(), size.height()
					OWNER_event(CODES.RESIZE, ID=self, size=(w,h)) # TODO w,h

				elif etype == EVENT_FOCUS_IN: # TODO: try setting up auto mouse grab with release when user enabled, focus lost = release mouse
					OWNER_event(CODES.FOCUS, ID=self, value=True)

				elif etype == EVENT_FOCUS_OUT:
					OWNER_event(CODES.FOCUS, ID=self, value=False)

				elif etype == EVENT_SHOW:
					''#print('visibility:show')

				elif etype == EVENT_HIDE:
					''#print('visibility:hide')

				elif etype == EVENT_CLOSE:
					#print('window close')
					''


				# KEYBOARD
				elif etype == EVENT_SHORTCUT_OVERRIDE:#EVENT_KEYBOARD_PRESS:
					''#print('key press', dir(EVENT), EVENT.key(), EVENT.text(), EVENT.nativeScanCode(), EVENT.nativeVirtualKey())
					#self.event_out('device.keyboard.raw', {'EVENT':'key.press', 'KEY':event.key(), 'TEXT':event.text(), 'CODE':event.nativeScanCode(), 'HARDWARE':event.nativeVirtualKey()})

					# NETWORK.emit('device.keyboard.press', {'AUTOREPEAT':autorepeat, 'CODE':keycode, 'VALUE':keyval, 'TEXT':string, 'NAME':keyname})
				elif etype == EVENT_KEY_RELEASE:
					''#print('key release') # TODO: 'NAME'
					#self.event_out('device.keyboard.raw', {'EVENT':'key.release', 'KEY':event.key(), 'TEXT':event.text(), 'CODE':event.nativeScanCode(), 'HARDWARE':event.nativeVirtualKey()})


				# MOUSE
				elif etype == EVENT_MOUSE_MOVE:
					#print('mouse move', dir(EVENT))
					pos = EVENT.posF()

					lclx,lcly = pos.x(), pos.y()

					"""
					pointer_data = self.pointer_data
					currx,curry = pointer_data['POS']
					change = (lclx - currx, lcly - curry)
					pointer_data['POS'] = [lclx, lcly]
					"""

					#print('mouse move', lclx,lcly, change)
					#POINTER_emit(CODES.MOVE, device=POINTER, position=(lclx,lcly), change=change)#, tilt=tilt, time=time))

					#self.event_out('device.mouse.raw', {'EVENT':'move', 'DEVICE':'mouse', 'pressure':None, 'POS':[lclx, lcly], 'CHANGE':change})
				elif etype == EVENT_MOUSE_BUTTON_PRESS:
					but = EVENT.button()
					''#print('mouse press', but)
					#self.event_out('device.mouse.raw', {'EVENT':'button.press', 'DEVICE':'?', 'BUTTON':BUTTON_CODES.get(but, but.name)})
				elif etype == EVENT_MOUSE_BUTTON_RELEASE:
					but = EVENT.button()
					''#print('mouse release', but)
					#self.event_out('device.mouse.raw', {'EVENT':'button.release', 'DEVICE':'?', 'BUTTON':BUTTON_CODES.get(but, but.name)})
				elif etype == EVENT_MOUSE_BUTTON_DBL_CLICK:
					but = EVENT.button()
					''#print('mouse double', but)
					#self.event_out('device.mouse.raw', {'EVENT':'doubleclick', 'DEVICE':'?', 'BUTTON':BUTTON_CODES.get(but, but.name)})
				elif etype == EVENT_WHEEL:
					delta = -1
					if EVENT.delta() < 0:
						delta = 1
					''#print('mouse wheel', delta)
					#self.event_out('device.mouse.raw', {'EVENT':'scroll', 'DEVICE':'?', 'DIRECTION':delta})

					#print(dir(event))

					"""
					val = EVENT.direction.real
					if val == 0: self.event_out('mouse.scroll', {'CODE':val, 'AXIS':'y', 'VALUE':1, 'DIRECTION':'up'})
					elif val == 1: self.event_out('mouse.scroll', {'CODE':val, 'AXIS':'y', 'VALUE':-1, 'DIRECTION':'down'})
					elif val == 2: self.event_out('mouse.scroll', {'CODE':val, 'AXIS':'x', 'VALUE':-1, 'DIRECTION':'left'})
					elif val == 3: self.event_out('mouse.scroll', {'CODE':val, 'AXIS':'x', 'VALUE':1, 'DIRECTION':'right'})
					"""
					POINTER_emit(CODES.SCROLL, device=POINTER, index=0, value=delta)

				elif etype == EVENT_ENTER:
					''#print('mouse enter')
				elif etype == EVENT_LEAVE:
					''#print('mouse leave')


				# TABLET # TODO register as own device under pointer category?
				elif etype == EVENT_TABLET_MOVE:
					pos = EVENT.pos()
					hix = EVENT.hiResGlobalX()
					hiy = EVENT.hiResGlobalY()
					lclx = (pos.x() + hix) - int(hix)
					lcly = (pos.y() + hiy) - int(hiy)

					pointer_data = self.pointer_data
					currx,curry = pointer_data['POS']
					change = [lclx - currx, lcly - curry]
					pointer_data['POS'] = [lclx, lcly]

				
					''#print('tablet move', lclx, lcly, EVENT.xTilt(), EVENT.yTilt())
					#self.event_out('device.mouse.raw', {'EVENT':'move', 'DEVICE':'tablet', 'PRESSURE':event.pressure(), 'POS':[lclx,lcly], 'CHANGE':change})
					POINTER_emit(CODES.MOVE, device=POINTER, position=(lclx,lcly), change=change, pressure=EVENT.pressure(), tilt=(EVENT.xTilt(),EVENT.yTilt()))
					return True
				elif etype == EVENT_TABLET_PRESS:
					'' # XXX flag tablet as enabled for mouse device announcement
				elif etype == EVENT_TABLET_RELEASE:
					'' # XXX flag as disabled
				elif etype == EVENT_TABLET_ENTER_PROXIMITY:
					''#print('tablet in')
				elif etype == EVENT_TABLET_LEAVE_PROXIMITY:
					''#print('tablet out')

	

				else:
					''#print('unhandled event', event.type())#dir(event))
			
				return QWIDGET.event(self, EVENT)


			def _bounds(self):
				b = self.geometry()
				x,y,w,h = b.x(),b.y(),b.width(),b.height()
				return x,y,w,h

			def _set_bounds(self, x,y,w,h):
				cx,cy,cw,ch = self._bounds()
				if cx != x or cy != y:
					self.move(x,y)
				if cw != w or ch != h:
					self.resize(w,h)

			# _trigger_update assigned in __init__

			def _set(self, **SETTINGS):
				for k,v in SETTINGS.items():
					if k == 'visible':
						''
					elif k == 'fullscreen':
						''

					else:
						raise AttributeError(k)




		return PySideWindow()




	def null_func(*args, **kwargs):
		return

	def set_draw_method(USER, LIBWINDOW, GL=False):

		user_render = USER._user_render
		user_window = USER._user_window_

		print('set mode to GL', GL)

		if GL:
			#LIBWINDOW.paintEvent = null_func

			def render(*x, **X):
				#print('attempt paintGL')
				return

				try:
					#user_render()

					glBindFramebuffer(GL_FRAMEBUFFER, 0)
					'blit'
				except:
					debug.print_traceback()

			#LIBWINDOW.paintGL = render
			LIBWINDOW._render = render

		else:
			#LIBWINDOW.paintGL = null_func

			def render(self, e):
				#print('attempt paintEvent')
				#super(LIBWINDOW, self).paintEvent(e)
				try:
					#user_render()

					painter = QtGui.QPainter()

					pixels = user_window._image_.pull_data()
					h,w,d = pixels.shape
					new = QtGui.QImage(pixels, w, h, QtGui.QImage.Format_ARGB32)

					painter.begin(self)
					painter.drawImage(0,0, new)
					painter.end()
					'blit' # create painter and all that
					#print('nongl render complete')
				except:
					debug.print_traceback()

			#LIBWINDOW.paintEvent = render
			LIBWINDOW._render = render



	# TODO library window initialized with this instance and calls this instance's event() to communicate?  for resize and render?
	class GuiWindow(gui_utils.GuiWindowBase):

		# __slots__

		def __init__(self):
			gui_utils.GuiWindowBase.__init__(self, build_window(self))

		"""
			#gui_utils.set_container(self, USER)

			#print('user window image', self._user_window_.ENGINE)

			# TODO pre-initialize two windows, one for opengl rendering and one for all others, then just swap them as needed, so all opengl content is made for the same context
			# TODO just use a gl window and render normally into it?  attempt to build a QGLWidget unless OpenGL not available
			self._qtwindow_ = build_window(self)

			animate.fps(30, self.render) # animate.fps(30, self._qtwindow_.update) or updateGL?

		def set_user(self, USER):

			self._qtwindow_.show()
			geometry = self._qtwindow_.geometry()
			x,y = geometry.x(), geometry.y()
			w,h = USER.size() # full_extents?  USER.full_extents().size()
			self._qtwindow_.setGeometry(x,y,w,h)

			gui_utils.set_container(self, USER)

			interact.set_active_window(self)

			is_gl = False
			engine = getattr(self._user_window_, 'ENGINE', None)
			if engine:
				is_gl = (engine.name == 'opengl')
			set_draw_method(self, self._qtwindow_, is_gl)



		def render(self, *args, **kwargs):

			try: self._user_render()
			except: debug.print_traceback()

			self._qtwindow_.update() # TODO just connect update to QTimer?
			

		def event(self, EVENT=None, ID=None, **MESSAGE):

			if ID == self._qtwindow_:
				'qt window events'

			elif ID == self._user_window_:
				'user incoming'
				#print('PysideWindow.event', CODES.decode(EVENT))
				if EVENT == CODES.CHANGED:
					#self._qtwindow_.event(EVENT=EVENT, **MESSAGE)
					print('engine change gui.Window.event')

					#self.set_user(self._user_)
					is_gl = False
					engine = getattr(self._user_window_, 'ENGINE', None)
					if engine:
						is_gl = (engine.name == 'opengl')
					set_draw_method(self, self._qtwindow_, is_gl)

					""
					if self._user_window_.ENGINE == engines.pyside:
						#print('gui is cairo format')
						self._display_texture_ = self._user_window_._texture_
					else:
						#print('gui is not cairo format')
						self._display_texture_ = engines.pyside.Texture(engines.pyside.proxy(self._user_window_._image_))

					#self._user_window_.crop(self._gui_Metrics_)
					""

		"""


	class Gui(Relay):

		# slots
	
		_app = QtGui.QApplication(sys.argv)

		MainWindow = GuiWindow()

		if qt_has_gl():
			MainWindow._gui_window_._set_bounds(0,0,1,1)
			MainWindow._gui_window_.show()

			_app.processEvents()

			engines.opengl

			MainWindow._gui_window_.hide()
			_app.processEvents()
		else:
			''#MainWindow._qtwindow_.show()
			#_app.processEvents()

		def __init__(self):
			Relay.__init__(self)

			CH.QUIT.listen(self.quit)

			#self._app.setOverrideCursor(QtCore.Qt.BlankCursor)

			self._timer = QtCore.QTimer()
			#self._timer.timeout.connect(self.timeout)
			self._timer.timeout.connect(CH.REFRESH.emit)

			#self.Window = PySideWindow			

		#def Window(self, USER):
		#	self.MainWindow.set_user(USER)
		#	return self.MainWindow

		def init_user(self, USER):
			'first time initialize user and center window'
			self.MainWindow.set_user(USER)
			centered_window(self.MainWindow._gui_window_)
			self.MainWindow._gui_window_.show()

			

		def start(self, *args, **kwargs):

			f = QtOpenGL.QGLFormat.defaultFormat()
			f.setSampleBuffers(True)
			QtOpenGL.QGLFormat.setDefaultFormat(f)

			self._timer.start((1./30)*1000) # TODO: rate
			self._app.exec_()

		def quit(self, *args, **kwargs):
			self._timer.stop()
			self._app.quit()

	return {
		'GUI':Gui(),
		}



if __name__ == '__main__':

	from snap import *

	w = gui.pyside4.Window(Container())

	gui.pyside4.start()

