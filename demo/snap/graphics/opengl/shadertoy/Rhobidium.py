
# "Rhodium liquid carbon" created by https://www.shadertoy.com/user/Virgill
# https://www.shadertoy.com/view/llK3Dy

import time

from OpenGL.GL import *

sizeof_GLfloat = 4

VERTEX_SOURCE = """#version 330 core

layout (location = 0) in vec2 in_position;
layout (location = 1) in vec2 in_tex_coord;

out vec2 tex_coord0;

//uniform float time;

uniform mat4 OFFSET;

void main(void){

	gl_Position = vec4(in_position.xy, 0.0, 1.0);
	
	tex_coord0 = in_tex_coord;

	//tex_coord0 = (0.5 * gl_Position.xy + vec2(0.5)) * m;
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
//uniform vec2 resolution;
//vec2 resolution;// (300,300);
//resolution = (300,300);

vec2 res;

in vec2 tex_coord0;
//resolution = tex_coord0;

float bounce;

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


in vec2 fragCoord;
out vec4 fragColor;

//	main function
void main(void)//out vec4 fragColor,in vec2 fragCoord)
{    
    bounce=abs(fract(0.05*time)-.5)*20.; // triangle function
	
	res = vec2(640,480);
    
	vec2 uv=gl_FragCoord.xy/res.xy;
	//vec2 uv = tex_coord0;
    vec2 p=uv*2.-1.;
   
// 	bouncy cam every 10 seconds
    float wobble=(fract(.1*(time-1.))>=0.9)?fract(-time)*0.1*sin(30.*time):0.;
    
//  camera    
    vec3 dir = normalize(vec3(2.*gl_FragCoord.xy -res.xy, res.y));
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
	//fragColor = vec4(1.0, 0.0, 0.5, 1.0);
}

"""


VS2 = """
// ***********************************************************
// Alcatraz / Rhodium 4k Intro liquid carbon
// by Jochen "Virgill" Feldkotter
//
// 4kb executable: http://www.pouet.net/prod.php?which=68239
// Youtube: https://www.youtube.com/watch?v=YK7fbtQw3ZU
// ***********************************************************

#define time iGlobalTime
#define res iResolution

const float GA =2.399; 
const mat2 rot = mat2(cos(GA),sin(GA),-sin(GA),cos(GA));

// 	simplyfied version of Dave Hoskins blur
vec3 dof(sampler2D tex,vec2 uv,float rad)
{
	vec3 acc=vec3(0);
    vec2 pixel=vec2(.002*res.y/res.x,.002),angle=vec2(0,rad);;
    rad=1.;
	for (int j=0;j<80;j++)
    {  
        rad += 1./rad;
	    angle*=rot;
        vec4 col=texture(tex,uv+pixel*(rad-1.)*angle);
		acc+=col.xyz;
	}
	return acc/80.;
}

//-------------------------------------------------------------------------------------------
void mainImage(out vec4 fragColor,in vec2 fragCoord)
{
	vec2 uv = gl_FragCoord.xy / res.xy;
	fragColor=vec4(dof(iChannel0,uv,texture(iChannel0,uv).w),1.);
}
"""

import numpy

def build(ENV):

	# https://stackoverflow.com/questions/19449590/webgl-glsl-how-does-a-shadertoy-work

	GFX = ENV.GRAPHICS

	class RhobidiumShader(GFX.ShaderProgram):

		__slots__ = ()

		vertices = numpy.array([
			#1.0, -1.0,
			#-1.0, -1.0,
			#-1.0, 1.0,
			#1.0, 1.0,

			#-1.0, 1.0,
			#1.0, 1.0,
			#-1.0, -1.0,
			#1.0, -1.0,

			#0.0, 0.0,
			#1.0, 0.0,
			#0.0, 1.0,
			#1.0, 1.0,

			0.0, 0.0, # bottom left
			1.0, 0.0, # bottom right
			1.0, 1.0, # top right
			0.0, 1.0, # top left

			0.0, 0.0, # bottom left
			0.0, 1.0, # top left
			1.0, 1.0, # top right
			1.0, 0.0, # bottom right
			], dtype=numpy.float32)

		QUAD = glGenBuffers(1)

		glBindBuffer(GL_ARRAY_BUFFER, QUAD)
		glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
		glBindBuffer(GL_ARRAY_BUFFER, 0)

		@ENV.SnapProperty
		class time:
			def get(self, MSG):
				"()->float"
				start_time = self.__snap_data__['__start_time__']
				if start_time is None:
					start_time = self.__snap_data__['__start_time__'] = time.time()
				return time.time() - start_time

		def initialize(self):

			print('rhobidium vars are', self._VARS_)

			glUseProgram(self._ID_)

			glBindVertexArray(self._vao_)

			glBindBuffer(GL_ARRAY_BUFFER, self.QUAD)

			# (var_idx, num_per_vertex, data_type, normalized, stride(skip), offset(start_pointer)) # count is determined by draw call!
			glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, GLvoid) # in_position
			glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, 8 * sizeof_GLfloat) # in_tex_coord

			glEnableVertexAttribArray(self._VARS_.get('in_position',0))
			glEnableVertexAttribArray(self._VARS_.get('in_tex_coord',1))


			#glBindBuffer(GL_ARRAY_BUFFER, 0)
			glBindVertexArray(0)
			glUseProgram(0)



		def draw(self, CTX):

			program = self['program']
			if not program:
				return

			print('time', glGetUniformLocation(program, 'time'))
			#print('resolution', glGetUniformLocation(self._ID_, 'resolution'))

			def gen_time():
				starttime = THE_TIME()
				while 1:
					#t = int(THE_TIME() - starttime)
					#yield float(t & 0x3FFF) / float(0x3FFF)
					yield THE_TIME() - starttime
			time_var = glGetUniformLocation(self._ID_, 'time')#self._VARS_['time']
			gen_time = gen_time()
			def gen():
				#return (time_var, 1)#next(gen_time))
				yield time_var
				time = next(gen_time)
				#print(time)
				yield time


			CTX.glUniform1f( gen )#(self.time_loc, t)


			CTX.glDisable(GL_CULL_FACE)

			CTX.glBindVertexArray(self._vao_)

			CTX.glDrawArrays(GL_TRIANGLE_FAN, 0, 4)


		def __init__(self):
			GFX.ShaderProgram.__init__(self)

			self['vertex_shader'] = VERTEX_SOURCE
			self['fragment_shader'] = FRAGMENT_SOURCE

	return RhobidiumShader



def main(ENV):

	shader = build(ENV)
	ENV.__run_gui__(shader)

if __name__ == '__main__':
	import snap; main(snap.SnapEnv(graphics='OpenGL'))


