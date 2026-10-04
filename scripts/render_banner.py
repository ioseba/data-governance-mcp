"""Render high-resolution 300 DPI Hero Banner PNG for GitHub README."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

def render_hero_banner():
    # 2400 x 720 @ 150 dpi = 16 x 4.8 inches
    fig = plt.figure(figsize=(16, 4.8), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 480)
    ax.axis("off")

    # Dark background
    bg = patches.Rectangle((0, 0), 1600, 480, facecolor="#0B0F19", edgecolor="#1E293B", linewidth=2)
    ax.add_patch(bg)

    # Ambient subtle glow orbs
    circle1 = patches.Circle((200, 240), radius=160, facecolor="#0284C7", alpha=0.08, edgecolor="none")
    circle2 = patches.Circle((1450, 100), radius=180, facecolor="#7C3AED", alpha=0.06, edgecolor="none")
    ax.add_patch(circle1)
    ax.add_patch(circle2)

    # Subtle grid lines
    for x in range(0, 1600, 80):
        ax.axvline(x, color="#1E293B", alpha=0.25, linewidth=0.75)
    for y in range(0, 480, 80):
        ax.axhline(y, color="#1E293B", alpha=0.25, linewidth=0.75)

    # LEFT: Hexagonal Shield Icon
    # Center at (150, 240)
    cx, cy = 150, 240
    # Outer Hex
    outer_hex = [
        (cx, cy + 140),
        (cx + 105, cy + 65),
        (cx + 105, cy - 65),
        (cx, cy - 140),
        (cx - 105, cy - 65),
        (cx - 105, cy + 65),
    ]
    ax.add_patch(Polygon(outer_hex, closed=True, facecolor="#0E7490", alpha=0.2, edgecolor="#38BDF8", linewidth=2.5))

    # Inner Hex
    inner_hex = [
        (cx, cy + 105),
        (cx + 78, cy + 50),
        (cx + 78, cy - 50),
        (cx, cy - 105),
        (cx - 78, cy - 50),
        (cx - 78, cy + 50),
    ]
    ax.add_patch(Polygon(inner_hex, closed=True, facecolor="#090D16", alpha=0.9, edgecolor="#818CF8", linewidth=1.5))

    # Data telemetry lines and nodes inside shield
    ax.plot([cx, cx - 45], [cy + 55, cy - 10], color="#38BDF8", linewidth=2)
    ax.plot([cx, cx + 45], [cy + 55, cy - 10], color="#818CF8", linewidth=2)
    ax.plot([cx - 45, cx], [cy - 10, cy - 60], color="#34D399", linewidth=2)
    ax.plot([cx + 45, cx], [cy - 10, cy - 60], color="#34D399", linewidth=2)

    ax.scatter([cx], [cy + 55], s=120, color="#38BDF8", zorder=5)
    ax.scatter([cx - 45], [cy - 10], s=90, color="#818CF8", zorder=5)
    ax.scatter([cx + 45], [cy - 10], s=90, color="#C084FC", zorder=5)
    ax.scatter([cx], [cy - 60], s=90, color="#34D399", zorder=5)

    # Central MCP Chip
    chip = FancyBboxPatch((cx - 26, cy - 14), 52, 28, boxstyle="round,pad=2", facecolor="#0F172A", edgecolor="#38BDF8", linewidth=1.5, zorder=6)
    ax.add_patch(chip)
    ax.text(cx, cy, "MCP", color="#38BDF8", fontsize=11, fontweight="heavy", ha="center", va="center", zorder=7)

    # Circuit connectors extending outward
    ax.plot([cx - 105, cx - 140], [cy, cy], color="#38BDF8", linewidth=1.5, linestyle="--", alpha=0.5)
    ax.plot([cx + 105, cx + 140], [cy, cy], color="#38BDF8", linewidth=1.5, linestyle="--", alpha=0.5)

    # RIGHT: Hero Content
    tx = 340
    # Top Tag
    ax.text(
        tx, 400,
        "MODEL CONTEXT PROTOCOL  •  DAMA-DMBOK STANDARDS  •  DIFFERENTIAL PRIVACY",
        color="#38BDF8", fontsize=11, fontweight="bold", va="center"
    )

    # Main Title
    ax.text(
        tx, 335,
        "Data Governance & Privacy Twin MCP",
        color="#F8FAFC", fontsize=34, fontweight="heavy", va="center"
    )

    # Subtitle
    ax.text(
        tx, 275,
        "Enterprise-grade data quality audit, synthetic privacy digital twins & 95% LLM token compression",
        color="#94A3B8", fontsize=15, fontweight="normal", va="center"
    )

    # 4 Key Feature Badges
    badges = [
        ("🛡️ Differential Privacy Twins", "#0EA5E9", "#38BDF8"),
        ("⚡ -95% LLM Token Savings", "#6366F1", "#818CF8"),
        ("📐 DAMA-DMBOK 6 Dimensions", "#059669", "#34D399"),
        ("🚀 Instant dbt Test Suites", "#DB2777", "#F472B6"),
    ]

    bx = tx
    by = 175
    card_w = 285
    card_h = 52
    spacing = 18

    for i, (label, border_col, dot_col) in enumerate(badges):
        cur_x = bx + i * (card_w + spacing)
        # Badge background
        card = FancyBboxPatch(
            (cur_x, by), card_w, card_h,
            boxstyle="round,pad=3",
            facecolor="#1E293B",
            edgecolor=border_col,
            linewidth=1.4,
            alpha=0.9
        )
        ax.add_patch(card)
        ax.scatter([cur_x + 22], [by + card_h / 2], s=50, color=dot_col, zorder=5)
        ax.text(cur_x + 40, by + card_h / 2, label, color="#F1F5F9", fontsize=11.5, fontweight="bold", va="center")

    # Bottom Platform Support Line
    ax.text(
        tx, 90,
        "NATIVE PROTOCOL INTEGRATION WITH:",
        color="#64748B", fontsize=10.5, fontweight="bold", va="center"
    )

    platforms = "Cursor IDE   •   Claude Desktop   •   Antigravity   •   Cline   •   Devin   •   Windsurf   •   FastMCP CLI"
    ax.text(
        tx + 270, 90,
        platforms,
        color="#CBD5E1", fontsize=11, fontweight="bold", va="center"
    )

    out_path = Path("assets/hero_banner.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, facecolor="#0B0F19", edgecolor="none")
    plt.close()
    print(f"Hero banner successfully generated: {out_path.resolve()}")

if __name__ == "__main__":
    render_hero_banner()
