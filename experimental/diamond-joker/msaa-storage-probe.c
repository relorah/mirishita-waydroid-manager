/* SPDX-License-Identifier: 0BSD; independent synthetic regression, no game source. */
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl32.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
 int scale=argc>1?atoi(argv[1]):1;
 EGLDisplay d=eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA,EGL_DEFAULT_DISPLAY,NULL);
 EGLint major,minor,n; if(!eglInitialize(d,&major,&minor)){printf("eglInitialize failed %x\n",eglGetError());return 1;}
 EGLint a[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_NONE}; EGLConfig config;
 if(!eglChooseConfig(d,a,&config,1,&n)||!n)return 2;
 EGLint ca[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE}; EGLContext c=eglCreateContext(d,config,EGL_NO_CONTEXT,ca);
 EGLint sa[]={EGL_WIDTH,64,EGL_HEIGHT,64,EGL_NONE}; EGLSurface s=eglCreatePbufferSurface(d,config,sa);
 if(!eglMakeCurrent(d,s,s,c)){printf("makeCurrent failed %x\n",eglGetError());return 3;}
 printf("Renderer: %s\nVersion: %s\n",glGetString(GL_RENDERER),glGetString(GL_VERSION));

 GLuint color,depth,fb;
 glGenTextures(1,&color);glBindTexture(GL_TEXTURE_2D_MULTISAMPLE,color);
 glTexStorage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE,4,GL_RGBA8,1280,720,GL_TRUE);
 GLint samples,w,h;glGetTexLevelParameteriv(GL_TEXTURE_2D_MULTISAMPLE,0,GL_TEXTURE_SAMPLES,&samples);
 glGetTexLevelParameteriv(GL_TEXTURE_2D_MULTISAMPLE,0,GL_TEXTURE_WIDTH,&w);glGetTexLevelParameteriv(GL_TEXTURE_2D_MULTISAMPLE,0,GL_TEXTURE_HEIGHT,&h);
 glGenTextures(1,&depth);glBindTexture(GL_TEXTURE_2D_MULTISAMPLE,depth);
 glTexStorage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE,4,GL_DEPTH24_STENCIL8,1280,720,GL_TRUE);
 glGenFramebuffers(1,&fb);glBindFramebuffer(GL_FRAMEBUFFER,fb);
 glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D_MULTISAMPLE,color,0);
 glFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_STENCIL_ATTACHMENT,GL_TEXTURE_2D_MULTISAMPLE,depth,0);
 GLenum status=glCheckFramebufferStatus(GL_FRAMEBUFFER);printf("storage=%dx%d samples=%d fbo=%x error=%x\n",w,h,samples,status,glGetError());
 if(status!=GL_FRAMEBUFFER_COMPLETE)return 4;
 const char *vs="#version 320 es\nvoid main(){vec2 p=vec2((gl_VertexID==1)?3.0:-1.0,(gl_VertexID==2)?3.0:-1.0);gl_Position=vec4(p,0,1);}";
 const char *fs="#version 320 es\nprecision highp float;layout(location=0) out vec4 color;void main(){color=vec4(float(gl_SampleID)*0.5+0.25);gl_FragDepth=float(gl_SampleID)*0.25+0.25;}";
 GLuint a1=glCreateShader(GL_VERTEX_SHADER),a2=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(a1,1,&vs,0);glShaderSource(a2,1,&fs,0);glCompileShader(a1);glCompileShader(a2);
 GLuint program=glCreateProgram();glAttachShader(program,a1);glAttachShader(program,a2);glLinkProgram(program);GLint ok;glGetProgramiv(program,GL_LINK_STATUS,&ok);if(!ok){char log[4096];glGetProgramInfoLog(program,4096,0,log);puts(log);return 5;}
 GLuint vao;glGenVertexArrays(1,&vao);glBindVertexArray(vao);glUseProgram(program);glViewport(0,0,1280,720);glEnable(GL_DEPTH_TEST);glDepthFunc(GL_ALWAYS);glDrawArrays(GL_TRIANGLES,0,3);glDisable(GL_DEPTH_TEST);
 GLuint output,outfb;glGenTextures(1,&output);glBindTexture(GL_TEXTURE_2D,output);glTexStorage2D(GL_TEXTURE_2D,1,GL_RGBA8,640,360);glGenFramebuffers(1,&outfb);glBindFramebuffer(GL_FRAMEBUFFER,outfb);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,output,0);
 const char *resolve="#version 320 es\nprecision highp float;precision highp sampler2DMS;uniform sampler2DMS _ColorTex;uniform sampler2DMS _DepthTex;uniform vec4 _DepthTex_TexelSize;layout(location=0) out vec4 result;void main(){ivec2 c=ivec2(gl_FragCoord.xy/vec2(640,360)*_DepthTex_TexelSize.zw);float a=0.;float d=1.;for(int i=0;i<4;i++){a+=texelFetch(_ColorTex,c,i).r;d=min(d,texelFetch(_DepthTex,c,i).r);}result=vec4(a*.25,d,texelFetch(_ColorTex,c,2).r,1.0);}";
 GLuint r=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(r,1,&resolve,0);glCompileShader(r);GLuint rp=glCreateProgram();glAttachShader(rp,a1);glAttachShader(rp,r);glLinkProgram(rp);glGetProgramiv(rp,GL_LINK_STATUS,&ok);if(!ok){char log[4096];glGetShaderInfoLog(r,4096,0,log);puts(log);glGetProgramInfoLog(rp,4096,0,log);puts(log);return 6;}
 glUseProgram(rp);glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D_MULTISAMPLE,color);glUniform1i(glGetUniformLocation(rp,"_ColorTex"),0);glActiveTexture(GL_TEXTURE1);glBindTexture(GL_TEXTURE_2D_MULTISAMPLE,depth);glUniform1i(glGetUniformLocation(rp,"_DepthTex"),1);GLint loc=glGetUniformLocation(rp,"_DepthTex_TexelSize");glUniform4f(loc,1.f/1280,1.f/720,1280,720);float uv[4];glGetUniformfv(rp,loc,uv);printf("depth_uniform=%g,%g,%g,%g\n",uv[0],uv[1],uv[2],uv[3]);
 glViewport(0,0,640,360);glDrawArrays(GL_TRIANGLES,0,3);unsigned char pixel[4];glReadPixels(320,180,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);GLenum err=glGetError();printf("resolve=%u,%u,%u,%u error=%x\n",pixel[0],pixel[1],pixel[2],pixel[3],err);
 int cap=argc>2?atoi(argv[2]):0;int expected[4]={cap?128:191,64,cap?64:255,255};
 if(w!=1280*scale||h!=720*scale||samples!=(cap?2:4)||err)return 7;
 for(int i=0;i<4;i++)if(abs((int)pixel[i]-expected[i])>2)return 8;
 /* A spatial occluder: clear the background deep, then clear only the
  * left half near. Both physical size and pixel mapping must agree. */
 glBindFramebuffer(GL_FRAMEBUFFER,fb);glDepthMask(GL_TRUE);glClearDepthf(.75f);glClear(GL_DEPTH_BUFFER_BIT);
 glEnable(GL_SCISSOR_TEST);glScissor(0,0,640,720);glClearDepthf(.25f);glClear(GL_DEPTH_BUFFER_BIT);glDisable(GL_SCISSOR_TEST);
 glBindFramebuffer(GL_FRAMEBUFFER,outfb);glViewport(0,0,640,360);glDrawArrays(GL_TRIANGLES,0,3);
 unsigned char left[4],right[4];glReadPixels(160,180,1,1,GL_RGBA,GL_UNSIGNED_BYTE,left);glReadPixels(480,180,1,1,GL_RGBA,GL_UNSIGNED_BYTE,right);
 printf("occluder_depth_left=%u background_depth_right=%u error=%x\n",left[1],right[1],glGetError());
 if(abs((int)left[1]-64)>2||abs((int)right[1]-191)>2)return 9;
 const char *vfetch="#version 320 es\nprecision highp float;uniform highp sampler2DMS _VertexDepth;flat out float vd;void main(){vec2 p=vec2((gl_VertexID==1)?3.0:-1.0,(gl_VertexID==2)?3.0:-1.0);gl_Position=vec4(p,0,1);ivec2 c=ivec2(vec2(textureSize(_VertexDepth))*vec2(.25,.5));vd=texelFetch(_VertexDepth,c,2).r;}";
 const char *vout="#version 320 es\nprecision highp float;flat in float vd;layout(location=0)out vec4 result;void main(){result=vec4(vd,0,0,1);}";
 GLuint vsh=glCreateShader(GL_VERTEX_SHADER),fsh=glCreateShader(GL_FRAGMENT_SHADER);
 glShaderSource(vsh,1,&vfetch,0);glCompileShader(vsh);glShaderSource(fsh,1,&vout,0);glCompileShader(fsh);
 GLuint vp=glCreateProgram();glAttachShader(vp,vsh);glAttachShader(vp,fsh);glLinkProgram(vp);glGetProgramiv(vp,GL_LINK_STATUS,&ok);if(!ok){char log[4096];glGetProgramInfoLog(vp,4096,0,log);puts(log);return 13;}
 glUseProgram(vp);glUniform1i(glGetUniformLocation(vp,"_VertexDepth"),1);glDrawArrays(GL_TRIANGLES,0,3);glReadPixels(160,180,1,1,GL_RGBA,GL_UNSIGNED_BYTE,left);
 printf("vertex_msaa_sample2_depth=%u error=%x\n",left[0],glGetError());if(abs((int)left[0]-64)>2)return 14;


 glDeleteTextures(1,&color);glDeleteTextures(1,&depth);
 GLuint rb[2],rbfb;glGenRenderbuffers(2,rb);glGenFramebuffers(1,&rbfb);glBindFramebuffer(GL_FRAMEBUFFER,rbfb);
 glBindRenderbuffer(GL_RENDERBUFFER,rb[0]);glRenderbufferStorageMultisample(GL_RENDERBUFFER,4,GL_RGBA8,1280,720);
 GLint rs,rw,rh;glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_SAMPLES,&rs);glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_WIDTH,&rw);glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_HEIGHT,&rh);
 glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_RENDERBUFFER,rb[0]);
 glBindRenderbuffer(GL_RENDERBUFFER,rb[1]);glRenderbufferStorageMultisample(GL_RENDERBUFFER,4,GL_DEPTH24_STENCIL8,1280,720);glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_STENCIL_ATTACHMENT,GL_RENDERBUFFER,rb[1]);
 GLenum rbstatus=glCheckFramebufferStatus(GL_FRAMEBUFFER);GLenum rberror=glGetError();
 printf("renderbuffer=%dx%d samples=%d fbo=%x error=%x\n",rw,rh,rs,rbstatus,rberror);
 if(rw!=1280*scale||rh!=720*scale||rs!=(cap?2:4)||rbstatus!=GL_FRAMEBUFFER_COMPLETE||rberror)return 10;
 puts("PASS scaled color+depth MSAA textures/renderbuffers, four-index resolve, spatial depth occlusion, query and uniform");return 0;
}
