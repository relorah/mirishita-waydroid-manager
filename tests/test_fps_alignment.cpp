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
        const auto dot = text.find('.');
        const float left = anchor + mwm_fps_alignment_offset(text) - ImGui::CalcTextSize(text.c_str()).x;
        const float integer_end = left + ImGui::CalcTextSize(text.substr(0, dot).c_str()).x;
        assert(std::fabs(integer_end - anchor) < 0.01f);
        std::cout << text << " integer anchor=" << integer_end << '\n';
    }
    assert(mwm_fps_alignment_offset("error") == 0);
    assert(mwm_fps_alignment_offset("FPS 60.00") == 0);
    ImGui::EndFrame();
    ImGui::DestroyContext();
}
