"""Zero-Dependency Interactive HTML Governance Dashboard Generator."""

from __future__ import annotations

import json
import math
from .dimensions import QualityScorecard
from .pii_detector import PIIScanResult


class DashboardExporter:
    """Exports self-contained executive HTML dashboards with zero external CDN dependencies."""

    @classmethod
    def _generate_radar_svg(cls, scorecard: QualityScorecard) -> str:
        cx, cy, r = 180, 150, 95
        dims = list(scorecard.dimension_scores.items())
        n = len(dims)
        if n == 0:
            return ""

        # Grid rings
        rings_svg = []
        for level in [0.25, 0.5, 0.75, 1.0]:
            ring_pts = []
            for i in range(n):
                angle = (i * 2 * math.pi / n) - (math.pi / 2)
                x = cx + level * r * math.cos(angle)
                y = cy + level * r * math.sin(angle)
                ring_pts.append(f"{x:.1f},{y:.1f}")
            dash = ' stroke-dasharray="3,3"' if level < 1.0 else ""
            rings_svg.append(f'<polygon points="{" ".join(ring_pts)}" fill="none" stroke="#334155" stroke-width="1"{dash} />')

        # Axes, labels, data points
        axes_svg = []
        labels_svg = []
        data_pts = []
        dots_svg = []

        for i, (name, dim) in enumerate(dims):
            angle = (i * 2 * math.pi / n) - (math.pi / 2)
            ax_x = cx + r * math.cos(angle)
            ax_y = cy + r * math.sin(angle)
            axes_svg.append(f'<line x1="{cx}" y1="{cy}" x2="{ax_x:.1f}" y2="{ax_y:.1f}" stroke="#334155" stroke-width="1" />')

            # Label position
            lx = cx + (r + 26) * math.cos(angle)
            ly = cy + (r + 18) * math.sin(angle) + 4
            anchor = "middle"
            if math.cos(angle) > 0.3:
                anchor = "start"
            elif math.cos(angle) < -0.3:
                anchor = "end"
            labels_svg.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#cbd5e1" font-size="11" font-weight="600" text-anchor="{anchor}">{name} ({dim.score:.0f}%)</text>'
            )

            # Data coordinate
            val_r = (max(0.0, min(100.0, dim.score)) / 100.0) * r
            dx = cx + val_r * math.cos(angle)
            dy = cy + val_r * math.sin(angle)
            data_pts.append(f"{dx:.1f},{dy:.1f}")
            dots_svg.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4.5" fill="#38bdf8" stroke="#0f172a" stroke-width="2" />')

        data_poly = f'<polygon points="{" ".join(data_pts)}" fill="#38bdf8" fill-opacity="0.3" stroke="#38bdf8" stroke-width="2.5" />'

        return f'''
        <svg viewBox="0 0 360 300" width="100%" height="270" style="overflow: visible;">
          {"".join(rings_svg)}
          {"".join(axes_svg)}
          {data_poly}
          {"".join(dots_svg)}
          {"".join(labels_svg)}
        </svg>
        '''

    @classmethod
    def generate_html(
        cls,
        scorecard: QualityScorecard,
        pii: PIIScanResult,
    ) -> str:
        score = scorecard.overall_score
        status_color = "#10b981" if score >= 90 else ("#f59e0b" if score >= 75 else "#ef4444")
        status_label = "EXCELLENT" if score >= 90 else ("ACCEPTABLE" if score >= 75 else "CRITICAL")
        radar_svg = cls._generate_radar_svg(scorecard)

        # Prepare dimension bars
        dim_rows_html = []
        for name, dim in scorecard.dimension_scores.items():
            color = "#10b981" if dim.status == "PASS" else ("#f59e0b" if dim.status == "WARNING" else "#ef4444")
            dim_rows_html.append(f"""
            <div style="margin-bottom: 14px;">
              <div style="display: flex; justify-content: space-between; font-weight: 600; margin-bottom: 4px; font-size: 13px;">
                <span>{name}</span>
                <span style="color: {color};">{dim.score:.1f}% ({dim.status})</span>
              </div>
              <div style="background: #334155; height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: {color}; width: {dim.score}%; height: 100%; border-radius: 4px;"></div>
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-top: 3px;">{dim.summary}</div>
            </div>
            """)

        dim_html_joined = "".join(dim_rows_html)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Data Governance Audit Dashboard - {scorecard.source_info}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', Helvetica, Arial, sans-serif;
      background: #090d16;
      color: #f8fafc;
      margin: 0;
      padding: 30px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: #0f172a;
      border-radius: 16px;
      padding: 36px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
      border: 1px solid #1e293b;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #1e293b;
      padding-bottom: 24px;
      margin-bottom: 28px;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}
    .score-circle {{
      width: 110px;
      height: 110px;
      border-radius: 50%;
      border: 4px solid {status_color};
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      background: rgba(15, 23, 42, 0.8);
      box-shadow: 0 0 20px {status_color}33;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 20px;
    }}
    h1 {{ margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }}
    h2 {{ font-size: 15px; margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 10px; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.8px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; margin-bottom: 8px;">DAMA-DMBOK AUDIT REPORT</span>
        <h1>Data Governance & Quality Audit</h1>
        <p style="color: #94a3b8; margin: 6px 0 0 0; font-size: 13px;">Target: <code>{scorecard.source_info}</code> &bull; Records: <strong>{scorecard.total_records:,}</strong> &bull; Dimensions: <strong>6</strong></p>
      </div>
      <div class="score-circle">
        <span style="font-size: 28px; color: {status_color};">{score:.0f}</span>
        <span style="font-size: 10px; color: #94a3b8;">/ 100 DAMA</span>
      </div>
    </div>

    <div class="grid-2">
      <div class="card" style="margin-bottom: 0;">
        <h2>DAMA Radar Distribution</h2>
        <div style="display: flex; justify-content: center; align-items: center; padding: 10px 0;">
          {radar_svg}
        </div>
      </div>
      <div class="card" style="margin-bottom: 0;">
        <h2>Dimension Score Breakdown</h2>
        {dim_html_joined}
      </div>
    </div>

    <div class="card">
      <h2>Privacy & PII Exposure Risk Assessment</h2>
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
        <span style="font-weight: 700; font-size: 15px; color: {'#10b981' if not pii.has_pii_risk else '#f43f5e'};">
          Risk Rating: {pii.risk_level} ({pii.total_findings} findings)
        </span>
        <span class="badge" style="background: {'rgba(16, 185, 129, 0.15)' if not pii.has_pii_risk else 'rgba(244, 63, 94, 0.15)'}; color: {'#10b981' if not pii.has_pii_risk else '#f43f5e'};">
          {'ZERO LEAKAGE' if not pii.has_pii_risk else 'SYNTHETIC TWIN REQUIRED'}
        </span>
      </div>
      <p style="font-size: 13px; color: #94a3b8; margin: 0; line-height: 1.5;">
        {'Zero unmasked confidential records detected. Safe for direct ingestion.' if not pii.has_pii_risk else 'Sensitive tokens or headers detected. Generate a differential-privacy synthetic digital twin using `data-governance-mcp twin` prior to LLM injection to ensure GDPR and HIPAA compliance.'}
      </p>
    </div>

    <div style="text-align: center; font-size: 12px; color: #64748b; margin-top: 28px;">
      Generated autonomously by <strong>data-governance-mcp</strong> &bull; CDMP Certified DAMA-DMBOK Engine &bull; <a href="https://github.com/ioseba/data-governance-mcp" style="color: #38bdf8; text-decoration: none;">GitHub Repository</a>
    </div>
  </div>
</body>
</html>"""
        return html
