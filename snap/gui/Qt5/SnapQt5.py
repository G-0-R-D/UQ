
from weakref import ref as weakref_ref

import sys, time

def build(ENV):

	Qt5 = ENV.extern.Qt5 # from lib.extern
	QEvent = Qt5.QEvent

	# https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html
	Qt = Qt5.Qt # for keys

	SnapGuiWindowBase = ENV.SnapGuiWindowBase
	SnapGuiBase = ENV.SnapGuiBase

	SnapMessage = ENV.SnapMessage

	# TODO load the preferred engine of gui if not loaded...
	assert getattr(ENV, 'GUI_GRAPHICS', None) is None, 'gui graphics already loaded?'
	ENV.GUI_GRAPHICS = ENV.graphics.load('QT5')

	snap_extents_t = ENV.snap_extents_t

	snap_device_event = ENV.snap_device_event

	LOCAL_KEYMAP = {} # QtValue:{None:snapkey, scancode:snapkey, ...}

	KEYBOARD = ENV.DEVICES['keyboard']
	for name, entry in ENV.SnapDeviceKeyboard.KEYMAP.items():
		key = KEYBOARD.get('keys', name)
		assert key is not None, 'no key? {}'.format(repr(name))
		qkey = getattr(Qt, entry['Qt'])

		d = LOCAL_KEYMAP.get(qkey, {})
		scan = entry.get('scan') # can be None, default
		d[scan] = key
		LOCAL_KEYMAP[qkey] = d


	class _EventFilterer(Qt5.QWidget):
		# just to be able to install event filter because it has to be a QWidget subclass and I don't want polymorphism.

		def eventFilter(self, SOURCE, EVENT):
			return self._window_().eventFilter(SOURCE, EVENT)

		def __init__(self, WINDOW):
			Qt5.QWidget.__init__(self)

			self._window_ = weakref_ref(WINDOW)
			WINDOW['__qt_window__'].installEventFilter(self)


	class SnapQt5Window(SnapGuiWindowBase):

		__slots__ = []

		#__slots__ = ['__qt_window__', '_event_filterer_']

		"""
		def __snap_inputs__(self):
			return {
				'TRIGGER_BLIT':SnapEvent(),
				'BLIT':SnapEvent(),
				'ALLOCATE':SnapEvent(),
				'SHOW':SnapEvent(),
				'HIDE':SnapEvent(),
				'is_fullscreen':SnapProperty(),
				'FULLSCREEN':SnapEvent(),
				'MOVE':SnapEvent(),
				'RESIZE':SnapEvent(),
				'CLOSE':SnapEvent(),
			}
		"""


		"""
		if CHANNEL == 'TRIGGER_BLIT':
			''

		elif CHANNEL == 'BLIT':
			'' # transfer to the image representing the render result...

		elif CHANNEL == 'ALLOCATE':
			''

		elif CHANNEL == 'SHOW':
			'self.set(visible=True)'

		elif CHANNEL == 'HIDE':
			'self.set(visible=False)'

		elif CHANNEL == 'is_fullscreen':
			''

		elif CHANNEL == 'FULLSCREEN':
			'toggle fullscreen mode, or set to given value?'

		elif CHANNEL == 'MOVE':
			'move the window'

		elif CHANNEL == 'RESIZE':
			'resize the window (call ALLOCATE?)'

		elif CHANNEL == 'CLOSE':
			''
		"""

		@ENV.SnapProperty
		class extents:
			# XXX make this just go to assign of gui window, bypass this
			# XXX implement this, then forward to superclass for assign and user forward!

			def get(self, MSG):
				"()->snap_extents_t"
				qwindow = self['__qt_window__']
				if qwindow:
					geo = qwindow.geometry()
					#return snap_extents_t(geo.x(), geo.y(), 0, geo.x() + geo.width(), geo.y() + geo.height(), 1)
					return snap_extents_t(0,0,0, geo.width(),geo.height(),1)
				else:
					ENV.snap_debug('no qt window for extents')
					return None # snap_extents_t(0,0,0, 1,1,1)

			def set(self, MSG):
				"(snap_extents_t!)"
				ext = MSG.args[0]
				qwindow = self['__qt_window__']
				if qwindow is None:
					return

				# and this should trigger resize event which then goes to user...
				if ext is None:
					qwindow.setSize(1,1)
				else:
					qwindow.setGeometry(int(ext[0]),int(ext[1]), int(ext[3]-ext[0]), int(ext[4]-ext[1]))

				# TODO only use extents for this?
				#ENV.snap_out('set window ext', ext[:])
				#return SnapGuiWindowBase.extents.set(self, SnapMessage(ext))


		def eventFilter(self, SOURCE, EVENT):
			
			# https://doc.qt.io/qt-5/qobject.html#installEventFilter

			window = self['__qt_window__']

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
				ENV.snap_warning("clipboard event unhandled")

			elif etype == QEvent.Close:
				self['__event_filterer__']._window_ = None
				self['__event_filterer__'] = None
				#snap_emit(SNAP_CH_QUIT, "QUIT") # XXX TODO only if no windows left!  TODO this should just emit close/quit to gui
				#ENV.snap_out("close event")

			elif etype == QEvent.DragEnter:
				# The cursor enters a widget during a drag and drop operation ( QDragEnterEvent ).
				ENV.snap_warning("drag enter unhandled")

			elif etype == QEvent.DragLeave:
				# The cursor leaves a widget during a drag and drop operation ( QDragLeaveEvent ).
				ENV.snap_warning("drag leave unhandled")

			elif etype == QEvent.DragMove:
				# A drag and drop operation is in progress ( QDragMoveEvent ).
				ENV.snap_warning("drag move unhandled")

			elif etype == QEvent.Drop:
				# A drag and drop operation is completed ( QDropEvent ).
				ENV.snap_warning("drop event unhandled")

			#QEvent.CloseSoftwareInputPanel
			#QEvent.ContentsRectChange
			#QEvent.ContextMenu
			#QEvent.CursorChange
			#QEvent.DeferredDelete
			#QEvent.DynamicPropertyChange
			#QEvent.EnabledChange

			elif etype == QEvent.Enter:
				#ENV.snap_warning("mouse enter")
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
				#ENV.snap_warning("unhandled expose event")
				
				#window.blit()
				self.blit()

				return True

			#QEvent.FileOpen
			elif etype == QEvent.FocusIn:
				# Widget or Window gains keyboard focus ( QFocusEvent ).
				ENV.snap_warning("keyboard focus in unhandled")

			elif etype == QEvent.FocusOut:
				ENV.snap_warning("keyboard focus out")

			elif etype == QEvent.FocusAboutToChange:
				# Widget or Window focus is about to change ( QFocusEvent )
				ENV.snap_warning("focus about to change?")

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
				ENV.snap_warning("hide")

			#QEvent.HideToParent
			
			elif etype == QEvent.HoverEnter:
				ENV.snap_warning("hover enter")

			elif etype == QEvent.HoverLeave:
				ENV.snap_warning("hover leave")

			elif etype == QEvent.HoverMove:
				ENV.snap_warning("hover move")
				
			#QEvent.IconDrag
			#QEvent.IconTextChange
			#QEvent.InputMethod
			#QEvent.InputMethodQuery
			#QEvent.KeyboardLayoutChange

			elif etype == QEvent.KeyPress:
				#ENV.snap_debug('key press', EVENT.key())
				if EVENT.key() == Qt.Key_Q:
					''
				if not EVENT.isAutoRepeat():

					scan_lookup = LOCAL_KEYMAP.get(EVENT.key(), {})
					snap_key = scan_lookup.get(EVENT.nativeScanCode(), scan_lookup.get(None))


					if snap_key is None:
						ENV.snap_debug('missing key?', EVENT.key(), dir(EVENT))
					else:
						#ENV.snap_debug('found key', snap_key, EVENT.nativeScanCode())
						if snap_key['value'] > 0:
							ENV.snap_debug('key already pressed?', snap_key)
						else:
							snap_key['value'] = 1.0
					

					text = EVENT.text()
					if text:
						encoding = 'UTF8' # TODO ?
						snap_device_event(KEYBOARD, SnapMessage(action='text_input', value=text, encoding=encoding, time=time.time(), device=KEYBOARD, source=snap_key))
						

				#print(dir(EVENT), EVENT.key())

				# TODO make a map from qt key codes to the ones that we have...

				#keyboard = ENV.DEVICES['keyboard']
				#print(dir(EVENT))
				#print('key', EVENT.nativeScanCode(), EVENT.nativeVirtualKey())
				#print('get', ENV.SNAP_KEYMAP.snap_keycode_to_name(EVENT.key()), ENV.SNAP_KEYMAP.snap_scancode_to_name(EVENT.nativeVirtualKey()))

				"""
				int code = (int)E->hardware_keycode;

				SnapNode keyboard = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "keyboards");
				snap_event(&keyboard, "GENERATE_EVENT", "EVENT", "RELEASE", "code", &code);//, "keyval", &E->keyval);
				"""

			elif etype == QEvent.KeyRelease:
				#ENV.snap_debug('key release', EVENT.key())

				if not EVENT.isAutoRepeat():
					scan_lookup = LOCAL_KEYMAP.get(EVENT.key(), {})
					snap_key = scan_lookup.get(EVENT.nativeScanCode(), scan_lookup.get(None))

					if snap_key is None:
						ENV.snap_debug('missing key?', EVENT.key())
					else:
						if snap_key['value'] == 0.:
							ENV.snap_debug('key already released?', snap_key)
						else:
							snap_key['value'] = 0.

				"""
				int code = (int)E->hardware_keycode;

				SnapNode keyboard = SnapGuiWindowBase_get_default_device((SnapNode*)&user_data, "keyboards");
				snap_event(&keyboard, "GENERATE_EVENT", "EVENT", "RELEASE", "code", &code);//, "keyval", &E->keyval);
				"""

			#QEvent.LanguageChange
			#QEvent.LayoutDirectionChange
			#QEvent.LayoutRequest

			elif etype == QEvent.Leave:
				#ENV.snap_warning("mouse leave")

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
				ENV.snap_warning("double click outside window")

			elif etype == QEvent.NonClientAreaMouseButtonPress:
				ENV.snap_warning("mouse press outside window")

			elif etype == QEvent.NonClientAreaMouseButtonRelease:
				ENV.snap_warning("mouse release outside window")

			elif etype == QEvent.NonClientAreaMouseMove:
				ENV.snap_warning("mouse move outside window")
				

			#QEvent.MacSizeChange
			#QEvent.MetaCall
			#QEvent.ModifiedChange

			#elif etype == QEvent.MouseButtonDblClick:
				#print('double click', SOURCE == window, EVENT.button())

			elif etype in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):

				# NOTE: we accept double click because it actually happens in the place of single click!  we just want 'each click'
				# NOTE: to interpret any double click+ as a double click, just say count > 0 and count % 2 == 0

				"""
				if DEFAULT_POINTER:
					button = POINTER_MAP.get(EVENT.button())
					if button:
						print('mouse press', button.name(), button.code(), EVENT.button())#, dir(EVENT))
						DEFAULT_POINTER.generate_event('PRESS', code=button.code())
				else:
					snap_debug("no pointer for press event", EVENT.button())
				"""

				pointer = ENV.DEVICES['pointer']
				button = EVENT.button()

				if pointer and button:
					if button == Qt.LeftButton:
						pointer.get('buttons', "left").press()
					elif button == Qt.MiddleButton:
						pointer.get('buttons', "middle").press()
					elif button == Qt.RightButton:
						pointer.get('buttons', "right").press()
					else:
						# TODO higher codes can be accessed by indexing BUTTONS group?  make it like a list...  and __iter__, __len__, __getitem__(int)
						ENV.snap_debug('unhandled mouse button', button)

				else:
					ENV.snap_debug("no pointer for press event", EVENT.button())

			elif etype == QEvent.MouseButtonRelease:

				"""
				if DEFAULT_POINTER:
					button = POINTER_MAP.get(EVENT.button())
					if button:
						#print('mouse release', button.name(), button.code(), EVENT.button())#, dir(EVENT))
						DEFAULT_POINTER.generate_event('RELEASE', code=button.code())
				else:
					snap_debug("no pointer for release event", EVENT.button())
				"""

				pointer = ENV.DEVICES['pointer']
				button = EVENT.button()

				if pointer and button:
					if button == Qt.LeftButton:
						pointer.get('buttons', "left").release()
					elif button == Qt.MiddleButton:
						pointer.get('buttons', "middle").release()
					elif button == Qt.RightButton:
						pointer.get('buttons', "right").release()
					else:
						# TODO higher codes can be accessed by indexing BUTTONS group?  make it like a list...  and __iter__, __len__, __getitem__(int)
						# ("LEFT", "MIDDLE", "RIGHT") are always first 3 slots...
						ENV.snap_debug('unhandled mouse button', button)

				else:
					ENV.snap_debug("no pointer for release event", EVENT.button())

			elif etype == QEvent.MouseMove:
				#pos = EVENT.pos()
				#x,y = pos.x(),pos.y()

				#print(EVENT.globalX(), EVENT.globalY())

				pointer = ENV.DEVICES['pointer']
				if pointer:
					position = pointer.get('position')
					X = position.get('x')
					Y = position.get('y')
					X['value'] = EVENT.globalX()
					Y['value'] = EVENT.globalY()
				else:
					ENV.snap_debug('unhandled mouse move', EVENT.pos())

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

				qwindow = self['__qt_window__']
				geo = qwindow.geometry()

				x,y,z = self['position']
				if x != geo.x() or y != geo.y():
					SnapGuiWindowBase.position.set(self, SnapMessage([geo.x(), geo.y(), 0]))

			#QEvent.NativeGesture
			#QEvent.OrientationChange

			elif etype == QEvent.Paint:
				# TODO this is the draw/render call? XXX this would just mean blit?  the render is set to the fps timer...  this would be same as expose?
				#ENV.snap_warning("paint event")

				self.blit()

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
				#ENV.snap_out('resize', EVENT.size().width(), EVENT.size().height())

				qwindow = self['__qt_window__']
				geo = qwindow.geometry()

				x,y,z = self['position']
				if x != geo.x() or y != geo.y():
					SnapGuiWindowBase.position.set(self, SnapMessage([geo.x(), geo.y(), 0]))

				size = EVENT.size()
				ext = snap_extents_t(0,0,0,size.width(),size.height(),1)
				SnapGuiWindowBase.extents.set(self, SnapMessage(ext))
				
			#QEvent.ScrollPrepare
			elif etype == QEvent.Scroll:
				ENV.snap_warning("scroll?") # this is window scroll which won't be used

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
				ENV.snap_warning("show")
				
			#QEvent.ShowToParent
			#QEvent.SockAct
			#QEvent.StateMachineSignal
			#QEvent.StateMachineWrapped
			#QEvent.StatusTip
			#QEvent.StyleChange


			# https://stackoverflow.com/questions/48873483/python-example-for-wacom-tablets
			elif etype == QEvent.TabletMove:
				ENV.snap_warning("tablet move")
				EVENT.accept()
				
			elif etype == QEvent.TabletPress:
				ENV.snap_warning('tablet press')
				EVENT.accept()
				
			elif etype == QEvent.TabletRelease:
				ENV.snap_warning("tablet release")
				EVENT.accept()
				
			elif etype == QEvent.TabletEnterProximity:
				ENV.snap_warning('tablet enter proximity')
				EVENT.accept()
			
			elif etype == QEvent.TabletLeaveProximity:
				ENV.snap_warning("tablet leave proximity")
				EVENT.accept()
				
			#QEvent.TabletTrackingChange
				
			#QEvent.ThreadChange
				
			elif etype == QEvent.Timer:
				ENV.snap_warning("timeout")
				
			#QEvent.ToolBarChange
			#QEvent.ToolTip
			#QEvent.ToolTipChange
			
			elif etype == QEvent.TouchBegin:
				ENV.snap_warning("touch begin")
				

			elif etype == QEvent.TouchCancel:
				ENV.snap_warning('touch cancel')

			elif etype == QEvent.TouchEnd:
				ENV.snap_warning("touch end")
				
			elif etype == QEvent.TouchUpdate:
				ENV.snap_warning("touch update")
				
			elif etype == QEvent.UngrabKeyboard:
				ENV.snap_warning("ungrab keyboard")
				
			elif etype == QEvent.UngrabMouse:
				ENV.snap_warning("ungrab mouse")
				

			#QEvent.UpdateLater
			#QEvent.UpdateRequest
			#QEvent.WhatsThis
			#QEvent.WhatsThisClicked

			elif etype == QEvent.Wheel:
				#ENV.snap_debug('scroll', EVENT.angleDelta())

				pointer = ENV.DEVICES['pointer']
				wheel = pointer.get('wheels', 0)
				
				pt = EVENT.angleDelta()
				if pt.x() > 0:
					wheel.get('x')['value'] = 1.0
				elif pt.x() < 0:
					wheel.get('x')['value'] = -1.0

				if pt.y() > 0:
					wheel.get('y')['value'] = 1.0
				elif pt.y() < 0:
					wheel.get('y')['value'] = -1.0
				
				
			#QEvent.WinEventAct
			#QEvent.WindowActivate
			#QEvent.WindowBlocked
			#QEvent.WindowDeactivate
			#QEvent.WindowIconChange

			elif etype == QEvent.WindowStateChange:
				# The window's state (minimized, maximized or full-screen) has changed ( QWindowStateChangeEvent ).
				ENV.snap_warning('window state changed')

			#QEvent.WindowTitleChange
			#QEvent.WindowUnblocked
			#QEvent.WinIdChange
			#QEvent.ZOrderChange

			return False # unhandled

		@ENV.SnapChannel
		def allocate(self, MSG):
			#ENV.snap_out('GOT allocate')

			extents = MSG.unpack('extents', None)

			#ENV.snap_out("allocate", extents)

			if not extents:
				return None

			qwindow = self['__qt_window__']

			#qwindow.move(int(extents[0]), int(extents[1]))
			#qwindow.resize(int(extents[3]-extents[0]), int(extents[4]-extents[1]))
			x1,y1,z1,x2,y2,z2 = extents
			# TODO make sure extents don't put window out of bounds...
			sw,sh = ENV.GUI['screen_size']
			if x1 > (sw-10):
				x1 -= 10
			if y1 > (sh-10):
				y1 -= 10
			if x2-x1 < 10:
				x2 = x1 + 10
			if y2-y1 < 10:
				y2 = y1 + 10
			#ENV.snap_out('allocated', int(x1), int(y1), int(x2-x1), int(y2-y1))
			qwindow.setGeometry(int(x1), int(y1), int(x2-x1), int(y2-y1))

			ext = snap_extents_t(x1,y1,0, x2,y2,0)
			return SnapGuiWindowBase.allocate(self, SnapMessage(extents=ext))

		@ENV.SnapChannel
		def trigger_blit(self, MSG):
			self['__qt_window__'].update()

		@ENV.SnapChannel
		def blit(self, MSG):
			'assign current (already rendered) buffer'
			#ENV.snap_warning('blit!') # TODO put this under EXPOSE event?

			window = self['__qt_window__']

			# TODO just keep the existing design, render on window and then this just pulls the self.data()['__texture__'] setup in self._update_blit_data()

			ptr = Qt5.QPainter(window)

			blit_texture = self['__blit_texture__']
			if blit_texture is not None:
				#ENV.snap_out('__blit_texture__ exists!')
				# TODO resize blit texture image (or reformat if changed from user size)
				#if blit_texture['__engine_data__'] is None:
				#	ENV.snap_out('texture engine data', blit_texture['__engine_data__'])

				#import os
				#if not os.path.exists('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/gui/Qt5/test_out.png'):
				#	blit_texture['__engine_data__'].save('/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/gui/Qt5/test_out.png')
				try:
					ptr.drawPixmap(window.rect(), blit_texture['__engine_data__'])
					#ptr.drawImage(window.rect(), blit_texture['image']['__engine_data__'])
				except Exception as e:
					ENV.snap_error('render error', repr(e))
					ptr.fillRect(window.rect(), Qt5.Qt.red)
			else:
				user_window = self['__user_window__']
				if user_window is not None:
					texture = user_window['texture']
					if texture is not None:
						#ENV.snap_out('draw pixmap', window.rect(), texture.__engine_data__().size())
						#user_window.render() # TODO timer...
						#import os
						#savepath = '/media/user/CRUCIAL1TB/MyComputer/PROGRAMMING/PROJECTS/UQ/snap/lib/gui_blit.png'
						#ENV.snap_out("image size", texture.image().size())
						#if not os.path.exists(savepath) and texture['image']['size'] != [1,1]:
							#texture['image']['__engine_data__'].save(savepath)
						#	texture['image'].save(savepath)

						#ENV.snap_out("display texture")

						#GFX = ENV.GUI_GRAPHICS
						#image = GFX.Image()
						#image.open('/media/user/CRUCIAL1TB/MyComputer/ARTWORK/SKETCHBOOK/REFERENCE/ANATOMY/HUMAN/Cross Sections/cosmos.phy.tufts.edu ~rwillson medgross gross.htm.jpeg')
						#texture = GFX.Texture(image=image)

						#ptr.drawPixmap(window.rect(), texture.__engine_data__())
						#ENV.snap_out("image size", texture.image().size())
						try:
							#ptr.fillRect(window.rect(), Qt5.Qt.white)
							#ptr.setRenderHint(Qt5.QPainter.Antialiasing, True)
							#ptr.setCompositionMode(Qt5.QPainter.CompositionMode_Multiply)
							ptr.drawImage(window.rect(), texture['image']['__engine_data__'])
						except Exception as e:
							ENV.snap_error('render error', repr(e))
							ptr.fillRect(window.rect(), Qt5.Qt.red)

						#ptr.fillRect(Qt5.QRect(10,10,window.width()-20, window.height()-20), Qt5.Qt.red)
						ptr.end()
						return None

				#ptr.fillRect(window.rect(), Qt5.Qt.red)

			#ptr.finish()
			ptr.end()

		def __init__(self, **SETTINGS):
			SnapGuiWindowBase.__init__(self, **SETTINGS)

			window = self['__qt_window__'] = Qt5.QWidget()
			window.setWindowTitle(sys.argv[0])#' ')

			self['__event_filterer__'] = _EventFilterer(self)
			window.setMouseTracking(True)

			# TODO cursor

			# TODO self.fullscreen = SnapProperty(self, SnapBool(False))

			#self.position = SnapProperty(self, SnapMatrix())

			window.show()

		def __delete__(self):
			return SnapGuiWindowBase.__delete__(self)

	ENV.SnapQt5Window = SnapQt5Window

	class SnapQt5(SnapGuiBase):

		__slots__ = []

		#__slots__ = ['_timer_'] # XXX can't create weak reference error if this is enabled?

		Window = SnapQt5Window

		@ENV.SnapProperty
		class name:
			def get(self, MSG):
				"()->str"
				return "QT5"

			"""
		def __snap_inputs__(self):

			return {
				'SET':SnapEvent(), # TODO
				'screen_size':SnapProperty(None, return_value='list(int, int)'),
			}
			"""

		"""
		def set(self, MSG):

			for attr,value in MSG.kwargs.items():
				if attr == 'transparent':
					'true|false' # TODO XXX shouldn't this be on gui window?
					ENV.snap_warning("not implemented, SET", attr)
		"""

		@ENV.SnapProperty
		class screen_size:
			def get(self, MSG):
				"""()->list(int,int)"""
				SCREEN = Qt5.QDesktopWidget().screenGeometry()
				return [SCREEN.width(), SCREEN.height()]


		def start_mainloop(self):
			# TODO if not ENV.MAINLOOP, make one?  TODO ENV.MAINLOOP = SnapProperty(ENV, ENV.SnapMainloop(SNAP))

			ENV.__PRIVATE__['__MAINLOOP_NODE__'].__class__.OWNED = True

			# https://doc.qt.io/qtforpython-5/PySide2/QtCore/QTimer.html#PySide2.QtCore.PySide2.QtCore.QTimer.setInterval
			# "A QTimer with a timeout interval of 0 will time out as soon as all the events ... have been processed."
			self['__timer__'].start(0)
			Qt5._app_.exec()

		def stop_mainloop(self):
			self['__timer__'].stop()
			open_windows = self.__snap_data__['__open_windows__'] or []
			del self.__snap_data__['__open_windows__']
			for window in open_windows:
				'' # TODO close event?

			# TODO send quit event to user...

			ENV.__PRIVATE__['__MAINLOOP_NODE__'].__class__.OWNED = False

			Qt5._app_.quit() # TODO send quit event to user?

		#def timeout(self, MSG):
		#	'' # ENV.MAINLOOP.next() # XXX UQ.UQ_APP.next() # on main task...
		#	return True
			
			
		def __init__(self):
			SnapGuiBase.__init__(self)

			data = self.__snap_data__

			#data['__window_type__'] = SnapQt5Window # logic is in SnapGuiBase, just requires the assign

			t = data['__timer__'] = Qt5.QTimer()
			t.setTimerType(Qt.PreciseTimer) # Qt.CoarseTimer

			ENV.mainloop # touch to create
			t.timeout.connect(ENV.__PRIVATE__['__MAINLOOP_NODE__'].next) # # return True to keep going

			#self.screen_size = SnapProperty(self, None, setters=[], getters=[SnapQt5_get_screen_size])


	ENV.SnapQt5 = SnapQt5

