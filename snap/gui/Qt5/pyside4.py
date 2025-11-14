
from OpenGL.GL import *
from OpenGL import GL
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

VERTEX_SOURCE = """#version 330 core

layout (location = 0) in vec2 in_position;
layout (location = 1) in vec2 in_tex_coord;

out vec2 tex_coord0;

//uniform float time;

uniform mat4 OFFSET;

void main(void){

	gl_Position = vec4(in_position.xy, 0.0, 1.0);
	
	tex_coord0 = in_tex_coord;

	//tex_coord0 = (0.5 * gl_Position.xy + vec2(0.5)) * OFFSET;
	//tex_coord0 = (OFFSET * vec4(tex_coord0.xy, 0.0, 1.0)).xy;
	//tex_coord1 = (0.5 * gl_Position.xy + vec2(0.5)) * transpose(m);
	//tex_coord1 = (OFFSET * vec4(tex_coord1.xy, 0.0, 1.0)).xy;
}
"""

FRAGMENT_SOURCE = """#version 330 core

// ***********************************************************
// Alcatraz / Rhodium 4k Intro liquid carbon
// by Jochen "Virgill" Feldkotter
//
// 4kb executable: http://www.pouet.net/prod.php?which=68239
// Youtube: https://www.youtube.com/watch?v=YK7fbtQw3ZU
// ***********************************************************

//#define time iGlobalTime
//#define res iResolution

uniform float time;

//in vec2 tex_coord0;

vec2 res;
float bounce;

//in vec2 fragCoord;
out vec4 fragColor;



// signed box
float sdBox(vec3 p,vec3 b)
{
  vec3 d=abs(p)-b;
  return min(max(d.x,max(d.y,d.z)),0.)+length(max(d,0.));
}

// rotation
void pR(inout vec2 p,float a) 
{
	p=cos(a)*p+sin(a)*vec2(p.y,-p.x);
}

// 3D noise function (IQ)
float noise(vec3 p)
{
	vec3 ip=floor(p);
    p-=ip; 
    vec3 s=vec3(7,157,113);
    vec4 h=vec4(0.,s.yz,s.y+s.z)+dot(ip,s);
    p=p*p*(3.-2.*p); 
    h=mix(fract(sin(h)*43758.5),fract(sin(h+s.x)*43758.5),p.x);
    h.xy=mix(h.xz,h.yw,p.y);
    return mix(h.x,h.y,p.z); 
}

float map(vec3 p)
{	
	p.z-=1.0;
    p*=0.9;
    pR(p.yz,bounce*1.+0.4*p.x);
    return sdBox(p+vec3(0,sin(1.6*time),0),vec3(20.0, 0.05, 1.2))-.4*noise(8.*p+3.*bounce);
}

//	normal calculation
vec3 calcNormal(vec3 pos)
{
    float eps=0.0001;
	float d=map(pos);
	return normalize(vec3(map(pos+vec3(eps,0,0))-d,map(pos+vec3(0,eps,0))-d,map(pos+vec3(0,0,eps))-d));
}


// 	standard sphere tracing inside and outside
float castRayx(vec3 ro,vec3 rd) 
{
    float function_sign=(map(ro)<0.)?-1.:1.;
    float precis=.0001;
    float h=precis*2.;
    float t=0.;
	for(int i=0;i<120;i++) 
	{
        if(abs(h)<precis||t>12.)break;
		h=function_sign*map(ro+rd*t);
        t+=h;
	}
    return t;
}

// 	refraction
float refr(vec3 pos,vec3 lig,vec3 dir,vec3 nor,float angle,out float t2, out vec3 nor2)
{
    float h=0.;
    t2=2.;
	vec3 dir2=refract(dir,nor,angle);  
 	for(int i=0;i<50;i++) 
	{
		if(abs(h)>3.) break;
		h=map(pos+dir2*t2);
		t2-=h;
	}
    nor2=calcNormal(pos+dir2*t2);
    return(.5*clamp(dot(-lig,nor2),0.,1.)+pow(max(dot(reflect(dir2,nor2),lig),0.),8.));
}

//	softshadow 
float softshadow(vec3 ro,vec3 rd) 
{
    float sh=1.;
    float t=.02;
    float h=.0;
    for(int i=0;i<22;i++)  
	{
        if(t>20.)continue;
        h=map(ro+rd*t);
        sh=min(sh,4.*h/t);
        t+=h;
    }
    return sh;
}


//	main function
void main()//out vec4 fragColor,in vec2 fragCoord)
{    
    bounce = abs(fract(0.05*time)-.5)*20.; // triangle function
	
	res = vec2(640,480);
    
	vec2 uv = gl_FragCoord.xy/res.xy;
	//vec2 uv = tex_coord0;
    vec2 p = uv*2.-1.;
   
// 	bouncy cam every 10 seconds
    float wobble=(fract(.1*(time-1.))>=0.9)?fract(-time)*0.1*sin(30.*time):0.;

//  camera    
    vec3 dir = normalize(vec3(2.*gl_FragCoord.xy - res.xy, res.y));
	//vec3 dir = normalize(vec3(2.*tex_coord0.xy, tex_coord0.y));
    vec3 org = vec3(0,2.*wobble,-3.);  
    

// 	standard sphere tracing:
    vec3 color = vec3(0.);
    vec3 color2 =vec3(0.);
    float t=castRayx(org,dir);
	vec3 pos=org+dir*t;
	vec3 nor=calcNormal(pos);

// 	lighting:
    vec3 lig=normalize(vec3(.2,6.,.5));
//	scene depth    
    float depth=clamp((1.-0.09*t),0.,1.);
    
	
    vec3 pos2 = vec3(0.);
    vec3 nor2 = vec3(0.);
    if(t<12.0)
    {
    	color2 = vec3(max(dot(lig,nor),0.)  +  pow(max(dot(reflect(dir,nor),lig),0.),16.));
    	color2 *=clamp(softshadow(pos,lig),0.,1.);  // shadow            	
       	float t2;
		color2.rgb +=refr(pos,lig,dir,nor,0.9, t2, nor2)*depth;
        color2-=clamp(.1*t2,0.,1.);				// inner intensity loss

	}  

    float tmp = 0.;
    float T = 1.;

//	animation of glow intensity    
    float intensity = 0.1*-sin(.209*time+1.)+0.05; 
	for(int i=0; i<128; i++)
	{
        float density = 0.; float nebula = noise(org+bounce);
        density=intensity-map(org+.5*nor2)*nebula;
		if(density>0.)
		{
			tmp = density / 128.;
            T *= 1. -tmp * 100.;
			if( T <= 0.) break;
		}
		org += dir*0.078;
    }    
	vec3 basecol=vec3(1./1. ,  1./4. , 1./16.);
    T=clamp(T,0.,1.5); 
    color += basecol* exp(4.*(0.5-T) - 0.8);
    color2*=depth;
    color2+= (1.-depth)*noise(6.*dir+0.3*time)*.1;	// subtle mist

	
	
//	scene depth included in alpha channel
    fragColor = vec4(vec3(1.*color+0.8*color2)*1.3,abs(0.67-depth)*2.+4.*wobble);
	//fragColor = vec4(sin(time), cos(time), 0.0, 1.0);
	//fragColor = vec4(1.0, 0.0, 0.5, 1.0);
}

"""



def build(CODES, CH, Container, Window, engines, animate, devices, interact, GuiWindow, GuiBase, Matrix, draw, debug, **X):

	globals().update(get_events_dict())
	#for event in sorted(get_events_dict().keys()):
	#	print(event)

	KEYBOARD = devices.Device()
	devices.keyboard.register(KEYBOARD)
	KEYBOARD_emit = KEYBOARD.emit # TODO use event?

	POINTER = devices.Device()
	devices.pointer.register(POINTER)
	POINTER_emit = POINTER.emit

	def build_window(MAINWINDOW, BUILD_ENGINE):

		IS_GL = BUILD_ENGINE == engines.opengl
		if IS_GL:
			QWIDGET = QtOpenGL.QGLWidget
		else:
			QWIDGET = QtGui.QWidget

		class PySideWindow(QWIDGET):

			if IS_GL:

				class CTX(object):

					#GETATTR = BUILD_ENGINE.Context(BUILD_ENGINE.Image()) # to get missing attrs

					def __init__(self, *args, **kwargs):

						self._shader_ = None
						self._ctm_ = Matrix()._matrix_

						self._COMMANDS_ = [getattr(self, attr) for attr in BUILD_ENGINE.Context._COMMAND_LIST_]

					def __getattr__(self, ATTR):
						return getattr(GL, ATTR)#getattr(self.GETATTR, ATTR)

					def _clear(self):
						glClearColor(0,0,0,0)
						glClear(GL_COLOR_BUFFER_BIT)#|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)

					def _activate(self):
						glEnable(GL_DEPTH_TEST)
						glDepthFunc(GL_LEQUAL)#GL_LESS)

						#self._set_shader(None)
						self._shader_ = None

					def _reset(self):
						glFlush()

					def _set_shader(self, INT):
						print('set shader', type(INT), INT)
						glUseProgram(INT)
						self._shader_ = INT

					def _set_matrix(self, MATRIX):
						#self._ctm_ = MATRIX
						#self.set_matrix(MATRIX)
						#print('self._shader_id', self._shader_)
						location = glGetUniformLocation(self._shader_, 'OFFSET')
						glUniformMatrix4fv(location, 1, GL_FALSE, MATRIX.reshape(16))

				CTX = CTX()


			def __init__(self, **SETTINGS):
				QWIDGET.__init__(self)

				#self.display_texture = QtGui.QImage(self._app.renderbuffer.imagebuffer.pixels, w, h, QtGui.QImage.Format_ARGB32)
				self.display_texture = QtGui.QImage()

				self.setWindowTitle(SETTINGS.get('title', sys.argv[0]))

				centered_window(self)
				if SETTINGS.get('transparent', True):
					set_transparent(self)


				#self.setWindowFlags(QtCore.Qt.FramelessWindowHint)# | QtCore.Qt.SplashScreen)

				self.setMouseTracking(True)


				self._is_fullscreen_ = 0
				self.active_keys = []
				#self.screen_space = self.get_screen().get_root_window()
				self.button_codes = {
					1:'left',
					2:'middle',
					3:'right',
					}

				self.pointer_data = {
					'POS':[0,0],
					'CHANGE':[0,0],
					}

				self._user_test_ = []#[Container(shader=engines.opengl.RhobidiumShader())]

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

				self.show()

			def set_fullscreen(self, STATE=None):

				if STATE == None:
					STATE = self.isFullScreen()

				if STATE:
					self.showNormal()
				else:
					self.showFullScreen()


			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			if IS_GL:
				def initializeGL(self):
					print('initializeGL')
					#render.gpu_init()
					self._fbo_ = glGenFramebuffers(1)

					#self._image_ = MAINWINDOW._user_window_._image_
					#self._image_ = engines.opengl.Image(640,480)
					#glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_)
					#glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._image_._engine_data_, 0)
					#glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_)

					class Rhobidium(engines.opengl.RhobidiumShader):
						PROGRAM = engines.opengl.Shader.Program(VERTEX_SOURCE, FRAGMENT_SOURCE)
						

					self._user_test_ = [Container(shader=Rhobidium())]

				def paintGL(self):
					#print('paintGL')

					if 0:
						glBindFramebuffer(GL_FRAMEBUFFER, 0)
						try:
							ctx = self.CTX
							ctx._activate()
							ctx._clear()
							#print('set shader program', MAINWINDOW._user_._shader_.PROGRAM)
							#ctx._set_shader(MAINWINDOW._user_._shader_.PROGRAM) #XXX
							draw(ctx, [MAINWINDOW._user_], 20, MAINWINDOW._user_window_._camera_.render_matrix())
						except:
							debug.print_traceback()
					else:
						try:
							#glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_)
							#glClear(GL_COLOR_BUFFER_BIT)
							''
							#MAINWINDOW._user_window_.render()
							#print('user test', self._user_test_)
							draw(self.CTX, self._user_test_, 20, Matrix())
						except:
							debug.print_traceback()


					

				def resizeGL(self, w, h):
					print('resizeGL', w, h)
					glViewport(0,0,w,h)

			else:
				def paintEvent(self, *args, **kwargs):#paintGL(self):
					#print('paint') # TODO: twice after show/hide ?

					# TODO: use an opengl rect to draw imagebuffer to window
					#print('paint event')

					painter = QtGui.QPainter()
					painter.begin(self)

					try:
						#self._app.renderbuffer.render()

						#w,h = self._app.renderbuffer.imagebuffer.size()
						#img = QtGui.QImage(self._app.renderbuffer.imagebuffer.pixels, w, h, QtGui.QImage.Format_ARGB32)

						painter.drawImage(0,0,self.display_texture)
					except Exception as e:
						print('PySide render error', repr(e))
						color = QtGui.QColor(255,0,0,int(.5*255))
						painter.setBrush(color)
						painter.setPen(color)
						painter.drawRect(0,0,self.width(),self.height())

					painter.end()


				def resize(self, w, h):
					print('normal resize', w, h)
					return QWIDGET.resize(self, w,h)



			# EVENTS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

			def event(self, EVENT):

				etype = EVENT.type()

				if 0: pass

				# WINDOW
				elif etype == EVENT_MOVE:
					print('window move')

				elif etype == EVENT_RESIZE:
					print('window resize')

				elif etype == EVENT_FOCUS_IN: # TODO: try setting up auto mouse grab with release when user enabled, focus lost = release mouse
					print('focus:in')
	
				elif etype == EVENT_FOCUS_OUT:
					print('focus:out')
	
				elif etype == EVENT_SHOW:
					print('visibility:show')

				elif etype == EVENT_HIDE:
					print('visibility:hide')

				elif etype == EVENT_CLOSE:
					print('window close')

	
				# KEYBOARD
				elif etype == EVENT_SHORTCUT_OVERRIDE:#EVENT_KEYBOARD_PRESS:
					print('key press', dir(EVENT), EVENT.key(), EVENT.text(), EVENT.nativeScanCode(), EVENT.nativeVirtualKey())
					#self.event_out('device.keyboard.raw', {'EVENT':'key.press', 'KEY':event.key(), 'TEXT':event.text(), 'CODE':event.nativeScanCode(), 'HARDWARE':event.nativeVirtualKey()})

					# NETWORK.emit('device.keyboard.press', {'AUTOREPEAT':autorepeat, 'CODE':keycode, 'VALUE':keyval, 'TEXT':string, 'NAME':keyname})
				elif etype == EVENT_KEY_RELEASE:
					print('key release') # TODO: 'NAME'
					#self.event_out('device.keyboard.raw', {'EVENT':'key.release', 'KEY':event.key(), 'TEXT':event.text(), 'CODE':event.nativeScanCode(), 'HARDWARE':event.nativeVirtualKey()})


				# MOUSE
				elif etype == EVENT_MOUSE_MOVE:
					pos = EVENT.posF()

					lclx,lcly = pos.x(), pos.y()

					pointer_data = self.pointer_data
					currx,curry = pointer_data['POS']
					change = (lclx - currx, lcly - curry)
					pointer_data['POS'] = [lclx, lcly]

					#print('mouse move', lclx,lcly, change)
					POINTER_emit(CODES.MOVE, device=POINTER, position=(lclx,lcly), change=change)#, tilt=tilt, time=time))

					#self.event_out('device.mouse.raw', {'EVENT':'move', 'DEVICE':'mouse', 'pressure':None, 'POS':[lclx, lcly], 'CHANGE':change})
				elif etype == EVENT_MOUSE_BUTTON_PRESS:
					but = EVENT.button()
					print('mouse press', but)
					#self.event_out('device.mouse.raw', {'EVENT':'button.press', 'DEVICE':'?', 'BUTTON':BUTTON_CODES.get(but, but.name)})
				elif etype == EVENT_MOUSE_BUTTON_RELEASE:
					but = EVENT.button()
					print('mouse release', but)
					#self.event_out('device.mouse.raw', {'EVENT':'button.release', 'DEVICE':'?', 'BUTTON':BUTTON_CODES.get(but, but.name)})
				elif etype == EVENT_MOUSE_BUTTON_DBL_CLICK:
					but = EVENT.button()
					print('mouse double', but)
					#self.event_out('device.mouse.raw', {'EVENT':'doubleclick', 'DEVICE':'?', 'BUTTON':BUTTON_CODES.get(but, but.name)})
				elif etype == EVENT_WHEEL:
					delta = 1
					if EVENT.delta() < 0:
						delta = -1
					print('mouse wheel', delta)
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
					print('mouse enter')
				elif etype == EVENT_LEAVE:
					print('mouse leave')


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

					
					print('tablet move', lclx, lcly, EVENT.xTilt(), EVENT.yTilt())
					#self.event_out('device.mouse.raw', {'EVENT':'move', 'DEVICE':'tablet', 'PRESSURE':event.pressure(), 'POS':[lclx,lcly], 'CHANGE':change})
					POINTER_emit(CODES.MOVE, device=POINTER, position=(lclx,lcly), change=change, pressure=EVENT.pressure(), tilt=(EVENT.xTilt(),EVENT.yTilt()))
					return True
				elif etype == EVENT_TABLET_PRESS:
					'' # XXX flag tablet as enabled for mouse device announcement
				elif etype == EVENT_TABLET_RELEASE:
					'' # XXX flag as disabled
				elif etype == EVENT_TABLET_ENTER_PROXIMITY:
					print('tablet in')
				elif etype == EVENT_TABLET_LEAVE_PROXIMITY:
					print('tablet out')

		

				else:
					''#print('unhandled event', event.type())#dir(event))
				
				return QWIDGET.event(self, EVENT)



		return PySideWindow()


	class PySideWindow(GuiWindow):
		def __init__(self, USER, **SETTINGS):
			GuiWindow.__init__(self, USER)

			#self._qtwindow_ = build_window(engines.cairo) # TODO (USER) here?
			# self._qtwindow_.comms.listen(self.emit)

			interact.set_active_window(self)

			animate.fps(30, self.render)


		def render(self, *args, **kwargs):
			CH.UPDATE.emit()
			#self._user_window_.render()	
			self._qtwindow_.update()
			

		def event(self, EVENT=None, ID=None, **MESSAGE):
			print('PysideWindow.event', CODES.decode(EVENT))
			if EVENT == CODES.CHANGED and ID == self._user_window_:
				#self._qtwindow_.event(EVENT=EVENT, **MESSAGE)
				print('engine change ui')
				self._qtwindow_ = build_window(self, engines.opengl)


	class Gui(GuiBase):
		def __init__(self):
			GuiBase.__init__(self)

			self._app = QtGui.QApplication(sys.argv)

			CH.QUIT.listen(self.quit)

			#self._app.setOverrideCursor(QtCore.Qt.BlankCursor)

			self._timer = QtCore.QTimer()
			#self._timer.timeout.connect(self.timeout)
			self._timer.timeout.connect(CH.REFRESH.emit)

			self.Window = PySideWindow

		def start(self, *args, **kwargs):
			self._timer.start((1./30)*1000) # TODO: rate
			self._app.exec_()

		def quit(self, *args, **kwargs):
			self._timer.stop()
			self._app.quit()

	return {
		'gui':Gui,
		}



if __name__ == '__main__':

	from snap import *

	w = gui.pyside4.Window(Container())

	gui.pyside4.start()

