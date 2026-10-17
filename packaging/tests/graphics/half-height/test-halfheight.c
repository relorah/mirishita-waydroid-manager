/* SPDX-License-Identifier: 0BSD */
#include "gles_rtscale.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

int main(void)
{
   const unsigned formats[] = {0x8051, 0x8058, 0x81a5, 0x81a6, 0x881a,
                               0x88f0, 0x8c3a, 0x8c43, 0x8cac, 0x8cad};
   const int widths[] = {960, 1280, 1680, 2560};
   unsigned cases = 0;
   for (int scale = 0; scale <= 8; scale++) {
      for (unsigned b = 0; b < sizeof(widths)/sizeof(widths[0]); b++) {
         struct rtscale_rule r = {.scale=scale, .base_width=widths[b],
            .base_height=720, .surface=true, .zoom_fix=true, .texelsize=true};
         for (int half = 1; half <= 2; half++) {
            int h0 = 720 / half, w0 = widths[b] / half;
            for (unsigned f = 0; f < sizeof(formats)/sizeof(formats[0]); f++) {
               int w=w0, h=h0;
               assert(rtscale_dimensions(&r, formats[f], &w, &h) == (scale >= 2));
               assert(w == w0 * (scale >= 2 ? scale : 1));
               assert(h == h0 * (scale >= 2 ? scale : 1));
               cases++;
            }
            float in[4] = {w0,h0,0,0}, out[4];
            assert(rtscale_uniform(&r,"_ScreenParams",in,out) == (scale >= 2));
            if (scale >= 2) {
               assert(out[0] == w0*scale && out[1] == h0*scale);
               assert(fabsf(out[2]-(1.0f+1.0f/out[0])) < 0.000001f);
               assert(fabsf(out[3]-(1.0f+1.0f/out[1])) < 0.000001f);
            }
            in[0]=1.0f/w0; in[1]=1.0f/h0; in[2]=w0; in[3]=h0;
            assert(rtscale_uniform(&r,"_MainTex_TexelSize",in,out) == (scale >= 2));
            if (scale >= 2) {
               assert(out[0] == in[0]/scale && out[1] == in[1]/scale);
               assert(out[2] == w0*scale && out[3] == h0*scale);
            }
            r.texelsize=false;
            assert(!rtscale_uniform(&r,"_MainTex_TexelSize",in,out));
            r.texelsize=true;
            cases+=3;
         }
         const int heights[] = {180,359,361,719,721,1080};
         for (unsigned i=0;i<sizeof(heights)/sizeof(heights[0]);i++) {
            int w=widths[b],h=heights[i];
            assert(!rtscale_dimensions(&r,0x8058,&w,&h));
            assert(w==widths[b] && h==heights[i]); cases++;
         }
         for (int half=1;half<=2;half++) {
            int w=widths[b]+1,h=720/half;
            assert(!rtscale_dimensions(&r,0x8058,&w,&h));
            w=widths[b];assert(!rtscale_dimensions(&r,0x8229,&w,&h));
            float in[4]={widths[b]+1,720/half,0,0},out[4];
            assert(!rtscale_uniform(&r,"_ScreenParams",in,out));
            cases+=3;
         }
      }
   }
   printf("PASS: %u RTScale half-height and control cases\n",cases);
   return 0;
}
