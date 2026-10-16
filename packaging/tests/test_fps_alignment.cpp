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
    assert(mwm_layout_scale(58) == 1.0f);
    setenv("MWM_MANGOAPP_FPS_INTEGER_ALIGN", "1", 1);
    for (float scale : {1.25f, 1.5f, 1.75f, 2.0f}) {
        assert(std::fabs(mwm_layout_scale(29 * scale) - scale) < 0.001f);
        ImGui::CreateContext();
        auto& scaled_io = ImGui::GetIO();
        scaled_io.IniFilename = nullptr;
        scaled_io.DisplaySize = ImVec2(285 * scale, 200 * scale);
        scaled_io.Fonts->AddFontFromMemoryCompressedBase85TTF(GetDefaultCompressedFontDataTTFBase85(), 29 * scale);
        scaled_io.Fonts->Build();
        scaled_io.Fonts->SetTexID(static_cast<ImTextureID>(1));
        ImGui::NewFrame();
        const float scaled_anchor = ImGui::CalcTextSize("AAAA").x;
        // Integer font rasterization permits a up to 2 pixels over this four-character anchor after fit.
        assert(std::fabs(scaled_anchor / scale - anchor) <= 2.0f);
        for (const char* value : {"10", "60", "120", "240", "--"}) {
            const float width = ImGui::CalcTextSize(value).x;
            assert(std::fabs((scaled_anchor - width + width) / scale - scaled_anchor / scale) < 0.01f);
        }
        const float scaled_shift = mwm_metric_column_shift(1, step * scale, step * scale,
            anchor * scale, number_width * scale, label_width * scale, suffix_width * scale, scale);
        assert(std::fabs(scaled_shift / scale - shift1) < 0.01f);
        ImGui::EndFrame();
        ImGui::DestroyContext();
    }
    std::cout << "FSR 125/150/175/200% final font anchors and gaps verified\n";
}
