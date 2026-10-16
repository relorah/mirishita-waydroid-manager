// SPDX-License-Identifier: MIT
#include <cassert>
#include <cmath>
#include <iostream>
#include "imgui.h"
#include "imgui_internal.h"
#include "font_default.h"
#include "mwm_fps_alignment.h"

int main() {
    for (float fit : {1.0f, 1.25f, 1.5f, 1.75f, 2.0f}) {
        const float scale = fit * 0.9f;
        ImGui::CreateContext();
        auto& io = ImGui::GetIO();
        io.IniFilename = nullptr;
        io.DisplaySize = ImVec2(1920,1080);
        io.Fonts->AddFontFromMemoryCompressedBase85TTF(GetDefaultCompressedFontDataTTFBase85(),29*scale);
        io.Fonts->Build();
        io.Fonts->SetTexID(static_cast<ImTextureID>(1));
        auto& style = ImGui::GetStyle();
        style.WindowPadding = ImVec2(5*scale,5*scale);
        style.CellPadding = ImVec2(4*scale,0);
        style.WindowBorderSize = 0;
        // Let ImGui settle its automatic table sizing, just as the actual HUD does.
        for (int frame=0; frame<4; ++frame) {
            ImGui::NewFrame();
            ImGui::SetNextWindowPos(ImVec2(0,0));
            ImGui::SetNextWindowSize(ImVec2(285*scale,200*scale));
            ImGui::Begin("HUD",nullptr,ImGuiWindowFlags_NoDecoration);
            assert(ImGui::BeginTable("hud",3,ImGuiTableFlags_NoClip));
            ImGui::TableNextRow();
            ImGui::TableNextColumn();
            const float left = ImGui::GetCursorScreenPos().x;
            ImGui::TextUnformatted("GPU");
            ImGui::TableNextColumn();
            ImGui::TextUnformatted("60%");
            ImGui::TableNextColumn();
            auto& col = ImGui::GetCurrentTable()->Columns[2];
            const float unit = ImGui::CalcTextSize("°C").x;
            const float value = ImGui::CalcTextSize("51").x;
            const float anchor = mwm_temperature_anchor(col.WorkMaxX-col.WorkMinX,unit,scale);
            const float right = ImGui::GetCursorScreenPos().x+anchor-value+value+scale+unit;
            assert(std::fabs(left-(ImGui::GetWindowSize().x-right)) < 1.1f);
            ImGui::TextUnformatted("51°C");
            ImGui::TableNextRow();
            ImGui::TableSetColumnIndex(0);
            const float cursor = ImGui::GetCursorPosX();
            const float width = mwm_graph_width(ImGui::GetWindowContentRegionMax().x,cursor);
            assert(std::fabs(cursor-(ImGui::GetWindowSize().x-cursor-width)) < 1.1f);
            ImGui::EndTable();
            ImGui::End();
            ImGui::EndFrame();
        }
        ImGui::DestroyContext();
    }
    std::cout << "Actual ImGui temperature and graph margins symmetric at 100/125/150/175/200% fit\n";
}
