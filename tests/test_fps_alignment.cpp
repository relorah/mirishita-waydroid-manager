// SPDX-License-Identifier: MIT
#include <cassert>
#include <cmath>
#include <iostream>
#include <string>
#include "imgui.h"
#include "font_default.h"
#include "mwm_fps_alignment.h"

int main() {
    ImGui::CreateContext();
    auto& io = ImGui::GetIO();
    io.IniFilename = nullptr;
    io.DisplaySize = ImVec2(285, 200);
    io.Fonts->AddFontFromMemoryCompressedBase85TTF(GetDefaultCompressedFontDataTTFBase85(), 29);
    io.Fonts->Build();
    io.Fonts->SetTexID(static_cast<ImTextureID>(1));
    ImGui::NewFrame();
    const float anchor = ImGui::CalcTextSize("AAAA").x;
    for (const std::string text : {"9.99", "60.00", "120.00", "240.00", "--.--"}) {
        const auto value = mwm_fps_integer_text(text);
        const float width = ImGui::CalcTextSize(value.c_str()).x;
        const float left = anchor - width;
        assert(std::fabs(left + width - anchor) < 0.01f);
        std::cout << text << " -> " << value << " integer anchor=" << left + width << '\n';
    }
    assert(mwm_fps_integer_text("60.06") == "60");
    assert(mwm_fps_integer_text("59.99") == "60");
    assert(mwm_fps_integer_text("9.49") == "9");
    assert(mwm_fps_integer_text("error") == "--");
    assert(mwm_fps_integer_text("nan") == "--");
    assert(mwm_fps_integer_text("241.00") == "--");
    const float number_width = ImGui::CalcTextSize("00").x;
    const float label_width = ImGui::CalcTextSize("GPU").x;
    const float suffix_width = ImGui::CalcTextSize("%").x;
    const float step = 90.0f;
    const float shift1 = mwm_metric_column_shift(1, step, step, anchor, number_width, label_width, suffix_width);
    const float shift2 = mwm_metric_column_shift(2, step, step, anchor, number_width, label_width, suffix_width);
    const float gap1 = step + anchor - number_width - label_width;
    const float gap2 = step - number_width - suffix_width - 1;
    assert(std::fabs(gap1 - shift1 - gap1 * 0.8f) < 0.01f);
    assert(std::fabs(gap2 - shift2 + shift1 - gap2 * 0.8f) < 0.01f);
    std::cout << "Two-digit metric gaps: 80% verified\n";
    ImGui::EndFrame();
    ImGui::DestroyContext();
}
