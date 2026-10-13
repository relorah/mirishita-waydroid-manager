/* SPDX-License-Identifier: 0BSD; independently written UV invariance probe. */
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl32.h>
#include <stdio.h>
#include <stdlib.h>
static GLuint shader(GLenum t,const char *s){GLuint a=glCreateShader(t);glShaderSource(a,1,&s,NULL);glCompileShader(a);GLint ok;glGetShaderiv(a,GL_COMPILE_STATUS,&ok);if(!ok){char b[2048];glGetShaderInfoLog(a,sizeof b,NULL,b);puts(b);exit(2);}return a;}
int main(int argc, char **argv){
 int w=argc>1?atoi(argv[1]):1280, h=argc>2?atoi(argv[2]):720; if(w<=0||h<=0)return 1;
 EGLDisplay d=eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA,EGL_DEFAULT_DISPLAY,NULL);EGLint n,ma,mi; if(!eglInitialize(d,&ma,&mi))return 1;
 EGLint a[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_NONE};EGLConfig cfg;eglChooseConfig(d,a,&cfg,1,&n);
 EGLint ca[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE},sa[]={EGL_WIDTH,64,EGL_HEIGHT,64,EGL_NONE};EGLContext c=eglCreateContext(d,cfg,EGL_NO_CONTEXT,ca);EGLSurface surf=eglCreatePbufferSurface(d,cfg,sa);if(!eglMakeCurrent(d,surf,surf,c))return 1;
 GLuint tex,fb;glGenTextures(1,&tex);glBindTexture(GL_TEXTURE_2D,tex);glTexStorage2D(GL_TEXTURE_2D,1,GL_RGBA8,w,h);glGenFramebuffers(1,&fb);glBindFramebuffer(GL_FRAMEBUFFER,fb);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,tex,0);glViewport(0,0,w,h);glClearColor(.4,.5,.6,1);glClear(GL_COLOR_BUFFER_BIT);if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)return 3;
 glBindFramebuffer(GL_FRAMEBUFFER,0);glViewport(0,0,64,64);glBindTexture(GL_TEXTURE_2D,tex);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
 const char *vs="#version 320 es\nprecision highp float;uniform vec4 _ColorBuffer_TexelSize;uniform vec3 _ScreenRTSize;out vec2 uv;flat out vec2 ratio;void main(){vec2 p=vec2(gl_VertexID==1?3.:-1.,gl_VertexID==2?3.:-1.);gl_Position=vec4(p,0,1);ratio=_ColorBuffer_TexelSize.zw*_ScreenRTSize.xy;uv=(p*.5)*ratio+.5;}";
 const char *fs="#version 320 es\nprecision highp float;uniform highp sampler2D _ColorBuffer;in vec2 uv;flat in vec2 ratio;out vec4 result;void main(){result=vec4(uv.x,texture(_ColorBuffer,uv).g,ratio.x*.1,1);}";
 GLuint p=glCreateProgram();glAttachShader(p,shader(GL_VERTEX_SHADER,vs));glAttachShader(p,shader(GL_FRAGMENT_SHADER,fs));glLinkProgram(p);GLint ok;glGetProgramiv(p,GL_LINK_STATUS,&ok);if(!ok)return 4;glUseProgram(p);GLuint va;glGenVertexArrays(1,&va);glBindVertexArray(va);glUniform1i(glGetUniformLocation(p,"_ColorBuffer"),0);
 glUniform4f(glGetUniformLocation(p,"_ColorBuffer_TexelSize"),1.f/w,1.f/h,w,h);glUniform3f(glGetUniformLocation(p,"_ScreenRTSize"),1.f/w,1.f/h,(float)w/h);
 float cv[4],rv[3];glGetUniformfv(p,glGetUniformLocation(p,"_ColorBuffer_TexelSize"),cv);glGetUniformfv(p,glGetUniformLocation(p,"_ScreenRTSize"),rv);printf("color=%g,%g,%g,%g screen=%g,%g,%g ratio=%g,%g\n",cv[0],cv[1],cv[2],cv[3],rv[0],rv[1],rv[2],cv[2]*rv[0],cv[3]*rv[1]);
 glDrawArrays(GL_TRIANGLES,0,3);unsigned char l[4],r[4];glReadPixels(16,32,1,1,GL_RGBA,GL_UNSIGNED_BYTE,l);glReadPixels(48,32,1,1,GL_RGBA,GL_UNSIGNED_BYTE,r);printf("left=%u,%u,%u right=%u,%u,%u error=%x\n",l[0],l[1],l[2],r[0],r[1],r[2],glGetError());
 if(rv[2]-(float)w/h>0.00001f||(float)w/h-rv[2]>0.00001f)return 6;
 if(abs((int)l[0]-66)>3||abs((int)r[0]-193)>3||abs((int)l[2]-26)>2)return 5;puts("PASS UV mapping and aspect invariant");return 0;
}
