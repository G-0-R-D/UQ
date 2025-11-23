

def build(ENV):

	Qt5 = ENV.Qt5 # from lib.extern
	QEvent = Qt5.QEvent

	# https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html
	Qt = Qt5.Qt # for keys

	SnapGuiWindowBase = ENV.SnapGuiWindowBase
	SnapGuiBase = ENV.SnapGuiBase

	ENGINE = getattr(ENV, 'ENGINE', None) # TODO make this a function call instead, with internal logic hidden, can check for engine in multiple places...
	#TIMERS = getattr(ENV, 'SNAP_TIMERS', None)
	#snap_incoming = ENV.snap_incoming
	debug_gui = snap_debug = ENV.snap_debug # TODO put all the gui stuff into a gui module?
	snap_warning = ENV.snap_warning
	snap_out = ENV.snap_out
	snap_error = ENV.snap_error
	snap_test_out = ENV.snap_test_out

	snap_listen = ENV.snap_listen
	snap_ignore = ENV.snap_ignore
	snap_start_mainloop = ENV.snap_start_mainloop
	snap_stop_mainloop = ENV.snap_stop_mainloop
	SNAP_CH_REFRESH = ENV.SNAP_CH_REFRESH
	SNAP_CH_QUIT = ENV.SNAP_CH_QUIT
	snap_refresh_rate = ENV.snap_refresh_rate
	snap_emit = ENV.snap_emit

	SnapWeakref = ENV.SnapWeakref


	# mappings from qt codes to own codes (might be the same)
	KEYBOARD_MAP = {}
	POINTER_MAP = {}

	DEVICES = getattr(ENV, 'SNAP_DEVICES', None)
	if DEVICES:
		DEFAULT_POINTER = DEVICES.pointer()
		DEFAULT_KEYBOARD = DEVICES.keyboard()

		BUTTONS = DEFAULT_POINTER.find("BUTTONS")
		POINTER_MAP.update({
			# https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html#PySide2.QtCore.PySide2.QtCore.Qt.MouseButton
			Qt.LeftButton:BUTTONS.find("LEFT"),
			Qt.MiddleButton:BUTTONS.find("MIDDLE"),
			Qt.RightButton:BUTTONS.find("RIGHT")
		})

		# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QKeyEvent.html#qkeyevent
		for key in dir(Qt5.Qt):
			if not key.lower().startswith('key'): continue

			# TODO get all the keys in the keyboard, check code and name

			code = getattr(Qt5.Qt, key)
			if not isinstance(code, int): continue

			print('key', key, code)

	else:
		snap_warning("no devices module for sending device events")
		DEFAULT_POINTER = DEFAULT_KEYBOARD = None




	class _EventFilterer(Qt5.QWidget):
		# just to be able to install event filter because it has to be a QWidget subclass and I don't want polymorphism.

		def eventFilter(self, SOURCE, EVENT):
			return self._window_().eventFilter(SOURCE, EVENT)

		def __init__(self, WINDOW):
			Qt5.QWidget.__init__(self)

			self._window_ = SnapWeakref(WINDOW)
			WINDOW.__qt_window__.installEventFilter(self)


	class SnapQt5Window(SnapGuiWindowBase):

		__slots__ = ['__qt_window__', '_event_filterer_']

		def render(self):
			# render means to draw / update / redraw,
			# blit means transfer the render result to the screen

			"""
			UpdateTexture(MooseTexture); # this is update() / render() call...

			# these are blit:
			SDL_RenderClear(renderer);
			SDL_RenderTexture(renderer, MooseTexture, NULL, NULL); XXX this is now SDL_RenderCopy()?
			SDL_RenderPresent(renderer);
			"""
			return SnapGuiWindowBase.render(self)

		def trigger_blit(self):
			self.__qt_window__.update() # will trigger blit on next mainloop iteration (you can call this multiple times, it only updates once)
			
			#GtkWidget* gtk_window = (GtkWidget*)snap_getattr(self, "__gtk_window__");
			#GdkWindow* window = gtk_widget_get_window(gtk_window);
			#if (window){
			#	gdk_window_invalidate_rect(window, NULL, FALSE); // window, GdkRectangle, process children
			#	gdk_window_process_updates(window, FALSE); // second argument: update children, there are none (not in gtk)
			#	//window.invalidate_rect(None, False) # can be gdk.Rectangle(*AREA)(0,0) + self.get_size()
			#	//window.process_updates(False)
			#}
			return None

		def blit(self):
			"""
			# stackoverflow.com/questions/113600009/how-can-access-to-pixel-data-with-pyqt-qimage-scanline

			from PyQt4 import QtGui, QtCore
			img = QtGui.QImage(200, 100, QtGui.QImage.Format_ARGB32)
			img.fill(0xdeadbeef)

			ptr = img.bits()
			ptr.setsize(img.byteCount())

			## copy the data out as a string
			strData = ptr.asstring()

			## get a read-only buffer to access the data
			buf = buffer(ptr, 0, img.byteCount())

			## view the data as a read-only numpy array
			import numpy
			arr = numpy.frombuffer(buf, dtype=numpy.ubyte).reshape(img.height(), img.width(), 4)

			## view the data as a writable numpy array
			arr = numpy.asarray(ptr).reshape(img.height(), img.width(), 4)
			"""

			#ENGINE = self._engine_ # from SnapContainer
			blit_texture = self._blit_texture_
			window = self.__qt_window__
			if not (ENGINE and window):
				# the window might just not be ready yet
				return False

			if 0:
				pass
			elif ENGINE.name() == 'CAIRO':
				# assume cairo?

				#cairo_t* cr = gdk_cairo_create(gtk_widget_get_window(gtk_window));

				#snap_event(&ENGINE, "BLIT_GUI_WINDOW", "window", *self, "blit_texture", blit_texture, "context", cr);

				#cairo_destroy(cr);

				'get the pixels from the SDL context and then pass them to the engine to process?' # TODO

			elif ENGINE.name() == 'QT5':
				# TODO
				snap_warning("Qt5 blit not handled in gui yet; nothing shown on screen")

			else:
				snap_warning('unsupported engine:', repr(ENGINE.name()))
				
		
			return True

		def close(self):
			# TODO forward event to user to possibly reject?
			return True

		def allocate(self, extents=None, **SETTINGS):
			# ?
			return SnapGuiWindowBase.allocate(self, extents=extents, **SETTINGS)

		def show(self):
			self.set(visible=True)

		def hide(self):
			self.set(visible=False)

		# TODO minimize(); maximize()

		def is_fullscreen(self):
			''

		def fullscreen(self):
			self.set(fullscreen = not self.is_fullscreen())

		def move(self, x=None, y=None):
			#gtk_window_move(GtkWindow* gtk_window, gint x, gint y);
			return self.__qt_window__.move(int(x or 0), int(y or 0))

		def resize(self, width=None, height=None):
			#gtk_window_resize(GtkWindow* gtk_window, gint width, gint height);
			return self.__qt_window__.resize(int(width or 0), int(height or 0))

		def set(self, **SETTINGS):

			for attr,value in SETTINGS.items():

				if attr == 'fullscreen':
					'' # TODO
				elif attr == 'visible':
					'' # TODO
				elif attr == 'cursor':
					'' # TODO
				else:
					SnapGuiWindowBase.set(self, **{attr:value})



		def eventFilter(self, SOURCE, EVENT):

			# https://doc.qt.io/qt-5/qobject.html#installEventFilter

			window = self.__qt_window__

			#print(SOURCE, EVENT)
			#snap_out("event filter", SOURCE == window, EVENT.type())

			if SOURCE is not window:
				return False

			etype = EVENT.type()

			# https://doc.qt.io/qtforpython-5/PySide2/QtCore/QEvent.html

			#QEvent.None
			#QEvent.ActionAdded
			#QEvent.ActionChanged
			#QEvent.ActionRemoved
			#QEvent.ActivationChange
			#QEvent.ApplicationActivate
			#QEvent.ApplicationActivated
			#QEvent.ApplicationDeactivate
			#QEvent.ApplicationFontChange
			#QEvent.ApplicationLayoutDirectionChange
			#QEvent.ApplicationPaletteChange
			#QEvent.ApplicationStateChange
			#QEvent.ApplicationWindowIconChange
			#QEvent.ChildAdded
			#QEvent.ChildPolished
			#QEvent.ChildRemoved
			
			if etype == QEvent.Clipboard:
				snap_warning("clipboard event unhandled")

			elif etype == QEvent.Close:
				self._event_filterer_._window_ = None
				self._event_filterer_ = None
				snap_emit(SNAP_CH_QUIT, "QUIT") # XXX TODO only if no windows left!  TODO this should just emit close/quit to gui

			elif etype == QEvent.DragEnter:
				# The cursor enters a widget during a drag and drop operation ( QDragEnterEvent ).
				snap_warning("drag enter unhandled")

			elif etype == QEvent.DragLeave:
				# The cursor leaves a widget during a drag and drop operation ( QDragLeaveEvent ).
				snap_warning("drag leave unhandled")

			elif etype == QEvent.DragMove:
				# A drag and drop operation is in progress ( QDragMoveEvent ).
				snap_warning("drag move unhandled")

			elif etype == QEvent.Drop:
				# A drag and drop operation is completed ( QDropEvent ).
				snap_warning("drop event unhandled")

			#QEvent.CloseSoftwareInputPanel
			#QEvent.ContentsRectChange
			#QEvent.ContextMenu
			#QEvent.CursorChange
			#QEvent.DeferredDelete
			#QEvent.DynamicPropertyChange
			#QEvent.EnabledChange

			elif etype == QEvent.Enter:
				snap_warning("mouse enter")
				# TODO
				"""
				gboolean snap_gtk_event_enter_notify_event(
					GtkWidget *widget,
					GdkEvent *event,
					gpointer user_data
					){

					// XXX this should be handled in callback from devices, but right now gui determines proximity without updating position

					double time = snap_time();

					SnapNode pointer = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "pointers");
					SnapNode pointers = (SnapNode)snap_getattr_at(&pointer, "category", IDX_SnapDevice_category);

					SnapNode position = (SnapNode)snap_event(&pointer, "GET_BY_NAME", "POSITION");

					SnapNode buttons = (SnapNode)snap_event(&pointer, "GET_BY_NAME", "BUTTONS");
					SnapList buttons_list = (SnapList)snap_getattr_at(&buttons, "children", IDX_SnapDeviceNode_children);
					{for_item_in_SnapList(&buttons_list)
						// XXX HACK if mouse button is released while outside window, release is not received!
					}}

					SnapNode interact_info = (SnapNode)snap_getattr_at(&position, "interact_info", IDX_SnapDeviceNode_interact_info);
					if (!interact_info && position){
						interact_info = SnapNode_create(NULL, SnapDeviceInteractInfo_event);
						snap_setattr_SnapNode_at(&position, "interact_info", interact_info, IDX_SnapDeviceNode_interact_info);
					}

					SnapNode user = (SnapNode)snap_getattr_at((SnapNode*)&user_data, "_user_", IDX_SnapGuiWindowBase__user_);
					snap_event(&interact_info, "SET", "window", user_data, "graphic", user, "graphic_offset", NULL);

					SNAPLIST(proximity_msg,
						//"__ID__", ID,
						"EVENT", "PROXIMITY",
						"category", pointers,
						"device", pointer,
						"input", position,
						"time", &time,
						"state", "TRUE"
						);

					//_snap_event((SnapNode*)&user_data, (any)"DEVICE", &proximity_msg);
					_snap_event(&user, (any)"DEVICE", &proximity_msg);

					//snap_debug_gui("unhandled: enter notify");

					return TRUE;
				}
				"""

			#QEvent.EnterEditFocus
			#QEvent.EnterWhatsThisMode
			elif etype == QEvent.Expose:
				# Sent to a window when its on-screen contents are invalidated and need to be flushed from the backing store.
				snap_warning("unhandled expose event")
				
				window.blit()

				return True

			#QEvent.FileOpen
			elif etype == QEvent.FocusIn:
				# Widget or Window gains keyboard focus ( QFocusEvent ).
				snap_warning("keyboard focus in unhandled")

			elif etype == QEvent.FocusOut:
				snap_warning("keyboard focus out")

			elif etype == QEvent.FocusAboutToChange:
				# Widget or Window focus is about to change ( QFocusEvent )
				snap_warning("focus about to change?")

			#QEvent.FontChange
			#QEvent.Gesture
			#QEvent.GestureOverride
			#QEvent.GrabKeyboard
				#Item gains keyboard grab ( QGraphicsItem only).
			#QEvent.GrabMouse
				#Item gains mouse grab ( QGraphicsItem only).
			#QEvent.GraphicsSceneContextMenu
			#QEvent.GraphicsSceneDragEnter
			#QEvent.GraphicsSceneDragLeave
			#QEvent.GraphicsSceneDragMove
			#QEvent.GraphicsSceneDrop
			#QEvent.GraphicsSceneHelp
			#QEvent.GraphicsSceneHoverEnter
			#QEvent.GraphicsSceneHoverLeave
			#QEvent.GraphicsSceneHoverMove
			#QEvent.GraphicsSceneMouseDoubleClick
			#QEvent.GraphicsSceneMouseMove
			#QEvent.GraphicsSceneMousePress
			#QEvent.GraphicsSceneMouseRelease
			#QEvent.GraphicsSceneMove
			#QEvent.GraphicsSceneResize
			#QEvent.GraphicsSceneWheel

			elif etype == QEvent.Hide:
				snap_warning("hide")

			#QEvent.HideToParent
			
			elif etype == QEvent.HoverEnter:
				snap_warning("hover enter")

			elif etype == QEvent.HoverLeave:
				snap_warning("hover leave")

			elif etype == QEvent.HoverMove:
				snap_warning("hover move")
				
			#QEvent.IconDrag
			#QEvent.IconTextChange
			#QEvent.InputMethod
			#QEvent.InputMethodQuery
			#QEvent.KeyboardLayoutChange

			elif etype == QEvent.KeyPress:
				print('key press', EVENT.key())
				if EVENT.key() == Qt.Key_Q:
					''

				"""
				int code = (int)E->hardware_keycode;

				SnapNode keyboard = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "keyboards");
				snap_event(&keyboard, "GENERATE_EVENT", "EVENT", "RELEASE", "code", &code);//, "keyval", &E->keyval);
				"""

			elif etype == QEvent.KeyRelease:
				print('key press', EVENT.key())
				"""
				int code = (int)E->hardware_keycode;

				SnapNode keyboard = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "keyboards");
				snap_event(&keyboard, "GENERATE_EVENT", "EVENT", "RELEASE", "code", &code);//, "keyval", &E->keyval);
				"""

			#QEvent.LanguageChange
			#QEvent.LayoutDirectionChange
			#QEvent.LayoutRequest

			elif etype == QEvent.Leave:
				snap_warning("mouse leave")

				"""

				// XXX this is a temporary hack until pointer device is read by snap

				double time = snap_time();

				SnapNode pointer = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "pointers");
				SnapNode pointers = (SnapNode)snap_getattr_at(&pointer, "category", IDX_SnapDevice_category);

				SnapNode position = (SnapNode)snap_event(&pointer, "GET_BY_NAME", "POSITION");

				SnapNode interact_info = (SnapNode)snap_getattr_at(&position, "interact_info", IDX_SnapDeviceNode_interact_info);
				SnapNode interact_window = (SnapNode)snap_getattr_at(&interact_info, "window", IDX_SnapDeviceInteractInfo_window);
				SnapNode interact_graphic = (SnapNode)snap_getattr_at(&interact_info, "graphic", IDX_SnapDeviceInteractInfo_graphic);

				snap_event(&interact_info, "SET", "window", NULL, "graphic", NULL, "graphic_offset", NULL);

				SNAPLIST(proximity_msg,
					//"__ID__", ID,
					"EVENT", "PROXIMITY",
					"category", pointers,
					"device", pointer,
					"input", position,
					// sources, SNAPLIST(x,y)?
					"time", &time,
					"state", "FALSE"
					);

				if (interact_graphic &&
					(any)interact_graphic != snap_getattr_at((SnapNode*)&user_data, "_user_", IDX_SnapGuiWindowBase__user_)){
					_snap_event(&interact_graphic, (any)"DEVICE", &proximity_msg);
				}
				if (interact_window){
					if (interact_window != user_data){
						snap_warning("proximity leave on another window!");
					}
					SnapNode user = (SnapNode)snap_getattr_at(&interact_window, "_user_", IDX_SnapGuiWindowBase__user_);
					//_snap_event(&interact_window, (any)"DEVICE", &proximity_msg);
					_snap_event(&user, (any)"DEVICE", &proximity_msg);
				}
				"""
				
			#QEvent.LeaveEditFocus
			#QEvent.LeaveWhatsThisMode
			#QEvent.LocaleChange

			elif etype == QEvent.NonClientAreaMouseButtonDblClick:
				snap_warning("double click outside window")

			elif etype == QEvent.NonClientAreaMouseButtonPress:
				snap_warning("mouse press outside window")

			elif etype == QEvent.NonClientAreaMouseButtonRelease:
				snap_warning("mouse release outside window")

			elif etype == QEvent.NonClientAreaMouseMove:
				snap_warning("mouse move outside window")
				

			#QEvent.MacSizeChange
			#QEvent.MetaCall
			#QEvent.ModifiedChange

			#elif etype == QEvent.MouseButtonDblClick:
				#print('double click', SOURCE == window, EVENT.button())

			elif etype in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):

				# NOTE: to just interpret any double click+ as a double click, just say count > 0 and count % 2 == 0
				# TODO add double click as a property of the click for the user to easily check

				if DEFAULT_POINTER:
					button = POINTER_MAP.get(EVENT.button())
					if button:
						#print('mouse press', button.name(), button.code(), EVENT.button())#, dir(EVENT))
						DEFAULT_POINTER.generate_event('PRESS', code=button.code())
				else:
					snap_debug("no pointer for press event", EVENT.button())

			elif etype == QEvent.MouseButtonRelease:

				if DEFAULT_POINTER:
					button = POINTER_MAP.get(EVENT.button())
					if button:
						#print('mouse release', button.name(), button.code(), EVENT.button())#, dir(EVENT))
						DEFAULT_POINTER.generate_event('RELEASE', code=button.code())
				else:
					snap_debug("no pointer for release event", EVENT.button())

			elif etype == QEvent.MouseMove:
				''#print('mouse moved', EVENT.pos())

				"""
				GdkEventMotion* E = (GdkEventMotion*)event;

				gdouble pressure = 0;

				gdk_event_get_axis(event, GDK_AXIS_PRESSURE, &pressure);

				//double ext[] = {0.,0.,0., 0.,0.,0.};
				//snap_event((SnapNode*)&user_data, "GET", "gui_extents", ext); // TODO gui_extents is with matrix origin
				// TODO snap_out("motion gui extents");
				//snap_extents_print(ext);
				double* mat = (double*)snap_getattr_at((SnapNode*)&user_data, "_matrix_", IDX_SnapMatrix__matrix_);
				if (!mat){
					snap_warning("no matrix on gui window?");
					return TRUE;
				}

				double global_position[] = {E->x + mat[3], E->y + mat[7]};

				SnapNode pointer = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "pointers");
				snap_event(&pointer, "GENERATE_EVENT", "EVENT", "PRESSURE", "pressure", &pressure); // update pressure first separately
				snap_event(&pointer, "GENERATE_EVENT", "EVENT", "MOTION", "global_position", global_position);

				return TRUE;
				"""

			#QEvent.MouseTrackingChange
				
			elif etype == QEvent.Move:
				snap_warning("window moved")
				

			#QEvent.NativeGesture
			#QEvent.OrientationChange

			elif etype == QEvent.Paint:
				# TODO this is the draw/render call? XXX this would just mean blit?  the render is set to the fps timer...  this would be same as expose?
				snap_warning("paint event")

			#QEvent.PaletteChange
			#QEvent.ParentAboutToChange
			#QEvent.ParentChange
			#QEvent.PlatformPanel
			#QEvent.PlatformSurface
			#QEvent.Polish
			#QEvent.PolishRequest
			#QEvent.QueryWhatsThis
			#QEvent.ReadOnlyChange
			#QEvent.RequestSoftwareInputPanel

			elif etype == QEvent.Resize:
				snap_warning("window resize")
				
			#QEvent.ScrollPrepare
			elif etype == QEvent.Scroll:
				snap_warning("scroll?") # this is window scroll which won't be used

				"""
				// these settings indicate invalid entries
					double direction[3] = {0,0,0}; // TODO use full vector?  for now just using y for wheel...

					/*struct GdkEventScroll {
						GdkEventType type;
						GdkWindow *window;
						gint8 send_event;
						guint32 time;
						gdouble x;
						gdouble y;
						guint state;
						GdkScrollDirection direction;
						GdkDevice *device;
						gdouble x_root, y_root;
					};
					*/

					switch (E->direction){
						case GDK_SCROLL_UP:
							direction[1] = 1;
							break;
						case GDK_SCROLL_DOWN:
							direction[1] = -1;
							break;
						case GDK_SCROLL_RIGHT:
							direction[0] = 1;
							break;
						case GDK_SCROLL_LEFT:
							direction[0] = -1;
							break;

						//case GDK_SCROLL_SMOOTH: // window event?
						//	snap_warning("GDK_SCROLL_SMOOTH recieved as mouse event??");
						//	break;
					}

					//snap_out("scroll direction (%.2lf, %.2lf, %.2lf)", direction[0], direction[1], direction[2]);

					SnapNode pointer = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "pointers");
					snap_event(&pointer, "GENERATE_EVENT", "EVENT", "SCROLL", "direction", &direction[1]);
				"""

			#QEvent.Shortcut
			#QEvent.ShortcutOverride
				
			elif etype == QEvent.Show:
				snap_warning("show")
				
			#QEvent.ShowToParent
			#QEvent.SockAct
			#QEvent.StateMachineSignal
			#QEvent.StateMachineWrapped
			#QEvent.StatusTip
			#QEvent.StyleChange

			elif etype == QEvent.TabletMove:
				snap_warning("tablet move")
				
			elif etype == QEvent.TabletPress:
				snap_warning('tablet press')
				
			elif etype == QEvent.TabletRelease:
				snap_warning("tablet release")
				
			elif etype == QEvent.TabletEnterProximity:
				snap_warning('tablet enter proximity')
			
			elif etype == QEvent.TabletLeaveProximity:
				snap_warning("tablet leave proximity")
				
			#QEvent.TabletTrackingChange
				
			#QEvent.ThreadChange
				
			elif etype == QEvent.Timer:
				snap_warning("timeout")
				
			#QEvent.ToolBarChange
			#QEvent.ToolTip
			#QEvent.ToolTipChange
			
			elif etype == QEvent.TouchBegin:
				snap_warning("touch begin")
				

			elif etype == QEvent.TouchCancel:
				snap_warning('touch cancel')

			elif etype == QEvent.TouchEnd:
				snap_warning("touch end")
				
			elif etype == QEvent.TouchUpdate:
				snap_warning("touch update")
				
			elif etype == QEvent.UngrabKeyboard:
				snap_warning("ungrab keyboard")
				
			elif etype == QEvent.UngrabMouse:
				snap_warning("ungrab mouse")
				

			#QEvent.UpdateLater
			#QEvent.UpdateRequest
			#QEvent.WhatsThis
			#QEvent.WhatsThisClicked

			elif etype == QEvent.Wheel:
				''#print('scroll', EVENT.angleDelta())
				
			#QEvent.WinEventAct
			#QEvent.WindowActivate
			#QEvent.WindowBlocked
			#QEvent.WindowDeactivate
			#QEvent.WindowIconChange

			elif etype == QEvent.WindowStateChange:
				# The window's state (minimized, maximized or full-screen) has changed ( QWindowStateChangeEvent ).
				snap_warning('window state changed')

			#QEvent.WindowTitleChange
			#QEvent.WindowUnblocked
			#QEvent.WinIdChange
			#QEvent.ZOrderChange		

			return False # unhandled

		def trigger_blitXXX(self):

			window = getattr(self, '__qt_window__', None)
			if window:
				window.update()

		def blitXXX(self):
			"""
			SnapNode ENGINE = (SnapNode)snap_getattr_at(self, "ENGINE", IDX_SnapContainer_ENGINE);
			SnapNode blit_texture = (SnapNode)snap_getattr_at(self, "_blit_texture_", IDX_SnapGuiWindowBase__blit_texture_);
			GtkWidget* gtk_window = (GtkWidget*)snap_getattr_at(self, "__gtk_window__", -1);
			if (!(ENGINE && gtk_window)){
				//snap_warning("gtk BLIT is missing data");
				return (any)"ERROR";
			}

			#if defined __GTK_CAN_USE_OPENGL__
			if (snap_getattr_at(&ENGINE, "name", -1) == (any)"OPENGL"){

				// opengl

				GdkGLContext* gl_context = gtk_widget_get_gl_context(gtk_window);
				GdkGLDrawable* gl_drawable = gtk_widget_get_gl_drawable(gtk_window);

				if (!gdk_gl_drawable_gl_begin(gl_drawable, gl_context)){
					g_assert_not_reached();
				}

				snap_out("BLIT OPENGL CALL");

				snap_event(&ENGINE, "BLIT_GUI_WINDOW", "window", *self, "blit_texture", blit_texture);

				gdk_gl_drawable_gl_end(gl_drawable);
				
			}
			#else
			if (0){
			}
			#endif
			else {
				// assume cairo

				cairo_t* cr = gdk_cairo_create(gtk_widget_get_window(gtk_window));

				snap_event(&ENGINE, "BLIT_GUI_WINDOW", "window", *self, "blit_texture", blit_texture, "context", cr);

				cairo_destroy(cr);
			}
		
			return NULL;
			"""



		def set(self, **SETTINGS):

			for attr,value in SETTINGS.items():

				if attr == 'fullscreen':
					snap_warning('TODO', attr) # TODO

				elif attr == 'visible':
					snap_warning("TODO", attr) # show/hide of self.__qt_window__ TODO

				elif attr == 'cursor':
					snap_warning("TODO", attr)

				else:
					SnapGuiWindowBase.set(self, **{attr:value})

		def allocate(self, **SETTINGS):
			# TODO forward to user
			"""
			double* ext = (double*)snap_getattr(MSG, "extents");
			if (ext){
				// TODO snap_warning("gui window crop not implemented");
				// if extents changed, assign extents in gtk_window
				// XXX TODO this just sets the gui window extents which triggers an event that then sends a crop to the user!
			}
			return SnapGuiWindowBase_event(self, EVENT, MSG);
			"""


		def show(self):
			self.set(visible=True)

		def hide(self):
			self.set(visible=False)

		def move(self, x=0, y=0):
			'' # TODO

		def resize(self, *args, **SETTINGS):
			'' # either 'w', 'width', or args[0]... TODO


		def __init__(self, *args, **kwargs):
			SnapGuiWindowBase.__init__(self, *args, **kwargs)

			window = self.__qt_window__ = Qt5.QWidget()

			self._event_filterer_ = _EventFilterer(self)
			window.setMouseTracking(True)

			window.show()


		def __del__(self):
			pass



	class SnapQt5(SnapGuiBase):

		__slots__ = ['_timer_']

		#_app = Qt5.QApplication([])

		@snap_incoming
		def REFRESH(self, SOURCE, *args, **kwargs):
			return None

			try:
				devices = ENV.devices() # TODO snap_devices?
				pointer = devices.pointer()
				keyboard = devices.keyboard()
			except:
				pointer = keyboard = devices = None

		@snap_incoming
		def QUIT(self, SOURCE, *args, **kwargs):
			self.stop_mainloop()


		def screen_size(self):
			SCREEN = Qt5.QDesktopWidget().screenGeometry()
			return SCREEN.width(), SCREEN.height()

		def set_transparent(self):
			"""
			palette = WIDGET.palette()
			palette.setBrush(QtGui.QPalette.Base, QtCore.Qt.transparent)
			WIDGET.setPalette(palette)
			WIDGET.setAttribute(QtCore.Qt.WA_TranslucentBackground)
			"""


		def start_mainloop(self, **SETTINGS):
			# blocking mainloop (TODO make blocking optional?)

			#snap_debug_gui("mainloop started @ {} or {}/sec".format(SNAP_REFRESH_RATE, 1/SNAP_REFRESH_RATE))
			snap_debug("mainloop started @ {} or {}/sec".format(snap_refresh_rate(), 1/snap_refresh_rate()))

			#ENV = self.ENV()
			snap_listen(SNAP_CH_REFRESH, self)
			snap_listen(SNAP_CH_QUIT, self)
			#print('listened to', SNAP_CH_REFRESH)
			#return snap_start_mainloop(**SETTINGS)
			self._timer_.start(int(snap_refresh_rate()*1000)) # TODO: rate
			Qt5._app_.exec()

		def stop_mainloop(self):
			#snap_stop_mainloop()
			snap_ignore(SNAP_CH_REFRESH, self)
			snap_ignore(SNAP_CH_QUIT, self)
			self._timer_.stop()
			Qt5._app_.quit()
			self._open_windows_ = []
			snap_debug("app quit")

		def _refresh_callback(self, *args, **kwargs):
			snap_emit(SNAP_CH_REFRESH, "REFRESH")

		def __init__(self, *args, **kwargs):
			SnapGuiBase.__init__(self, *args, **kwargs)

			

			self._window_ = SnapQt5Window

			self._timer_ = Qt5.QTimer()
			self._timer_.timeout.connect(self._refresh_callback)

			#Qt5.QApplication.instance().installEventFilter(self) # TODO

			# https://www.geeksforgeeks.org/sdl-library-in-c-c-with-examples/

			if not 0:#SDL_WasInit(SDL_INIT_EVERYTHING): #if SNAP_SDL_NEEDS_INIT[0]:
				#SNAP_SDL_NEEDS_INIT[0] = False

				snap_debug('init QT5')

				#if SDL_Init(SDL_INIT_EVERYTHING) != 0:
				#	raise Exception('unable to initialize SDL', SDL_GetError())

				#SnapSDL_init_default_keyboard(self)

				#print('drop event enabled?', SDL_EventState(SDL_DROPFILE, SDL_QUERY) == SDL_ENABLE)
				#SDL_EventState(SDL_DROPFILE, SDL_DISABLE)
				#SDL_EventState(SDL_DROPTEXT, SDL_DISABLE)

				#state = SDL_GetModState()
				#if KMOD_CAPS & state:
				#	'init capslock to on' # TODO
				#	snap_test_out(KMOD_CAPS & state)

			
		def __del__(self):
			pass

			#SDL_Quit()

			# needs init again?


	ENV.SnapQt5 = SnapQt5



if __name__ == '__main__':

	from snap.lib.core import SNAP_GLOBAL_ENV as ENV
	from snap.lib import extern, graphics
	from snap.lib.os import devices
	from snap.lib.gui import SnapGuiBase
	extern.build(ENV)
	graphics.build(ENV)
	devices.build(ENV)
	SnapGuiBase.build(ENV)
	build(ENV)

	gui = ENV.SnapQt5()
	window = gui.Window()

	gui.start_mainloop()


	
