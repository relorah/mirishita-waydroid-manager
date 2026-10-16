/* SPDX-License-Identifier: 0BSD */
#include "gles_rtscale.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
static void check(const char *tail, int valid, int samples) {
 char path[]="/tmp/mwm-msaa-config-XXXXXX";
 int fd=mkstemp(path); assert(fd>=0); FILE *fp=fdopen(fd,"w");
 fputs("schema_version=1\n[application.0]\nname=test.app\nbase_width=1280\nbase_height=720\nscale=6\nsurface=1\ntexelsize=0\nzoom_fix=1\n",fp);fputs(tail,fp);fclose(fp);
 struct rtscale_rule rule; assert(rtscale_load(path,"test.app",&rule)==valid);
 if(valid){assert(rule.msaa_samples==samples);assert(rule.scale==6);assert(rule.base_width==1280);}
 unlink(path);
}
int main(void){check("",1,0);check("msaa_samples=0\n",1,0);check("msaa_samples=2\n",1,2);check("msaa_samples=4\n",0,0);check("msaa_samples=-1\n",0,0);check("msaa_samples=2\nmsaa_samples=2\n",0,0);check("msaa_samples=x\n",0,0);puts("PASS optional default, 0/2, invalid and duplicate rejection");}
