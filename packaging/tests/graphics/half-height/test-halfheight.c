/* SPDX-License-Identifier: 0BSD */
#include "gles_rtscale.h"
#include <assert.h>
int main(void) {
 struct rtscale_rule r={.scale=3,.base_width=1280,.base_height=720,.surface=true,.zoom_fix=true};
 int w=1280,h=720;assert(rtscale_dimensions(&r,0x8058,&w,&h)&&w==3840&&h==2160);
 w=1280;h=360;assert(rtscale_dimensions(&r,0x8058,&w,&h)&&w==3840&&h==1080);
 w=640;h=360;assert(rtscale_dimensions(&r,0x88f0,&w,&h)&&w==1920&&h==1080);
 w=1280;h=180;assert(!rtscale_dimensions(&r,0x8058,&w,&h));
 w=1616;h=720;assert(!rtscale_dimensions(&r,0x8058,&w,&h));
 float a[4]={1280,360,0,0},o[4];assert(rtscale_uniform(&r,"_ScreenParams",a,o)&&o[0]==3840&&o[1]==1080);
 r.scale=1;w=1280;h=360;assert(!rtscale_dimensions(&r,0x8058,&w,&h));
 return 0;
}
