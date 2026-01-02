
import os, json
THISDIR = os.path.realpath(os.path.dirname(__file__))
SAMPLEDIR = os.path.join(THISDIR, 'samples')

# TODO make a shader base class that can more easily drop in shadertoy code as-is...

# https://stackoverflow.com/questions/19449590/webgl-glsl-how-does-a-shadertoy-work
# https://www.shadertoy.com/howto

# https://codebrowser.dev/gtk/gtk/demos/gtk-demo/gtkshadertoy.c.html
# https://github.com/GabeRundlett/desktop-shadertoy

# manually acquire json in mozilla: open debugger (F12), set it to network tab, reload page, click on last 200 post shadertoy, in the right side select response, right click below response in the text field and 'copy all', then paste into .json file
#	-- just be mindful of the copyrights!

"""

Dolphin
https://www.shadertoy.com/view/4sS3zG
https://www.shadertoy.com/user/iq
	*careful: this dude has extremely restrictive copyright claims sometimes!*

	tutorial:
	https://www.youtube.com/watch?v=0ifChJ0nJfM

https://www.shadertoy.com/user/diatribes/
https://www.shadertoy.com/user/BigWIngs
https://www.shadertoy.com/user/Virgill
https://www.shadertoy.com/user/Shane

https://virtualdj.com/forums/223454/General_Discussion/Best_visualization_shaders_for_VirtualDJ.html


multi-pass examples:
https://www.shadertoy.com/view/stVfWc


https://viclw17.github.io/2018/06/12/GLSL-Practice-With-Shadertoy

https://www.youtube.com/@TheArtofCodeIsCool/videos


"""
# https://codebrowser.dev/gtk/gtk/demos/gtk-demo/gtkshadertoy.c.html#gtk_shadertoy_realize_shader
VERTEX_SHADER = """#version 150 core

uniform vec3 iResolution;

in vec2 position;
out vec2 fragCoord;

void main(void){
	gl_Position = vec4(position, 0.0, 1.0);

	// Convert from OpenGL coordinate system (with origin in center
	// of screen) to Shadertoy/texture coordinate system (with origin
	// in lower left corner)
	fragCoord = (gl_Position.xy + vec2(1.0)) / vec2(2.0) * iResolution.xy;
}
"""

FRAGMENT_HEADER = """#version 150 core
uniform vec3			iResolution;			// viewport resolution (in pixels)
uniform float			iTime;					// shader playback time (in seconds)
uniform float			iTimeDelta;				// render time (in seconds)
uniform float			iFrameRate;				// shader frame rate
uniform int				iFrame;					// shader playback frame
uniform float			iChannelTime[4];		// channel playback time (in seconds)
uniform vec3			iChannelResolution[4];	// channel resolution (in pixels)
uniform vec4			iMouse;					// mouse pixel coords. xy: current (if MLB down), zw: click
uniform sampler2D		iChannel0;
uniform sampler2D		iChannel1;
uniform sampler2D		iChannel2;
uniform sampler2D 		iChannel3;
uniform vec4			iDate;					// (year, month, day, time in seconds)
uniform float			iSampleRate;			// sound sample rate (i.e., 44100)

in vec2 fragCoord;
out vec4 vFragColor;
"""
# COMMON here if applicable

# USER here

DEFAULT_mainImage_FUNCTION = """
void mainImage(out vec4 fragColor, in vec2 fragCoord){
	// Normalized pixel coordinates (from 0 to 1)
	vec2 uv = fragCoord/iResolution.xy;

	// Time varying pixel color
	vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,2,4));

	if (distance(iMouse.xy, fragCoord.xy) <= 10.0){
		col = vec3(0.0);
	}

	// Output to screen
	fragColor = vec4(col,1.0);
}
"""
FRAGMENT_FOOTER = """
void main(void){
	vec4 c;
	mainImage(c, fragCoord);
	vFragColor = c;
}
"""


# https://stackoverflow.com/questions/34859701/how-do-shadertoys-audio-shaders-work
SOUND_HEADER = """
precision highp float;

uniform float     iChannelTime[4];
uniform float     iBlockOffset;
uniform vec4      iDate;
uniform float     iSampleRate;
uniform vec3      iChannelResolution[4];
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform sampler2D iChannel2;
uniform sampler2D iChannel3;

"""
DEFAULT_mainSound_FUNCTION = """
vec2 mainSound(in int samp, in float time){
    // A 440 Hz wave that attenuates quickly over time
    //return vec2( sin(6.2831*440.0*time)*exp(-3.0*time) );
	return vec2( sin(time * 1000.0), sin(time * 1000.0) );
}
"""
SOUND_FOOTER = """
void main(void){
	// compute time `t` based on the pixel we're about to write
	// the 512.0 means the texture is 512 pixels across so it's
	// using a 2 dimensional texture, 512 samples per row
	float t = iBlockOffset + ((gl_FragCoord.x-0.5) + (gl_FragCoord.y-0.5)*512.0)/iSampleRate;

	// Get the 2 values for left and right channels

	int samp = -1; // TODO time * iSampleRate = samp?
	// so: int samp = ((gl_FragCoord.x-0.5) + (gl_FragCoord.y-0.5)*512.0);
	// float t = samp / iSampleRate;

	vec2 y = mainSound( samp, t );

	// convert them from -1 to 1 to 0 to 65536
	vec2 v  = floor((0.5+0.5*y)*65536.0);

	// separate them into low and high bytes
	vec2 vl = mod(v,256.0)/255.0;
	vec2 vh = floor(v/256.0)/255.0;

	// write them out where 
	// RED   = channel 0 low byte
	// GREEN = channel 0 high byte
	// BLUE  = channel 1 low byte
	// ALPHA = channel 2 high byte
	gl_FragColor = vec4(vl.x,vh.x,vl.y,vh.y);
}
"""


def build(ENV):

	SnapContainer = ENV.SnapContainer

	GFX = ENV.graphics['OpenGL']

	OpenGL = ENV.extern.OpenGL

	glClearColor = OpenGL.glClearColor
	glClear = OpenGL.glClear
	glUseProgram = OpenGL.glUseProgram
	glFlush = OpenGL.glFlush
	glBindVertexArray = OpenGL.glBindVertexArray
	glDrawArrays = OpenGL.glDrawArrays
	glUniform3fv = OpenGL.glUniform3fv
	glUniform3fv = OpenGL.glUniform3fv
	glUniform1f = OpenGL.glUniform1f
	glUniform1i = OpenGL.glUniform1i
	glUniform4fv = OpenGL.glUniform4fv

	GL_COLOR_BUFFER_BIT = OpenGL.GL_COLOR_BUFFER_BIT
	GL_TRIANGLE_FAN = OpenGL.GL_TRIANGLE_FAN

	# TODO CubemapA?
	# TODO Sound
	#	https://stackoverflow.com/questions/35631836/how-does-shadertoy-load-sounds-into-a-texture
	#		https://twgljs.org/examples/dynamic-buffers.html
	#			https://twgljs.org/
	#	https://stackoverflow.com/questions/34859701/how-do-shadertoys-audio-shaders-work
	#	--> so basically, the color of the image is assigned the l/r float channels of the audio, based on the time (so the audio track is rendered to an image buffer, and then that buffer can be used as sound input for something else)
	#	-- so the audio shader is called once, the output is generated (by rendering to the screen/buffer assigning colors for the audio values (RG for L and BA for R)), and then it can be played back on the CPU and piped into the image shaders frame by frame based on playback time...  clever!
	#	https://www.shadertoy.com/view/Xds3Rr
	# NOTE: all music samples on the site are 44100hz signed int 16 (2 bytes per channel), so the output of the sound buffer would be the same...
	# https://www.youtube.com/watch?v=3mteFftC7fE

	#https://www.shadertoy.com/view/ldXXDj
	#https://www.shadertoy.com/view/MdXXW2
	#https://www.shadertoy.com/view/4dfXWj
	#https://www.shadertoy.com/view/lssXWS
	#https://www.shadertoy.com/view/XdfXWS

	# TODO Common? -- this is code shared/accessible between shaders, so just paste it between the header and the user code in each?
	# buffer
	# image (buffer but flagged as toplevel -- final output)

	class ShaderToyBuffer(GFX.Shader):

		__slots__ = []

		@ENV.SnapProperty
		class name:
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['name'] or 'ShaderToyBuffer'

			def set(self, MSG):
				"(str!)"
				name = MSG.args[0]
				if name is not None:
					assert isinstance(name, str), 'name must be a string'
				self.__snap_data__['name'] = name
				self.changed(name=name)

		@ENV.SnapProperty
		class type:
			# image, buffer, sound, cubemap, ...?
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['type'] or 'buffer'
			def set(self, MSG):
				"(str!)"
				t = MSG.args[0]
				if t is not None:
					assert isinstance(t, str), 'type must be string'
				self.__snap_data__['type'] = t
				self.changed(type=t)


		@ENV.SnapProperty
		class input_info:
			def get(self, MSG):
				"()->list(dict(str:str|int))"
				return self.__snap_data__['input_info'] or {}

			def set(self, MSG):
				"(list(dict(str:str|int))!)"
				info = MSG.args[0]
				self.__snap_data__['input_info'] = info
				self.changed(input_info=info)

		
		@ENV.SnapProperty
		class output_info:
			def get(self, MSG):
				"()->list(dict(str:str|int))"
				return self.__snap_data__['output_info'] or {}

			def set(self, MSG):
				"(list(dict(str:str|int))!)"
				info = MSG.args[0]
				self.__snap_data__['output_info'] = info
				self.changed(output_info=info)

		

		@ENV.SnapProperty
		class iChannel0:
			def get(self, MSG):
				"()->ShaderToyBuffer"
				# TODO
			def set(self, MSG):
				"(ShaderToyBuffer!)"
				# TODO assign to shader uniform immediately, because it stays activated for the shader...

		@ENV.SnapProperty
		class iChannel1: pass # TODO

		@ENV.SnapProperty
		class iChannel2: pass # TODO

		@ENV.SnapProperty
		class iChannel3: pass # TODO

		@ENV.SnapProperty
		class vertex_shader:

			def get(self, MSG):
				"()->str"
				return VERTEX_SHADER

			set = None

		@ENV.SnapProperty
		class fragment_shader:
			def get(self, MSG):
				"()->str"

				common_code = self['common_code']
				user_code = self['user_code']

				FRAG = FRAGMENT_HEADER
				if common_code:
					FRAG += '\n' + common_code

				if user_code:
					FRAG += '\n' + user_code
				else:
					FRAG += '\n' + DEFAULT_mainImage_FUNCTION

				FRAG += FRAGMENT_FOOTER

				return FRAG

			set = None

		@ENV.SnapProperty
		class user_code:
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['user_code']

			def set(self, MSG):
				"(str!)"
				code = MSG.args[0]
				if code is not None:
					assert isinstance(code, str), 'code must be string'
				self.__snap_data__['user_code'] = code
				self.changed(user_code=code)

		@ENV.SnapProperty
		class common_code:
			# this is the 'common' tab in shadertoy, which means code that is shared between all the buffers,
			# ie. paste this code above the user code in each buffer (we'll just assign the duplicate copy to each buffer)
			def get(self, MSG):
				"()-str"
				return self.__snap_data__['common_code']

			def set(self, MSG):
				"(str!)"
				common = MSG.args[0]
				if common is not None:
					assert isinstance(common, str), 'common code must be string'
				self.__snap_data__['common_code'] = common
				self.changed(common_code=common)

		def __init__(self, **SETTINGS):
			GFX.Shader.__init__(self, **SETTINGS)

			self.__snap_data__['image_buffer'] = GFX.Image()
			self.__snap_data__['ctx'] = GFX.Context(image=self.__snap_data__['image_buffer'])



	class ShaderToy(GFX.Shader):
		__slots__ = []

		# TODO BufferA, BufferB, ... rendering to texture
		# TODO iChannel0-4...

		@ENV.SnapProperty
		class iResolution:
			# viewport resolution (in pixels)
			def get(self, MSG):
				"()->float[3]"
				# TODO

			def set(self, MSG):
				"(float[3]|float[2])"
				# TODO XXX just do get() using extents?

		@ENV.SnapProperty
		class iTime:
			# shader playback time (in seconds)
			def get(self, MSG):
				"()->float"
				return ENV.SnapTimers.CURRENT_TIME

		@ENV.SnapProperty
		class iTimeDelta:
			# render time (in seconds)
			def get(self, MSG):
				"()->float"
				return ENV.SnapTimers.ELAPSED_TIME

		@ENV.SnapProperty
		class iFrameRate:
			# shader frame rate
			def get(self, MSG):
				"()->float"
				return 1./ENV.SnapTimers.ELAPSED_TIME

		@ENV.SnapProperty
		class iFrame:
			# shader playback frame
			def get(self, MSG):
				"()->int"
				f = self.__snap_data__['iFrame'] or 0
				f += 1
				self.__snap_data__['iFrame'] = f
				return f

		@ENV.SnapProperty
		class iChannelTime:
			# channel playback time (in seconds)
			def get(self, MSG):
				"()->float[4]"
				# TODO 4, one for each channel?

		@ENV.SnapProperty
		class iChannelResolution:
			# channel resolution (in pixels)
			def get(self, MSG):
				"()->float[3][4]"
				# TODO resolution of each (vec3) ... maybe do this differently?

		@ENV.SnapProperty
		class iMouse:
			# mouse pixel coords. xy: current (if MLB down), zw: click
			def get(self, MSG):
				"()->float[4]"
				# TODO update and assign locally in device_event, then just return the current value...
				return [0., 0., 0., 0.]

		# these can go on the buffers, they are applied to each as shader inputs/outputs...
		#uniform sampler2D		iChannel0;
		#uniform sampler2D		iChannel1;
		#uniform sampler2D		iChannel2;
		#uniform sampler2D 		iChannel3;

		@ENV.SnapProperty
		class iDate:
			# (year, month, day, time in seconds)
			def get(self, MSG):
				"()->float[4]"
				# TODO x = year, y = month (/12), z = day, w = seconds since midnight
				return [0.,0.,0.,0.]

		@ENV.SnapProperty
		class iSampleRate:
			def get(self, MSG):
				"()->float"
				# https://www.shadertoy.com/howto
				# "44100 or 48000 depending on the host application" - but the music samples are all 44100 so we'll go with that...
				return 44100.





		@ENV.SnapProperty
		class image_buffers:
			def get(self, MSG):
				"()->ShaderToyBuffer[]"
				return self.__snap_data__['image_buffers'] or []

			def set(self, MSG):
				"(ShaderToyBuffer[])"
				images = MSG.args[0]
				if images is None:
					images = []
				# TODO connect and validate?
				if len(images) > 1:
					ENV.snap_warning('TODO multiple image buffers')
				self.__snap_data__['image_buffers'] = images
				self.changed(image_buffers=images)

		@ENV.SnapProperty
		class common_code:
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['common_code']

			def set(self, MSG):
				"(str!)"
				code = MSG.args[0]
				if code is not None:
					assert isinstance(code, str), 'wrong code type: {}'.format(type(code))
				self.__snap_data__['common_code'] = code
				for buf in self['image_buffers']:
					buf['common_code'] = code
				self['image_buffers'] = self['image_buffers'] # update
				self.changed(common_code=code)

		def from_json(self, INPUT):

			if isinstance(INPUT, (list,dict)):
				data = INPUT
			else:
				with open(INPUT, 'r') as openfile:
					data = json.loads(openfile.read())

			if isinstance(data, list):
				if len(data) > 1:
					ENV.snap_warning('extra shaders in json spec?')
				info = data[0]
			elif isinstance(data, dict):
				info = data

			version = info.pop('ver')
			description = info.pop('info')
			renderpass = info.pop('renderpass')
			if info:
				ENV.snap_warning('missed json attrs', info.keys())

			# TODO create the buffers and then link them...

			#print(description)
			title = description['name']
			user = description['username']
			date = description['date']
			tags = description['tags']

			user_profile = 'https://www.shadertoy.com/user/' + user
			url = 'https://www.shadertoy.com/view/' + description['id']

			# TODO store input/output id and info, then run through and assign the properties...
			image_buffers = []
			for buff in reversed(renderpass):
				TYPE = buff.pop('type')
				name = buff.pop('name')
				code = buff.pop('code')
				inputs = buff.pop('inputs')
				outputs = buff.pop('outputs')

				print(TYPE, name, inputs, outputs)

				d = buff.pop('description')
				if d:
					ENV.snap_debug('description used', d)

				if buff:
					ENV.snap_warning('missed buffer descriptions', buff.keys())
				
				if TYPE in ('image', 'buffer'):
					if TYPE == 'image' and not (len(outputs) == 1 and outputs[0]['id'] == '4dfGRr'):
						ENV.snap_warning('image buffer with abnormal output config?', outputs)
					image_buffers.append(
						ShaderToyBuffer(type=TYPE, name=name, user_code=code, input_info=inputs, output_info=outputs),
						)
				elif TYPE == 'common':
					# this is just code that gets pasted into the fragment shader of every buffer...
					# so just assign it to each buffer...
					raise NotImplementedError(TYPE)
				else:
					raise NotImplementedError('type', TYPE)

			self['image_buffers'] = image_buffers # and this will connect them together...

			


		def update(self):
			# https://codebrowser.dev/gtk/gtk/demos/gtk-demo/gtkshadertoy.c.html#gtk_shadertoy_realize_shader
			# -> gtk_shadertoy_realize_shader
			"""
			{
			  GtkShadertoyPrivate *priv = gtk_shadertoy_get_instance_private (
			shadertoy);
			  char *fragment_shader;
			  GError *error = NULL;
			  fragment_shader = g_strconcat (
			fragment_prefix, priv->image_shader, fragment_suffix, NULL);
			  if (!init_shaders (shadertoy, shadertoy_vertex_shader, fragment_shader, 
			&error))
				{
				  priv->error_set = TRUE;
				  gtk_gl_area_set_error (GTK_GL_AREA (shadertoy), error);
				  g_error_free (error);
				}
			  g_free (
			fragment_shader);
			  /* Start new shader at time zero */
			  priv->first_frame_time = 0;
			  priv->first_frame = 0;
			  priv->image_shader_dirty = FALSE;
			}

			"""

		def draw(self, CTX):
			# https://codebrowser.dev/gtk/gtk/demos/gtk-demo/gtkshadertoy.c.html#gtk_shadertoy_realize_shader
			# -> gtk_shadertoy_render

			#program = self['program']

			glClearColor(0.10, 0.50, 0.75, 1.0)
			glClear(GL_COLOR_BUFFER_BIT)


			# get / update these just once:
			iResolution = [640.,480.,1.]#self['iResolution']
			iTime = self['iTime']
			iTimeDelta = self['iTimeDelta']
			iFrame = self['iFrame']
			iMouse = [0.,0.,0.,0.] #self['iMouse']

			for buf in self['image_buffers']:

				glUseProgram(buf['program'])

				# Update uniforms
				for uniform in buf['uniforms']:
					loc = uniform.location
					#if loc < 0: continue # or it just wouldn't be in there...?
					name = uniform.name
					if name == 'iResolution':
						glUniform3fv(loc, 1, iResolution)
					elif name == 'iTime':
						glUniform1f(loc, iTime)
					elif name == 'iTimeDelta':
						glUniform1f(loc, iTimeDelta)
					elif name == 'iFrame':
						glUniform1i(loc, iFrame)
					elif name == 'iMouse':
						glUniform4fv(loc, 1, iMouse)
					elif name.startswith('iChannel'):
						continue # already bound
					else:
						ENV.snap_debug('miss uniform', name)

				TYPE = buf['type']
				if TYPE == 'image':
					'toplevel, render to CTX'
					CTX.activate()
					glBindVertexArray(CTX.RENDER_QUAD['__engine_data__']['__vao__'])
					glDrawArrays(GL_TRIANGLE_FAN, 0, 6)
					
				elif TYPE == 'buffer':
					'bind the fbo of the buffer context'
					'bind the uniforms' # TODO we should assign the gl uniform setter to the namedtuple as well...?
					'render using context quad'

			#glUseProgram(self['program'])

			"""

			# Use the vertices in our buffer
			glBindBuffer(GL_ARRAY_BUFFER, priv->buffer)
			glEnableVertexAttribArray(0)
			glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, 0)
			glDrawArrays(GL_TRIANGLES, 0, 6)

			# We finished using the buffers and program 
			glDisableVertexAttribArray(0)
			glBindBuffer(GL_ARRAY_BUFFER, 0)
			"""
			glUseProgram(0)
			# Flush the contents of the pipeline
			glFlush()

		def __init__(self, **SETTINGS):
			GFX.Shader.__init__(self, **SETTINGS)

			self.from_json(os.path.join(SAMPLEDIR, '"Night Cloud Dance by diatribes" -- www.shadertoy.com view 3cjcWD.json'))
			#self.from_json(os.path.join(SAMPLEDIR, '"Rhodium Liquid Carbon by Virgill" -- www.shadertoy.com view llK3Dy.json'))

	# TODO make a non-opengl gui like the one shadertoy has, then do the gl render in the corner...



	GFX = ENV.graphics['QT5']

	class ShaderToyApp(SnapContainer):

		__slots__ = []

		def __init__(self, **SETTINGS):
			SnapContainer.__init__(self, **SETTINGS)

			

	ENV.ShaderToy = ShaderToy
	return ShaderToy

def main(ENV):

	ENV.__run_gui__(build(ENV))

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='OpenGL'))

