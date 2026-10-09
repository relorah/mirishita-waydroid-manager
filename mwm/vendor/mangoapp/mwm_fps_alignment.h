// SPDX-License-Identifier: MIT
#pragma once
#include <string>
#include "imgui.h"

// right_aligned_text subtracts the whole string width. Add its fractional
// suffix back so the integer portion ends at the native CPU/GPU anchor.
inline float mwm_fps_alignment_offset(const std::string& text) {
    const auto dot = text.find('.');
    if (dot == std::string::npos || dot == 0 ||
        text.find_first_not_of("0123456789.-") != std::string::npos)
        return 0.0f;
    return ImGui::CalcTextSize(text.c_str()).x -
           ImGui::CalcTextSize(text.c_str(), text.c_str() + dot).x;
}
