// SPDX-License-Identifier: MIT
// GRBM_STATUS/GUI_ACTIVE sampling follows filippor/cyan-skillfish-governor gpu.rs.
#define _POSIX_C_SOURCE 200809L
#include <amdgpu.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static double clock_seconds(clockid_t id) {
    struct timespec t;
    clock_gettime(id, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}
int main(int argc, char **argv) {
    const char *node = argc > 1 ? argv[1] : "/dev/dri/renderD128";
    double interval_ms = argc > 2 ? atof(argv[2]) : 2;
    double duration = argc > 3 ? atof(argv[3]) : 2;
    if (interval_ms < 1 || interval_ms > 100 || duration < 0 || duration > 120) return 2;
    int fd = open(node, O_RDONLY | O_CLOEXEC);
    if (fd < 0) { perror(node); return 1; }
    amdgpu_device_handle dev;
    uint32_t major, minor;
    int rc = amdgpu_device_initialize(fd, &major, &minor, &dev);
    if (rc) { fprintf(stderr, "initialize: %s\n", strerror(-rc)); close(fd); return 1; }
    struct timespec delay = {0, (long)(interval_ms * 1e6)};
    if (delay.tv_nsec >= 1000000000) return 2;
    double start = clock_seconds(CLOCK_MONOTONIC), window = start;
    double cpu = clock_seconds(CLOCK_PROCESS_CPUTIME_ID);
    unsigned samples = 0, busy = 0;
    uint32_t previous = 0, reg = 0, changed = 0;
    puts("elapsed_s,gpu_active_percent,samples,register_changes,register_hex,process_cpu_ms");
    while (duration == 0 || clock_seconds(CLOCK_MONOTONIC) - start < duration) {
        rc = amdgpu_read_mm_registers(dev, 0x2004, 1, 0xffffffff, 0, &reg);
        if (rc) { fprintf(stderr, "GRBM_STATUS read: %s (%d)\n", strerror(-rc), rc); amdgpu_device_deinitialize(dev); close(fd); return 1; }
        samples++;
        busy += (reg >> 31) & 1;
        changed += samples > 1 && reg != previous;
        previous = reg;
        double now = clock_seconds(CLOCK_MONOTONIC);
        if (now - window >= 0.5) {
            double current_cpu = clock_seconds(CLOCK_PROCESS_CPUTIME_ID);
            printf("%.3f,%.2f,%u,%u,0x%08x,%.3f\n", now-start, 100.0*busy/samples, samples, changed, reg, (current_cpu-cpu)*1000);
            fflush(stdout);
            window = now; cpu = current_cpu; samples=0; busy=0; changed=0;
        }
        nanosleep(&delay, NULL);
    }
    amdgpu_device_deinitialize(dev);
    close(fd);
    return 0;
}
