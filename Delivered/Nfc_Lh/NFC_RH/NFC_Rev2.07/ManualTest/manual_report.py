"""
manual_report.py
----------------
Generates a timestamped HTML report for manual test results.

Usage (from gui_main.py):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from ManualTest.manual_report import save_manual_report

    save_manual_report(
        test_name  = "LED Test",
        fields     = [("LedVoltage", "1234 mV", True)],
        overall_ok = True,
    )
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

# ManualTest/reports/ lives next to this file
_REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def save_manual_report(
    test_name: str,
    fields: list[tuple[str, str, bool]],
    overall_ok: bool,
) -> str:
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
