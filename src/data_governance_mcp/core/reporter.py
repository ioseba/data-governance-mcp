"""Executive Markdown & JSON Reporting Engine for Data Governance Audits."""

from __future__ import annotations

from typing import Any, Dict
from .dimensions import QualityScorecard
from .pii_detector import PIIScanResult


class GovernanceReporter:
    """Renders comprehensive, executive-ready data audit and compliance reports."""

    @staticmethod
    def render_markdown(
        scorecard: QualityScorecard,
        pii_result: PIIScanResult,
    ) -> str:
        """Produces a clean GitHub-Flavored Markdown governance report."""
        score = scorecard.overall_score
        status_emoji = "🟢" if score >= 90 else ("🟡" if score >= 75 else "🔴")
        status_label = "EXCELLENT" if score >= 90 else ("ACCEPTABLE" if score >= 75 else "CRITICAL / NON-COMPLIANT")

        pii_emoji = "🛡️" if not pii_result.has_pii_risk else ("⚠️" if pii_result.risk_level in ("LOW", "MEDIUM") else "🚨")

        md = []
        md.append(f"# 🛡️ Data Governance & Quality Audit Report")
        md.append(f"> **Target Dataset**: `{scorecard.source_info}` | **Records**: `{scorecard.total_records:,}` | **Columns**: `{scorecard.total_columns}`\n")

        md.append("## 📊 Executive Summary\n")
        md.append(f"| Metric | Value | Compliance Status |")
        md.append(f"| :--- | :--- | :--- |")
        md.append(f"| **DAMA Overall Quality Index** | **`{score:.1f} / 100`** | {status_emoji} **{status_label}** |")
        md.append(f"| **Privacy & PII Exposure Risk** | **`{pii_result.risk_level}`** | {pii_emoji} **{pii_result.total_findings} findings** |")
        md.append(f"| **Critical Blockers** | **`{len(scorecard.critical_issues)}`** | {'✅ Clean' if not scorecard.critical_issues else '❌ Remediation Required'} |\n")

        md.append("## 📐 DAMA-DMBOK Quality Dimensions Breakdown\n")
        md.append("| Dimension | Score | Status | Key Diagnostic Finding |")
        md.append("| :--- | :---: | :---: | :--- |")

        for dim_name, res in scorecard.dimension_scores.items():
            icon = "🟢" if res.status == "PASS" else ("🟡" if res.status == "WARNING" else "🔴")
            md.append(f"| **{dim_name}** | `{res.score:.1f}%` | {icon} `{res.status}` | {res.summary} |")

        md.append("")

        # PII Findings Section
        if pii_result.has_pii_risk:
            md.append("## 🚨 Sensitive Data & Privacy Risks (PII)")
            for col, findings in pii_result.findings_by_column.items():
                md.append(f"- **Column `{col}`**:")
                for f in findings:
                    if f["type"] == "HEADER_RISK":
                        md.append(f"  - ⚠️ *Header Alert*: {f['detail']}")
                    else:
                        md.append(f"  - 🔴 *Pattern Match*: Found `{f['sample_matches']}` instances of `{f['pattern']}` ({round(f['sample_rate']*100, 1)}% of sample)")
            if pii_result.leakage_warnings:
                md.append("\n> [!CAUTION]")
                for w in pii_result.leakage_warnings:
                    md.append(f"> {w}")
            md.append("")
        else:
            md.append("## 🛡️ Privacy & Sensitive Data Scan")
            md.append("✅ **No unmasked PII, credentials, or sensitive headers detected in sample.**\n")

        # Remediation Section
        remediations = []
        for res in scorecard.dimension_scores.values():
            remediations.extend(res.remediations)

        if remediations:
            md.append("## 🛠️ Actionable Remediation Plan")
            for idx, rem in enumerate(remediations, 1):
                md.append(f"{idx}. {rem}")
            md.append("")

        md.append("---")
        md.append("*Generated automatically by [data-governance-mcp](https://github.com/ioseba/data-governance-mcp) based on DAMA-DMBOK standards.*")

        return "\n".join(md)

    @staticmethod
    def render_json(scorecard: QualityScorecard, pii_result: PIIScanResult) -> Dict[str, Any]:
        """Consolidates complete audit in structured JSON dictionary."""
        return {
            "scorecard": scorecard.to_dict(),
            "pii_scan": pii_result.to_dict(),
        }
