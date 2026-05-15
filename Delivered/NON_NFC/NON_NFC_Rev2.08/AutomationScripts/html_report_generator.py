"""
HTML Test Report Generator
==========================
Generates a self-contained HTML test report from the structured results
produced by :func:`~AutomationScripts.report_generator.results_from_run`.

Typical usage (called automatically from ``generate_report``)::

    from AutomationScripts.html_report_generator import generate_html_report
    html_path = generate_html_report(
        results_by_sheet=results_by_sheet,
        reports_dir=REPORTS_DIR,
        project_title="Smart BU Testbench NON_NFC – Automated Test Report",
    )
    print(f"HTML Report saved to: {html_path}")
"""

from __future__ import annotations

import html as _html
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# ── Column headers matching the Excel template ────────────────────────────────
_HEADERS = [
    "S No.",
    "Test Case ID",
    "Test Case Name",
    "Pre Action",
    "Test Steps",
    "Expected Result",
    "Post Action",
    "Observed Result",
    "Status",
    "Remark",
]

# ── Embedded CSS ──────────────────────────────────────────────────────────────
_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: Calibri, 'Segoe UI', Arial, sans-serif;
    background: #eef1f5;
    color: #2c2c2c;
    min-height: 100vh;
}

/* ── Header ─────────────────────────────────────────────────────────────── */
.report-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2a5298 100%);
    color: #fff;
    padding: 24px 36px 20px;
    border-bottom: 4px solid #FFC000;
}
.report-header h1 {
    font-size: 1.55em;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin-bottom: 6px;
}
.report-header .meta {
    font-size: 0.82em;
    opacity: 0.78;
}

/* ── Summary cards ──────────────────────────────────────────────────────── */
.summary {
    display: flex;
    gap: 16px;
    padding: 22px 36px;
    flex-wrap: wrap;
}
.card {
    background: #fff;
    border-radius: 10px;
    padding: 18px 28px;
    text-align: center;
    flex: 1;
    min-width: 120px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.09);
    border-top: 4px solid transparent;
}
.card .count  { font-size: 2.4em; font-weight: 700; line-height: 1.1; }
.card .label  { font-size: 0.78em; color: #777; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.card.total   { border-color: #1a3a5c; }  .card.total   .count { color: #1a3a5c; }
.card.pass    { border-color: #2e7d32; }  .card.pass    .count { color: #2e7d32; }
.card.fail    { border-color: #c62828; }  .card.fail    .count { color: #c62828; }
.card.not-run { border-color: #e65100; }  .card.not-run .count { color: #e65100; }

/* ── Tabs bar ───────────────────────────────────────────────────────────── */
.tabs-bar {
    display: flex;
    gap: 4px;
    padding: 0 36px;
    flex-wrap: wrap;
    align-items: flex-end;
}
.tab-btn {
    padding: 9px 20px;
    border: none;
    border-radius: 8px 8px 0 0;
    background: #c5d0dc;
    color: #1a3a5c;
    cursor: pointer;
    font-size: 0.88em;
    font-weight: 700;
    transition: background 0.15s;
    outline: none;
}
.tab-btn:hover:not(.active) { background: #a8b8c8; }
.tab-btn.active {
    background: #fff;
    color: #1a3a5c;
    box-shadow: 0 -2px 6px rgba(0,0,0,0.08);
}

/* ── Content area ───────────────────────────────────────────────────────── */
.content-area {
    background: #fff;
    margin: 0 36px 36px;
    border-radius: 0 8px 8px 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.09);
    overflow-x: auto;
}
.tab-panel { display: none; padding: 22px; }
.tab-panel.active { display: block; }

/* ── Table ──────────────────────────────────────────────────────────────── */
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.80em;
    table-layout: auto;
}
thead tr th {
    background: #FFC000;
    color: #1a1a1a;
    padding: 9px 11px;
    text-align: left;
    border: 1px solid #d99e00;
    white-space: nowrap;
    font-size: 0.92em;
    font-weight: 700;
    position: sticky;
    top: 0;
    z-index: 1;
}
tbody tr td {
    padding: 8px 11px;
    border: 1px solid #dce0e6;
    vertical-align: top;
    white-space: pre-wrap;
    word-break: break-word;
}
tbody tr:nth-child(even) td { background: #f7f9fc; }
tbody tr:hover td { background: #eef3fa; }

/* ── Column widths ──────────────────────────────────────────────────────── */
.col-sno    { width: 44px;  text-align: center; }
.col-tcid   { width: 110px; white-space: nowrap; }
.col-name   { width: 220px; }
.col-pre    { width: 240px; }
.col-steps  { width: 240px; }
.col-exp    { width: 210px; }
.col-post   { width: 170px; }
.col-obs    { width: 160px; }
.col-status { width: 80px;  text-align: center; white-space: nowrap; }
.col-remark { width: 80px;  }

/* ── Status cell colours ────────────────────────────────────────────────── */
.status-pass {
    background: #92D050 !important;
    color: #1a3a1a;
    font-weight: 700;
    text-align: center;
}
.status-fail {
    background: #FF4C4C !important;
    color: #fff;
    font-weight: 700;
    text-align: center;
}
.status-skip {
    background: #FFFF00 !important;
    color: #555;
    font-weight: 700;
    text-align: center;
}

/* ── Footer ─────────────────────────────────────────────────────────────── */
.report-footer {
    text-align: center;
    font-size: 0.75em;
    color: #999;
    padding: 12px 0 24px;
}
"""

# ── Embedded JavaScript ───────────────────────────────────────────────────────
_JS = """
function showTab(name) {
    document.querySelectorAll('.tab-panel').forEach(function(p) {
        p.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(function(b) {
        b.classList.remove('active');
    });
    var panel = document.getElementById('panel-' + name);
    var btn   = document.getElementById('btn-'   + name);
    if (panel) panel.classList.add('active');
    if (btn)   btn.classList.add('active');
}
document.addEventListener('DOMContentLoaded', function() {
    var first = document.querySelector('.tab-btn');
    if (first) first.click();
});
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _esc(value: Any) -> str:
    """HTML-escape any value, converting it to a string first."""
    return _html.escape(str(value) if value is not None else "")


def _safe_id(sheet_name: str) -> str:
    """Convert a sheet name to a valid HTML id fragment."""
    return sheet_name.strip().replace(" ", "_").replace("/", "-")


def _status_class(status: str) -> str:
    s = (status or "").upper().strip()
    if s == "PASS":
        return "status-pass"
    if s == "FAIL":
        return "status-fail"
    return "status-skip"


def _build_table(rows: List[Dict[str, Any]]) -> str:
    """Render one sheet's rows as an HTML table string."""
    parts: List[str] = []
    parts.append("<table>")
    parts.append("<thead><tr>")
    col_classes = [
        "col-sno", "col-tcid", "col-name", "col-pre", "col-steps",
        "col-exp", "col-post", "col-obs", "col-status", "col-remark",
    ]
    for header, cls in zip(_HEADERS, col_classes):
        parts.append(f'<th class="{cls}">{_esc(header)}</th>')
    parts.append("</tr></thead>")
    parts.append("<tbody>")
    for i, row in enumerate(rows, start=1):
        parts.append("<tr>")
        parts.append(f'<td class="col-sno">{i}</td>')
        parts.append(f'<td class="col-tcid">{_esc(row.get("TestCaseID", ""))}</td>')
        parts.append(f'<td class="col-name">{_esc(row.get("TestName", ""))}</td>')
        parts.append(f'<td class="col-pre">{_esc(row.get("PreAction", ""))}</td>')
        parts.append(f'<td class="col-steps">{_esc(row.get("TestSteps", ""))}</td>')
        parts.append(f'<td class="col-exp">{_esc(row.get("Expected", ""))}</td>')
        parts.append(f'<td class="col-post">{_esc(row.get("PostAction", ""))}</td>')
        parts.append(f'<td class="col-obs">{_esc(row.get("ObservedText", ""))}</td>')
        status = row.get("Status", "")
        parts.append(
            f'<td class="col-status {_status_class(status)}">{_esc(status)}</td>'
        )
        parts.append('<td class="col-remark"></td>')
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "\n".join(parts)


# ── Public API ────────────────────────────────────────────────────────────────

def generate_html_report(
    results_by_sheet: Dict[str, List[Dict[str, Any]]],
    output_path: Optional[str] = None,
    reports_dir: Optional[str] = None,
    project_title: str = "Smart BU Testbench – Automated Test Report",
    scan_code: Optional[str] = None,
    sw_revision: Optional[str] = None,
) -> str:
    """
    Generate a self-contained HTML test report.

    Parameters
    ----------
    results_by_sheet:
        Mapping of sheet-name → list-of-row-dicts as returned by
        :func:`~AutomationScripts.report_generator.results_from_run`.
    output_path:
        Destination ``.html`` file path.  When *None*, a timestamped file
        is created inside *reports_dir*.
    reports_dir:
        Directory used when *output_path* is *None*.  Defaults to the
        current working directory.
    project_title:
        Title shown in the report header.

    Returns
    -------
    str
        Absolute path to the generated HTML file.
    """
    if reports_dir is None:
        reports_dir = os.getcwd()
    os.makedirs(reports_dir, exist_ok=True)

    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(reports_dir, f"{ts}_Test_Report.html")
    output_path = os.path.abspath(output_path)

    now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    # ── Summary counts ────────────────────────────────────────────────────────
    total = pass_c = fail_c = skip_c = 0
    for rows in results_by_sheet.values():
        for r in rows:
            s = (r.get("Status") or "").upper().strip()
            total += 1
            if s == "PASS":
                pass_c += 1
            elif s == "FAIL":
                fail_c += 1
            else:
                skip_c += 1

    # ── Build tab buttons and content panels ──────────────────────────────────
    tab_buttons: List[str] = []
    tab_panels:  List[str] = []

    for idx, (sheet_name, rows) in enumerate(results_by_sheet.items()):
        sid    = _safe_id(sheet_name)
        active = " active" if idx == 0 else ""
        tab_buttons.append(
            f'<button id="btn-{sid}" class="tab-btn{active}" '
            f"onclick=\"showTab('{sid}')\">"
            f"{_esc(sheet_name.strip())}</button>"
        )
        tab_panels.append(
            f'<div id="panel-{sid}" class="tab-panel{active}">'
            f"{_build_table(rows)}"
            f"</div>"
        )

    # ── Assemble the full document ────────────────────────────────────────────
    html_doc = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"<title>{_esc(project_title)}</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '<div class="report-header">\n'
        f"  <h1>{_esc(project_title)}</h1>\n"
        f'  <div class="meta">Generated: {_esc(now_str)}'
        + (f" &nbsp;|&nbsp; SW Revision: <strong>{_esc(sw_revision)}</strong>" if sw_revision else "")
        + (f" &nbsp;|&nbsp; 2D Scan: <strong>{_esc(scan_code)}</strong>" if scan_code else "")
        + "</div>\n"
        "</div>\n"
        '<div class="summary">\n'
        '  <div class="card total">'
        f'<div class="count">{total}</div>'
        '<div class="label">Total Tests</div></div>\n'
        '  <div class="card pass">'
        f'<div class="count">{pass_c}</div>'
        '<div class="label">Pass</div></div>\n'
        '  <div class="card fail">'
        f'<div class="count">{fail_c}</div>'
        '<div class="label">Fail</div></div>\n'
        '  <div class="card not-run">'
        f'<div class="count">{skip_c}</div>'
        '<div class="label">Not Run</div></div>\n'
        "</div>\n"
        '<div class="tabs-bar">\n'
        + "\n".join(tab_buttons)
        + "\n</div>\n"
        '<div class="content-area">\n'
        + "\n".join(tab_panels)
        + "\n</div>\n"
        '<div class="report-footer">'
        f"Smart BU Automated Test Report &mdash; {_esc(now_str)}"
        "</div>\n"
        f"<script>{_JS}</script>\n"
        "</body>\n"
        "</html>\n"
    )

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(html_doc)

    return output_path
