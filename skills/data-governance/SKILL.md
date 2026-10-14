---
name: data-governance
description: Enterprise-grade DAMA-DMBOK data quality audit, PII vulnerability detection, differential-privacy synthetic twin generation, and LLM token optimization for AI agents.
---

# Data Governance & Privacy Twin Skill

Empowers AI coding agents (Cursor, Claude Code, Antigravity, Copilot, Windsurf) to safely handle and audit enterprise datasets without leaking PII or blowing up LLM context windows.

## Core Capabilities

1. **DAMA-DMBOK Quality Scorecard (0-100)**: Evaluates datasets across the 6 official DAMA dimensions:
   - Completeness
   - Uniqueness
   - Validity
   - Accuracy
   - Consistency
   - Timeliness
2. **PII Vulnerability & Leakage Detection**: Scans records for credit cards, emails, phone numbers, IP addresses, and enterprise secrets.
3. **Differential-Privacy Synthetic Digital Twin**: Generates realistic statistical replicas of production datasets with zero real user records ($\epsilon=1.0$), ensuring 100% GDPR/HIPAA compliance for vibe coding.
4. **Token Context Optimization (90-95% reduction)**: Compresses multi-megabyte datasets into high-density ~680 token statistical moments fingerprints.
5. **Production Artifacts Export**:
   - Production-ready `dbt` schema tests (`not_null`, `unique`, accepted values, Tukey fences).
   - Self-contained interactive executive HTML audit dashboards with zero external CDN dependencies.
   - Ready-to-run Python/SQL remediation scripts.

---

## When to Trigger This Skill

- When the user asks to analyze, clean, inspect, or optimize a dataset (`.csv`, `.parquet`, `.json`, `.db`, `.sqlite`).
- When working with sensitive or confidential data where corporate compliance forbids uploading real records to external LLMs.
- When an AI agent encounters prompt context bloat or token limit warnings while working with data pipelines.
- When generating data models, schema definitions, or automated `dbt` tests for production CI/CD.

---

## Workflow Instructions for AI Agents

### Step 1: Pre-Audit & Privacy Check
Before reading or processing arbitrary customer/company data:
```python
audit_dataset(file_path="path/to/dataset.csv")
```
- If PII is flagged, **never** dump the raw rows into conversation context.
- Warn the user if high-risk PII or GDPR liabilities are detected.

### Step 2: Context Compression or Synthetic Twin
Choose the optimal path depending on the user's objective:
- **For coding, feature engineering, or ML modeling**:
  Generate a privacy-safe digital twin to test code locally:
  ```python
  generate_synthetic_twin(
      file_path="path/to/dataset.csv",
      output_csv_path="data/synthetic_twin.csv",
      n_rows=500
  )
  ```
- **For prompt context minimization**:
  Extract the dense statistical fingerprint instead of passing the raw dataset:
  ```python
  compress_context_for_llm(file_path="path/to/dataset.csv")
  ```

### Step 3: Production Pipeline & Remediation
- Auto-generate test cases for data pipelines (`dbt`):
  ```python
  export_dbt_tests(file_path="path/to/dataset.csv", model_name="stg_customer_orders")
  ```
- Generate an interactive report for stakeholders:
  ```python
  export_html_dashboard(file_path="path/to/dataset.csv", output_html_path="reports/audit.html")
  ```
- Provide automatic Python/SQL fix scripts:
  ```python
  suggest_remediations(file_path="path/to/dataset.csv")
  ```

---

## MCP Server Configuration

To connect this skill to your agent, add the server configuration:

```json
{
  "mcpServers": {
    "data-governance": {
      "command": "uvx",
      "args": ["data-governance-mcp"]
    }
  }
}
```
Or when running from source:
```json
{
  "mcpServers": {
    "data-governance": {
      "command": "python",
      "args": ["-m", "data_governance_mcp.server"]
    }
  }
}
```
