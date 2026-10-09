// SPDX-License-Identifier: MIT
#pragma once
#include <cmath>
#include <fstream>
#include <optional>
#include <string>
#include <time.h>

inline std::optional<double> mwm_bc250_load(const char* path, const std::string& pci, double now) {
    std::ifstream input(path);
    int version;
    std::string device, extra;
    double stamp, value;
    if (!(input >> version >> device >> stamp >> value) || input >> extra ||
        version != 1 || device != pci || !std::isfinite(stamp) || !std::isfinite(value) ||
        now - stamp < 0 || now - stamp > 2 || value < 0 || value > 100)
        return std::nullopt;
    return value;
}
inline double mwm_monotonic_time() {
    timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return now.tv_sec + now.tv_nsec / 1e9;
}
