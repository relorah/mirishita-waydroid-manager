// SPDX-License-Identifier: MIT
#pragma once
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>

// Keep measurement precision in the cache; round only the displayed number.
inline std::string mwm_fps_integer_text(const std::string& text) {
    char* end = nullptr;
    const double fps = std::strtod(text.c_str(), &end);
    if (end == text.c_str() || *end != '\0' || !std::isfinite(fps) || fps <= 0 || fps > 240)
        return "--";
    char buffer[16];
    std::snprintf(buffer, sizeof(buffer), "%.0f", fps);
    return buffer;
}

inline float mwm_metric_column_shift(int column, float step1, float step2,
                                     float anchor, float number_width,
                                     float label_width, float suffix_width) {
    const float gap1 = std::fmax(0.0f, step1 + anchor - number_width - label_width);
    const float gap2 = std::fmax(0.0f, step2 - number_width - suffix_width - 1.0f);
    if (column == 1) return gap1 * 0.2f;
    if (column == 2) return (gap1 + gap2) * 0.2f;
    return 0.0f;
}
