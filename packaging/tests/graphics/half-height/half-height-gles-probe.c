/* SPDX-License-Identifier: 0BSD
 * Independent half-height target regression, adapted from the MWM depth/stencil probe.
 * No game source or shaders.
 */
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl32.h>
#include <stdio.h>
#include <stdlib.h>

static GLuint attachment(int renderbuffer, int multisample) {
   GLuint id;
   if (renderbuffer) {
      glGenRenderbuffers(1, &id); glBindRenderbuffer(GL_RENDERBUFFER, id);
      if (multisample) glRenderbufferStorageMultisample(GL_RENDERBUFFER, 4, GL_DEPTH24_STENCIL8, 1280, 360);
      else glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 1280, 360);
      glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, id);
   } else {
      GLenum target = multisample ? GL_TEXTURE_2D_MULTISAMPLE : GL_TEXTURE_2D;
      glGenTextures(1, &id); glBindTexture(target, id);
      if (multisample) glTexStorage2DMultisample(target, 4, GL_DEPTH24_STENCIL8, 1280, 360, GL_TRUE);
      else glTexStorage2D(target, 1, GL_DEPTH24_STENCIL8, 1280, 360);
      glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, target, id, 0);
   }
   return id;
}

int main(int argc, char **argv) {
   int scale = argc > 1 ? atoi(argv[1]) : 1;
   int source_rb = argc > 2 ? atoi(argv[2]) : 0;
   int destination_rb = argc > 3 ? atoi(argv[3]) : 0;
   int bits = argc > 4 ? atoi(argv[4]) : 3;
   int expected_samples = argc > 5 ? atoi(argv[5]) : 4;
   int requested_samples = argc > 6 ? atoi(argv[6]) : 4;
   EGLDisplay display = eglGetPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, NULL);
   EGLint major, minor, count;
   if (!eglInitialize(display, &major, &minor)) return 1;
   EGLint attributes[] = {EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT, EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_NONE};
   EGLConfig config;
   if (!eglChooseConfig(display, attributes, &config, 1, &count) || !count) return 2;
   EGLint context_attributes[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
   EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, context_attributes);
   EGLint size[] = {EGL_WIDTH, 64, EGL_HEIGHT, 64, EGL_NONE};
   EGLSurface surface = eglCreatePbufferSurface(display, config, size);
   if (!eglMakeCurrent(display, surface, surface, context)) return 3;
   printf("Renderer: %s\nscale=%d source_rb=%d destination_rb=%d bits=%d\n", glGetString(GL_RENDERER), scale, source_rb, destination_rb, bits);
   GLuint source, destination;
   glGenFramebuffers(1, &source); glBindFramebuffer(GL_FRAMEBUFFER, source);
   attachment(source_rb, requested_samples != 0);
   GLint width, height, samples;
   if (source_rb) {
      glGetRenderbufferParameteriv(GL_RENDERBUFFER, GL_RENDERBUFFER_WIDTH, &width);
      glGetRenderbufferParameteriv(GL_RENDERBUFFER, GL_RENDERBUFFER_HEIGHT, &height);
      glGetRenderbufferParameteriv(GL_RENDERBUFFER, GL_RENDERBUFFER_SAMPLES, &samples);
   } else {
      GLenum target = requested_samples ? GL_TEXTURE_2D_MULTISAMPLE : GL_TEXTURE_2D;
      glGetTexLevelParameteriv(target, 0, GL_TEXTURE_WIDTH, &width);
      glGetTexLevelParameteriv(target, 0, GL_TEXTURE_HEIGHT, &height);
      if (requested_samples) glGetTexLevelParameteriv(target, 0, GL_TEXTURE_SAMPLES, &samples);
      else samples = 0;
   }
   printf("source_storage=%dx%d samples=%d\n", width, height, samples);
   if (width != 1280 * scale || height != 360 * scale || samples != expected_samples) return 11;
   GLenum none = GL_NONE;
   glDrawBuffers(1, &none); glReadBuffer(GL_NONE);
   if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) return 4;
   glClearDepthf(0.25f); glClearStencil(37); glClear(GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
   glGenFramebuffers(1, &destination); glBindFramebuffer(GL_FRAMEBUFFER, destination);
   attachment(destination_rb, 0); glDrawBuffers(1, &none); glReadBuffer(GL_NONE);
   if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) return 5;
   glClearDepthf(1.f); glClearStencil(0); glClear(GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
   glBindFramebuffer(GL_READ_FRAMEBUFFER, source); glBindFramebuffer(GL_DRAW_FRAMEBUFFER, destination);
   GLbitfield mask = (bits & 1 ? GL_DEPTH_BUFFER_BIT : 0) | (bits & 2 ? GL_STENCIL_BUFFER_BIT : 0);
   glBlitFramebuffer(0, 0, 1280, 360, 0, 0, 1280, 360, mask, GL_NEAREST);
   GLenum error = glGetError(); printf("blit_error=%x\n", error); if (error) return 6;
   /* Attach matching scaled color storage only after the depth-only blit. */
   glBindFramebuffer(GL_FRAMEBUFFER, destination);
   GLuint color; glGenTextures(1, &color); glBindTexture(GL_TEXTURE_2D, color);
   glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, 1280, 360);
   glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color, 0);
   GLenum output = GL_COLOR_ATTACHMENT0; glDrawBuffers(1, &output); glReadBuffer(output);
   if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) return 7;
   const char *vs = "#version 320 es\nvoid main(){vec2 p=vec2(gl_VertexID==1?3.0:-1.0,gl_VertexID==2?3.0:-1.0);gl_Position=vec4(p,0,1);}";
   const char *fs = "#version 320 es\nprecision highp float;layout(location=0)out vec4 color;void main(){color=vec4(0,1,0,1);}";
   GLuint v = glCreateShader(GL_VERTEX_SHADER), f = glCreateShader(GL_FRAGMENT_SHADER);
   glShaderSource(v, 1, &vs, 0); glCompileShader(v); glShaderSource(f, 1, &fs, 0); glCompileShader(f);
   GLuint program = glCreateProgram(); glAttachShader(program, v); glAttachShader(program, f); glLinkProgram(program);
   GLint linked; glGetProgramiv(program, GL_LINK_STATUS, &linked); if (!linked) return 8;
   GLuint vao; glGenVertexArrays(1, &vao); glBindVertexArray(vao); glUseProgram(program);
   glViewport(0, 0, 1280, 360); glDepthMask(GL_FALSE); glClearColor(0, 0, 0, 1);
   for (int test = 0; test < 2; test++) {
      glClear(GL_COLOR_BUFFER_BIT);
      if (test == 0) { glEnable(GL_DEPTH_TEST); glDepthFunc(GL_GREATER); glDisable(GL_STENCIL_TEST); }
      else { glDisable(GL_DEPTH_TEST); glEnable(GL_STENCIL_TEST); glStencilFunc(GL_EQUAL, 37, 255); glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP); }
      glDrawArrays(GL_TRIANGLES, 0, 3);
      unsigned char left[4], right[4];
      glReadPixels(320 * scale, 180 * scale, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, left);
      glReadPixels(960 * scale, 180 * scale, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, right);
      int expected = bits & (test == 0 ? 1 : 2) ? 255 : 0;
      error = glGetError(); printf("%s left=%u right=%u expected=%d error=%x\n", test == 0 ? "depth" : "stencil", left[1], right[1], expected, error);
      if (error || left[1] != expected || right[1] != expected) return 9 + test;
   }
   puts("PASS depth-only read/draw, texture/renderbuffer, depth/stencil masks and full physical coverage");
   return 0;
}
