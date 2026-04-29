"""
manual_report.py
----------------
Generates a single timestamped HTML report covering ALL manual test sections
performed during a test session.

Called automatically from gui_main.py when the operator clicks
"Disconnect Trace32".  Only sections whose entry fields are non-empty
are included; empty (not-tested) tabs are silently skipped.

Usage:
    from ManualTest.manual_report import save_manual_report
    path = save_manual_report(
        sections=[
            {"name": "LED Test",
             "fields": [("LedVoltage", "1234 mV", True)],
             "overall": True},
            {"name": "BAT Test",
             "fields": [("AiBatRef", "12000 mV", True)],
             "overall": True},
        ],
        output_dir=Path("ManualTest/reports"),
    )
    # path → absolute path of the saved .html file
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

# Default output directory — ManualTest/reports/ next to this file
_DEFAULT_REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def save_manual_report(
    sections: list[dict],
    output_dir: "Path | str | None" = None,
) -> str:
    """
    Write a single timestamped HTML report covering multiple test sections.

    Parameters
    ----------
    sections   : list of dicts, each with:
                   name    (str)  — test tab name, e.g. "LED Test"
                   fields  (list) — [(field_name, measured_value, passed), ...]
                   overall (bool) — True if the section overall passed
    output_dir : directory to save the report (default: ManualTest/reports/)

    Returns
    -------
    str  Absolute path to the saved report file.
    """
    out = Path(output_dir) if output_dir else _DEFAULT_REPORTS_DIR
    out.mkdir(parents=True, exist_ok=True)

    ts          = datetime.now()
    ts_str      = ts.strftime("%Y%m%d_%H%M%S")
    ts_readable = ts.strftime("%Y-%m-%d  %H:%M:%S")
    filename    = f"Manual_Report_{ts_str}.html"
    filepath    = out / filename

    # ── Summary table ────────────────────────────────────────────────────────
    summary_rows = ""
    for sec in sections:
        cls = "pass" if sec["overall"] else "fail"
        txt = "PASS"  if sec["overall"] else "FAIL"
        summary_rows += f'      <tr><td>{sec["name"]}</td><td class="{cls}">{txt}</td></tr>\n'

    # ── Detailed sections ─────────────────────────────────────────────────────
    detail_html = ""
    for sec in sections:
        sec_cls  = "pass" if sec["overall"] else "fail"
        sec_text = "PASS"  if sec["overall"] else "FAIL"
        rows = ""
        for field_name, value, passed in sec["fields"]:
            rc = "pass" if passed else "fail"
            rt = "PASS" if passed else "FAIL"
            rows += (
                f'        <tr>\n'
                f'          <td>{field_name}</td>\n'
                f'          <td>{value}</td>\n'
                f'          <td class="{rc}">{rt}</td>\n'
                f'        </tr>\n'
            )
        detail_html += (
            f'  <h2 class="section-title">{sec["name"]}'
            f'    <span class="badge {sec_cls}">{sec_text}</span></h2>\n'
            f'  <table>\n'
            f'    <thead><tr><th>Field</th><th>Measured Value</th><th>Result</th></tr></thead>\n'
            f'    <tbody>\n{rows}    </tbody>\n'
            f'  </table>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Manual Test Report — {ts_readable}</title>
  <style>
    body                  {{ font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:20px; }}
    h1                    {{ color:#2C3E50; margin-bottom:4px; }}
    h2.section-title      {{ color:#2C3E50; margin-top:28px; margin-bottom:6px; font-size:15px; }}
    .meta                 {{ color:#7F8C8D; font-size:13px; margin-bottom:24px; }}
    table                 {{ border-collapse:collapse; width:65%; background:#fff;
                             box-shadow:0 1px 4px rgba(0,0,0,.12); border-radius:6px;
                             overflow:hidden; margin-bottom:8px; }}
    th                    {{ background:#2C3E50; color:#fff; padding:9px 14px;
                             text-align:left; font-size:13px; }}
    td                    {{ padding:7px 14px; border-bottom:1px solid #ECF0F1; font-size:13px; }}
    tr:last-child td      {{ border-bottom:none; }}
    .pass                 {{ color:#27AE60; font-weight:bold; }}
    .fail                 {{ color:#C0392B; font-weight:bold; }}
    .badge                {{ display:inline-block; padding:2px 10px; border-radius:3px;
                             font-size:12px; font-weight:bold; color:#fff; margin-left:10px;
                             vertical-align:middle; }}
    .badge.pass           {{ background:#27AE60; }}
    .badge.fail           {{ background:#C0392B; }}
    .summary              {{ border-collapse:collapse; width:320px; background:#fff;
                             box-shadow:0 1px 4px rgba(0,0,0,.12); border-radius:6px;
                             overflow:hidden; margin-bottom:28px; }}
    .summary th           {{ background:#2C3E50; color:#fff; padding:9px 14px;
                             text-align:left; font-size:13px; }}
    .summary td           {{ padding:7px 14px; border-bottom:1px solid #ECF0F1; font-size:13px; }}
    .summary tr:last-child td {{ border-bottom:none; }}
  </style>
</head>
<body>
  <h1>Manual Test Report</h1>
  <div class="meta">Generated: {ts_readable}</div>
  <h2 style="color:#2C3E50;font-size:15px;margin-bottom:6px;">Summary</h2>
  <table class="summary">
    <thead><tr><th>Test Module</th><th>Result</th></tr></thead>
    <tbody>
{summary_rows}    </tbody>
  </table>
  <h2 style="color:#2C3E50;font-size:15px;margin-bottom:6px;">Detailed Results</h2>
{detail_html}</body>
</html>
"""

    filepath.write_text(html, encoding="utf-8")
    return str(filepath)

    """
    Write a timestamped HTML report for one manual test session.

    Parameters
    ----------
    test_name  : Human-readable name of the test (e.g. "LED Test").
    fields     : List of (field_name, measured_value, passed) tuples.
    overall_ok : True if all fields passed.

    Returns
    -------
    str  Absolute path to the saved report file.
    """
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    ts          = datetime.now()
    ts_str      = ts.strftime("%Y%m%d_%H%M%S")
    ts_readable = ts.strftime("%Y-%m-%d  %H:%M:%S")

    filename  = f"Manual_Report_{ts_str}.html"
    filepath  = _REPORTS_DIR / filename

    overall_class = "pass" if overall_ok else "fail"
    overall_text  = "PASS" if overall_ok else "FAIL"

    rows_html = ""
    for field_name, value, passed in fields:
        row_class  = "pass" if passed else "fail"
        row_result = "PASS" if passed else "FAIL"
        rows_html += (
            f'        <tr>\n'
            f'          <td>{field_name}</td>\n'
            f'          <td>{value}</td>\n'
            f'          <td class="{row_class}">{row_result}</td>\n'
            f'        </tr>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Manual Test Report — {test_name}</title>
  <style>
    body      {{ font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:20px; }}
    h1        {{ color:#2C3E50; margin-bottom:4px; }}
    .meta     {{ color:#7F8C8D; font-size:13px; margin-bottom:20px; }}
    table     {{ border-collapse:collapse; width:60%; background:#fff;
                 box-shadow:0 1px 4px rgba(0,0,0,.15); border-radius:6px; overflow:hidden; }}
    th        {{ background:#2C3E50; color:#fff; padding:10px 14px; text-align:left; font-size:14px; }}
    td        {{ padding:8px 14px; border-bottom:1px solid #ECF0F1; font-size:13px; }}
    tr:last-child td {{ border-bottom:none; }}
    .pass     {{ color:#27AE60; font-weight:bold; }}
    .fail     {{ color:#C0392B; font-weight:bold; }}
    .overall  {{ display:inline-block; margin-top:16px; padding:8px 24px;
                 border-radius:4px; font-size:16px; font-weight:bold; color:#fff; }}
    .overall.pass {{ background:#27AE60; }}
    .overall.fail {{ background:#C0392B; }}
  </style>
</head>
<body>
  <h1>Manual Test Report — {test_name}</h1>
  <div class="meta">Generated: {ts_readable}</div>
  <table>
    <thead>
      <tr><th>Field</th><th>Measured Value</th><th>Result</th></tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>
  <div class="overall {overall_class}">{overall_text}</div>
</body>
</html>
"""

    filepath.write_text(html, encoding="utf-8")
    return str(filepath)
