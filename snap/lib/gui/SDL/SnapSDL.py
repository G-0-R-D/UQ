
#from snap.lib.extern.SDL import *
from sdl2 import *

#from snap.lib.gui.SnapGuiBase import *

# https://wiki.libsdl.org/SDL2/Tutorials
# https://wiki.libsdl.org/SDL2/APIByCategory

#SNAP_SDL_NEEDS_INIT = [True]

import ctypes

def build(ENV):

	SnapGuiWindowBase = ENV.SnapGuiWindowBase
	SnapGuiBase = ENV.SnapGuiBase

	GRAPHICS = getattr(ENV, 'GRAPHICS', None) # TODO make this a function call instead, with internal logic hidden, can check for engine in multiple places...

	debug_gui = ENV.snap_debug

	class SnapSDLWindow(SnapGuiWindowBase):

		__slots__ = ['__sdl_window__', '__sdl_renderer__']

		@ENV.SnapChannel
		def render(self, MSG):
			# render means to draw / update / redraw,
			# blit means transfer the render result to the screen

			"""
			UpdateTexture(MooseTexture); # this is update() / render() call...

			# these are blit:
			SDL_RenderClear(renderer);
			SDL_RenderTexture(renderer, MooseTexture, NULL, NULL); XXX this is now SDL_RenderCopy()?
			SDL_RenderPresent(renderer);
			"""
			return SnapGuiWindowBase.render(self, MSG)

		@ENV.SnapChannel
		def trigger_blit(self, MSG):
			sdl_window = self.__sdl_window__
			
			#GtkWidget* gtk_window = (GtkWidget*)snap_getattr(self, "__gtk_window__");
			#GdkWindow* window = gtk_widget_get_window(gtk_window);
			#if (window){
			#	gdk_window_invalidate_rect(window, NULL, FALSE); // window, GdkRectangle, process children
			#	gdk_window_process_updates(window, FALSE); // second argument: update children, there are none (not in gtk)
			#	//window.invalidate_rect(None, False) # can be gdk.Rectangle(*AREA)(0,0) + self.get_size()
			#	//window.process_updates(False)
			#}
			return None

		@ENV.SnapChannel
		def blit(self, MSG):

			# https://slouken.blogspot.com/2011/02/streaming-textures-with-sdl-13.html
			# https://github.com/libsdl-org/SDL/blob/main/test/teststreaming.c

			# https://glusoft.com/sdl2-tutorials/play-video-sdl/
			"""
			texture = SDL_CreateTexture(renderer,
						                SDL_PIXELFORMAT_ARGB8888,
						                SDL_TEXTUREACCESS_STREAMING,
						                width, height);

			surface = SDL_CreateRGBSurfaceFrom(NULL,
						                       width, height,
						                       32, 0,
						                       0x00FF0000,
						                       0x0000FF00,
						                       0x000000FF,
						                       0xFF000000);

			...
			SDL_LockTexture(texture, NULL,
						    &surface->pixels,
						    &surface->pitch);
			... draw to surface
			SDL_UnlockTexture(texture)
			"""

			#ENGINE = self._engine_ # from SnapContainer
			blit_texture = self._blit_textrue_
			sdl_window = self.__sdl_window__
			if not (GRAPHICS and sdl_window):
				return False
			"""
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
			"""
			if 0:
				pass
			elif GRAPHICS['name'] == 'CAIRO':
				# assume cairo?

				#cairo_t* cr = gdk_cairo_create(gtk_widget_get_window(gtk_window));

				#snap_event(&ENGINE, "BLIT_GUI_WINDOW", "window", *self, "blit_texture", blit_texture, "context", cr);

				#cairo_destroy(cr);

				'get the pixels from the SDL context and then pass them to the engine to process?' # TODO

			else:
				snap_warning('unsupported engine:', repr(GRAPHICS['name']))
				
		
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
			return None

		def resize(self, width=None, height=None):
			#gtk_window_resize(GtkWindow* gtk_window, gint width, gint height);
			return None

		"""
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
		"""

		def __init__(self, *args, **kwargs):
			SnapGuiWindowBase.__init__(self, *args, **kwargs)

			# https://stackoverflow.com/questions/23048993/sdl-fullscreen-translucent-background

			# https://github.com/libsdl-org/SDL/blob/main/test/teststreaming.c
			ENV.snap_out('create', (__file__, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 640, 480, SDL_WINDOW_RESIZABLE))
			window = SDL_CreateWindow(__file__.encode(), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 640, 480, SDL_WINDOW_RESIZABLE)
			if not window:
				raise Exception("Couldn't set create window:", SDL_GetError())

			renderer = SDL_CreateRenderer(window, -1, 0)
			if not renderer:
				raise Exception("unable to initialize renderer", SDL_GetError())

			# MooseTexture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, MOOSEPIC_W, MOOSEPIC_H);

			self.__sdl_renderer__ = renderer
			self.__sdl_window__ = window

			# SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
			# SDL_RenderClear(renderer)
			# SDL_RenderPresent(renderer) # to swap buffers

		def __del__(self):

			# TODO SDL_DestroyTexture(texture)

			renderer = getattr(self, "__sdl_renderer__", None)
			if renderer:
				SDL_DestroyRenderer(renderer)
				self.__sdl_renderer__ = None

			# TODO SDL_DestroyWindow(window)


	class SnapSDL(SnapGuiBase):

		__slots__ = []

		@ENV.SnapProperty
		class running:

			def get(self, MSG):
				"()->bool"
				return bool(self.__snap_data__['running'])

			def set(self, MSG):
				"(bool!)"
				value = MSG.args[0]
				self.__snap_data__['running'] = bool(value)

		@ENV.SnapChannel
		def REFRESH(self, MSG):#SOURCE, *args, **kwargs):

			try:
				devices = ENV.devices() # TODO snap_devices?
				pointer = devices.pointer()
				keyboard = devices.keyboard()
			except:
				pointer = keyboard = devices = None

			event = SDL_Event()

			while SDL_PollEvent(ctypes.byref(event)):
				# https://wiki.libsdl.org/SDL2/SDL_Event

				event_type = event.type
				#out('event.type', event_type)

				# https://www.libsdl.org/release/SDL-1.2.15/docs/html/sdlkey.html
				# https://wiki.libsdl.org/SDL2/SDL_Keysym
				if event_type == SDL_KEYDOWN:

					if keyboard:
						key = keyboard.find(event.key.scancode)

					ENV.snap_out('keydown', event.key.keysym.sym)#, snap_keyval_to_name(event.key.keysym.sym), SDL_GetKeyName(event.key.keysym.sym))
					#print(event.key.keysym.sym)#, SDLK_ESCAPE, repr(SDLK_SPACE))#, ord(SDLK_ESCAPE))
					if event.key.keysym.sym == SDLK_ESCAPE:
						ENV.snap_out("stopping from escape")
						self.stop()

				elif event_type == SDL_KEYUP:
					''

				# https://wiki.libsdl.org/SDL2/SDL_TextInputEvent
				# https://wiki.libsdl.org/SDL2/Tutorials-TextInput
				elif event_type == SDL_TEXTINPUT:
					text = event.text
					ENV.snap_out('textinput', text.text)

				elif event_type == SDL_TEXTEDITING:
					edit = event.edit
					ENV.snap_out('textediting', edit.start, edit.length, edit.text)

				# SDL_GetKeyboardState
				# 

				# https://wiki.libsdl.org/SDL2/SDL_MouseMotionEvent
				elif event_type == SDL_MOUSEMOTION:
					''#print(event.motion.x, event.motion.y, event.motion.xrel, event.motion.yrel)

				# https://wiki.libsdl.org/SDL2/SDL_MouseButtonEvent
				elif event_type == SDL_MOUSEBUTTONDOWN or event_type == SDL_MOUSEBUTTONUP:

					if 1:
						button ={SDL_BUTTON_LEFT:'SDL_BUTTON_LEFT',
							SDL_BUTTON_MIDDLE:'SDL_BUTTON_MIDDLE',
							SDL_BUTTON_RIGHT:'SDL_BUTTON_RIGHT',
							SDL_BUTTON_X1:'SDL_BUTTON_X1',
							SDL_BUTTON_X2:'SDL_BUTTON_X2'}.get(event.button.button, '?')
						print('button', button)
					#print('button', event.button)

					#print(event.button.clicks)
					#print(event.button.button)
					#print(event.button.x, event.button.y) # local window coordinates
					#print('window',event.button.windowID)
					#print('time',event.button.timestamp)

					#print('pressed', event.button.state == SDL_PRESSED)

					if event.button.which == SDL_TOUCH_MOUSEID:
						debug_gui('tablet mouse button')
						'event came from a touch source (and should likely be handled by SDL_TouchFingerEvent)'

				# https://wiki.libsdl.org/SDL2/SDL_MouseWheelEvent
				elif event_type == SDL_MOUSEWHEEL:

					direction = 1 if event.wheel.direction == SDL_MOUSEWHEEL_NORMAL else -1

					if event.wheel.x != 0:
						''#out('TODO mouse wheel x', event.wheel.x)
					if event.wheel.y != 0:
						''#out('TODO mouse wheel y', event.wheel.y)



				elif event_type == SDL_WINDOWEVENT:
					window_event = event.window.event

					continue

					if window_event == SDL_WINDOWEVENT_SHOWN:
						debug_gui("Window %d shown" % event.window.windowID)

					elif window_event == SDL_WINDOWEVENT_HIDDEN:
						debug_gui("Window %d hidden" % event.window.windowID)

					elif window_event == SDL_WINDOWEVENT_EXPOSED:
						debug_gui("Window %d exposed" % event.window.windowID)

					elif window_event == SDL_WINDOWEVENT_MOVED:
						debug_gui("Window %d moved to %d,%d" % (
								event.window.windowID, event.window.data1,
								event.window.data2))

					"""
					case SDL_WINDOWEVENT_RESIZED:
						SDL_Log("Window %d resized to %dx%d",
								event->window.windowID, event->window.data1,
								event->window.data2);
						break;
					case SDL_WINDOWEVENT_SIZE_CHANGED:
						SDL_Log("Window %d size changed to %dx%d",
								event->window.windowID, event->window.data1,
								event->window.data2);
						break;
					case SDL_WINDOWEVENT_MINIMIZED:
						SDL_Log("Window %d minimized", event->window.windowID);
						break;
					case SDL_WINDOWEVENT_MAXIMIZED:
						SDL_Log("Window %d maximized", event->window.windowID);
						break;
					case SDL_WINDOWEVENT_RESTORED:
						SDL_Log("Window %d restored", event->window.windowID);
						break;
					case SDL_WINDOWEVENT_ENTER:
						SDL_Log("Mouse entered window %d",
								event->window.windowID);
						break;
					case SDL_WINDOWEVENT_LEAVE:
						SDL_Log("Mouse left window %d", event->window.windowID);
						break;
					case SDL_WINDOWEVENT_FOCUS_GAINED:
						SDL_Log("Window %d gained keyboard focus",
								event->window.windowID);
						break;
					case SDL_WINDOWEVENT_FOCUS_LOST:
						SDL_Log("Window %d lost keyboard focus",
								event->window.windowID);
						break;
					case SDL_WINDOWEVENT_CLOSE:
						SDL_Log("Window %d closed", event->window.windowID);
						break;
					#if SDL_VERSION_ATLEAST(2, 0, 5)
					case SDL_WINDOWEVENT_TAKE_FOCUS:
						SDL_Log("Window %d is offered a focus", event->window.windowID);
						break;
					case SDL_WINDOWEVENT_HIT_TEST:
						SDL_Log("Window %d has a special hit test", event->window.windowID);
						break;
					"""

				# https://wiki.libsdl.org/SDL2/SDL_DropEvent
				elif event_type == SDL_DROPFILE:
					dropped_filedir = ctypes.cast(event.drop.file, ctypes.c_char_p)
					# Shows directory of dropped file
					SDL_ShowSimpleMessageBox(
						SDL_MESSAGEBOX_INFORMATION,
						"File dropped on window",
						dropped_filedir,
						self._open_windows_[0].__sdl_window__
						)
					# https://stackoverflow.com/questions/13445568/python-ctypes-how-to-free-memory-getting-invalid-pointer-error
					# set return value to c_void_p to prevent string conversion (and loss of original pointer)
					print(dropped_filedir.value.decode('utf8'))
					SDL_free(event.drop.file)

				elif event_type == SDL_DROPTEXT:
					if event.drop.file:
						print('drop text, free file', ctypes.cast(event.drop.file, ctypes.c_char_p).value.decode('utf8'))
						SDL_free(event.drop.file)

				elif event_type == SDL_DROPBEGIN:
					ENV.snap_out('drop begin')
				elif event_type == SDL_DROPCOMPLETE:
					ENV.snap_out('drop end')


				elif event_type == SDL_QUIT:
					ENV.snap_out('quit event')
					self.stop_mainloop()

				else:
					''#out('unhandled sdl gui event', event)

			# TODO put frame update on separate timer?

			#frame = (frame + 1) % MOOSEFRAMES_COUNT;
			#UpdateTexture(MooseTexture);

			#SDL_RenderClear(renderer);
			#SDL_RenderTexture(renderer, MooseTexture, NULL, NULL);
			#SDL_RenderPresent(renderer);


		def start_mainloop(self, **SETTINGS):
			# blocking mainloop (TODO make blocking optional?)

			SNAP_REFRESH_RATE = 500

			#snap_debug_gui("mainloop started @ {} or {}/sec".format(SNAP_REFRESH_RATE, 1/SNAP_REFRESH_RATE))
			ENV.snap_debug("mainloop started @ {} or {}/sec".format(SNAP_REFRESH_RATE, 1/SNAP_REFRESH_RATE))

			#ENV = self.ENV()
			ENV.mainloop.listen(self.REFRESH)
			#snap_listen(SNAP_CH_REFRESH, self)
			#print('listened to', SNAP_CH_REFRESH)
			#return snap_mainloop(**SETTINGS)
			self['running'] = True
			MAINLOOP = ENV.__PRIVATE__['__MAINLOOP_NODE__']
			while self['running']:
				MAINLOOP.next()
			#raise NotImplementedError('mainloop start')

		def stop_mainloop(self):
			''#snap_stop_mainloop()
			#snap_ignore(SNAP_CH_REFRESH, self)
			#raise NotImplementedError()
			self['running'] = False


		def __init__(self, *args, **kwargs):
			SnapGuiBase.__init__(self, *args, **kwargs)

			self.__snap_data__['__window_type__'] = SnapSDLWindow

			# https://www.geeksforgeeks.org/sdl-library-in-c-c-with-examples/

			if not SDL_WasInit(SDL_INIT_EVERYTHING): #if SNAP_SDL_NEEDS_INIT[0]:
				#SNAP_SDL_NEEDS_INIT[0] = False

				ENV.snap_debug('init SDL')

				if SDL_Init(SDL_INIT_EVERYTHING) != 0:
					raise Exception('unable to initialize SDL', SDL_GetError())

				#SnapSDL_init_default_keyboard(self)

				#print('drop event enabled?', SDL_EventState(SDL_DROPFILE, SDL_QUERY) == SDL_ENABLE)
				#SDL_EventState(SDL_DROPFILE, SDL_DISABLE)
				#SDL_EventState(SDL_DROPTEXT, SDL_DISABLE)

				state = SDL_GetModState()
				if KMOD_CAPS & state:
					'init capslock to on' # TODO
					ENV.test_out(KMOD_CAPS & state)

			
		def __del__(self):

			SDL_Quit()

			# needs init again?

	ENV.SnapSDL = SnapSDL
	return SnapSDL

def main(ENV):

	#from snap.lib.core import SNAP_GLOBAL_ENV as ENV
	#from snap.lib.gui import SnapGuiBase as SnapGuiBaseModule
	#SnapGuiBaseModule.build(ENV)
	build(ENV)

	sdl = ENV.SnapSDL()
	
	W = sdl.Window()

	sdl.start_mainloop()#runtime=3)

	ENV.snap_out('exit okay')

if __name__ == '__main__':

	from snap.SnapEnv import SnapEnv
	main(SnapEnv())


