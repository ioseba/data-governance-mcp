"""Renders an authentic, crisp, publication-grade architectural diagram."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up canvas
fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
fig.patch.set_facecolor("#ffffff")
ax.set_facecolor("#ffffff")
ax.set_xlim(0, 1500)
ax.set_ylim(0, 850)
ax.axis("off")

# Typography & Palette
FONT_FAMILY = "sans-serif"
COLOR_TITLE = "#0f172a"
COLOR_SUBTITLE = "#64748b"
COLOR_BORDER = "#cbd5e1"
COLOR_STAGE_BG = "#f8fafc"
COLOR_CARD_BG = "#ffffff"
COLOR_PRIMARY_DARK = "#1e293b"
COLOR_ACCENT_BLUE = "#2563eb"
COLOR_ACCENT_SLATE = "#475569"
COLOR_ACCENT_GREEN = "#059669"
COLOR_ACCENT_RED = "#dc2626"

# Header Banner
ax.text(750, 810, "DATA GOVERNANCE & PRIVACY TWIN MCP ARCHITECTURE", 
        fontsize=18, fontweight="bold", ha="center", va="center", color=COLOR_TITLE, fontfamily=FONT_FAMILY)
ax.text(750, 782, "Automated DAMA-DMBOK Quality Audit, Privacy-Safe Digital Twins & LLM Token Optimization", 
        fontsize=11, ha="center", va="center", color=COLOR_SUBTITLE, fontfamily=FONT_FAMILY)

# Decorative divider line
ax.plot([60, 1440], [760, 760], color="#e2e8f0", linewidth=1.5)

# Columns definitions: 4 Pillars
stages = [
    {
        "x": 60, "w": 320, "num": "1", "title": "RAW DATA INGESTION\n& PII SANITIZATION", "theme": "#3b82f6",
        "cards": [
            {"title": "Data Sources", "items": ["• CSV / TSV / Delimited", "• Columnar Parquet & Arrow", "• SQLite / SQL Databases", "• JSON & Memory Buffers"], "color": "#1e293b", "text_color": "#ffffff"},
            {"title": "Schema Sniffer & Ingestion", "items": ["• Automatic delimiter detection", "• Strict type inference", "• Encoding & header validation"], "color": "#eff6ff", "border": "#93c5fd", "text_color": "#1e3a8a"},
            {"title": "Zero-Trust Privacy Shield", "items": ["• Detects emails, phones, cards", "• Scans Spanish DNI / NIE", "• Intercepts API tokens & secrets"], "color": "#fef2f2", "border": "#fca5a5", "text_color": "#991b1b"},
        ]
    },
    {
        "x": 415, "w": 320, "num": "2", "title": "SYNTHETIC DIGITAL\nTWIN GENERATION", "theme": "#6366f1",
        "cards": [
            {"title": "Statistical Moment Profiler", "items": ["• Evaluates empirical means & std", "• Preserves min / max bounds", "• Categorical frequency ratios"], "color": "#1e293b", "text_color": "#ffffff"},
            {"title": "Differential Privacy Engine", "items": ["• Safe synthetic entity mocking", "• Replaces PII with realistic tokens", "• Preserves exact correlation ranks"], "color": "#eef2ff", "border": "#a5b4fc", "text_color": "#312e81"},
            {"title": "Null Dynamic Replicator", "items": ["• Injects exact observed missingness", "• Replicates edge cases & anomalies", "• Safe vibe coding for Cursor/Claude"], "color": "#f8fafc", "border": "#cbd5e1", "text_color": "#334155"},
        ]
    },
    {
        "x": 770, "w": 320, "num": "3", "title": "DAMA QUALITY &\nTOKEN OPTIMIZATION", "theme": "#10b981",
        "cards": [
            {"title": "DAMA-DMBOK 6 Dimensions", "items": ["• Completeness (null/whitespace)", "• Uniqueness (duplicates/keys)", "• Validity (data type consistency)", "• Consistency (cross-column logic)", "• Timeliness (temporal cadence)"], "color": "#1e293b", "text_color": "#ffffff"},
            {"title": "Tukey IQR Accuracy Engine", "items": ["• 2.5x IQR outlier fence", "• Statistical Z-score verification", "• Telemetry anomaly flagging"], "color": "#ecfdf5", "border": "#6ee7b7", "text_color": "#064e3b"},
            {"title": "Token Compressor & dbt", "items": ["• 90-95% context token reduction", "• Dense statistical fingerprint", "• Auto-generates dbt schema.yml"], "color": "#ecfdf5", "border": "#6ee7b7", "text_color": "#064e3b"},
        ]
    },
    {
        "x": 1125, "w": 315, "num": "4", "title": "MODEL CONTEXT\nPROTOCOL BRIDGE", "theme": "#0f766e",
        "cards": [
            {"title": "FastMCP Server Interface", "items": ["• Standard stdio JSON-RPC transport", "• audit_dataset & detect_pii", "• generate_synthetic_twin", "• compress_context_for_llm"], "color": "#1e293b", "text_color": "#ffffff"},
            {"title": "Supported AI Environments", "items": ["• Cursor IDE", "• Claude Desktop", "• Antigravity & Devin", "• Cline & Windsurf"], "color": "#f0fdfa", "border": "#99f6e4", "text_color": "#134e4a"},
            {"title": "Enterprise Deliverables", "items": ["• Zero enterprise data leakage", "• Offline interactive HTML report", "• Production dbt validation tests"], "color": "#f0fdf4", "border": "#86efac", "text_color": "#166534"},
        ]
    }
]

# Draw Pillars & Cards
for s in stages:
    # Stage Outer Column Box
    stage_box = patches.FancyBboxPatch((s["x"], 70), s["w"], 665,
                                        boxstyle="round,pad=0,rounding_size=10",
                                        facecolor=COLOR_STAGE_BG, edgecolor=COLOR_BORDER, linewidth=1.2)
    ax.add_patch(stage_box)

    # Column Header Tag
    ax.text(s["x"] + s["w"]/2, 695, f"{s['num']}. {s['title']}", 
            fontsize=11.5, fontweight="bold", ha="center", va="center", color=COLOR_TITLE, linespacing=1.2)

    # Draw Inner Cards
    card_y_positions = [490, 290, 95]
    card_height = 175

    for idx, card in enumerate(s["cards"]):
        cy = card_y_positions[idx]
        bg_col = card.get("color", COLOR_CARD_BG)
        border_col = card.get("border", "none")
        txt_col = card.get("text_color", "#1e293b")

        card_box = patches.FancyBboxPatch((s["x"] + 14, cy), s["w"] - 28, card_height,
                                          boxstyle="round,pad=0,rounding_size=8",
                                          facecolor=bg_col, edgecolor=border_col, linewidth=1.2)
        ax.add_patch(card_box)

        # Card Title
        is_dark_card = bg_col == "#1e293b"
        card_title_color = "#ffffff" if is_dark_card else txt_col
        ax.text(s["x"] + 28, cy + card_height - 24, card["title"], 
                fontsize=11, fontweight="bold", ha="left", va="center", color=card_title_color)

        # Card Items
        line_y = cy + card_height - 52
        for itm in card["items"]:
            item_color = "#94a3b8" if is_dark_card else (txt_col if "text_color" in card else "#475569")
            ax.text(s["x"] + 28, line_y, itm, fontsize=9.5, ha="left", va="center", color=item_color)
            line_y -= 23

# Draw Flow Arrows between stages
arrow_props = dict(arrowstyle="->,head_width=0.45,head_length=0.6", color="#2563eb", lw=2.2)
ax.annotate("", xy=(410, 420), xytext=(385, 420), arrowprops=arrow_props)
ax.annotate("", xy=(765, 420), xytext=(740, 420), arrowprops=arrow_props)
ax.annotate("", xy=(1120, 420), xytext=(1095, 420), arrowprops=arrow_props)

# Footer caption
ax.text(750, 35, "Standardized compliance workflow: Ingestion -> Differential Privacy Synthesis -> DAMA-DMBOK Scoring -> Model Context Protocol (MCP)", 
        fontsize=9.5, style="italic", ha="center", va="center", color="#64748b")

plt.tight_layout()
plt.savefig("assets/system_architecture.png", dpi=300, bbox_inches="tight")
print("assets/system_architecture.png successfully generated with 300 DPI!")
