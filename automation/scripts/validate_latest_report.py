"""
Simple validator for latest Excel report in automation/reports/output
- Finds the newest non-temp .xlsx
- Reads the first worksheet (LED or Test Results)
- For each data row tries to parse MeasuredValue (numeric) and Expected (numeric ranges like "2.76 V to 3.83 V")
- Prints PASS/FAIL for numeric comparisons

Run: python automation/scripts/validate_latest_report.py
"""
from pathlib import Path
import re
from openpyxl import load_workbook

OUT = Path(__file__).parent.parent / "reports" / "output"

def find_latest_report(out_dir: Path):
    files = [f for f in out_dir.glob("*.xlsx") if not f.name.startswith("~$")]
    if not files:
        return None
    files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0]


def parse_number(s: str):
    if s is None:
        return None
    try:
        return float(str(s).strip())
    except Exception:
        # remove commas and try
        try:
            return float(str(s).replace(',', '').strip())
        except Exception:
            return None


def parse_expected_range(s: str):
    if not s:
        return None
    s = str(s)
    # find all floats
    nums = re.findall(r"[-+]?[0-9]*\.?[0-9]+", s)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    if ">=" in s or ">" in s:
        m = re.search(r">=\s*([-+]?[0-9]*\.?[0-9]+)", s)
        if not m:
            m = re.search(r">\s*([-+]?[0-9]*\.?[0-9]+)", s)
        if m:
            return float(m.group(1)), None
    return None


def validate_sheet(ws):
    # attempt to find header row by searching first 5 rows for 'Measured' or 'MeasuredValue'
    header_row = 1
    headers = [str(c.value).strip().lower() if c.value is not None else '' for c in ws[1]]
    # locate columns
    def find_col(names):
        for i, h in enumerate(headers, start=1):
            for n in names:
                if n in h:
                    return i
        return None

    tc_col = find_col(["testcase", "test case id", "testcaseid"])
    meas_col = find_col(["measured", "measuredvalue", "observed result", "measuredvalue"])
    expected_col = find_col(["expected", "expected result"])
    status_col = find_col(["status"])

    if not meas_col or not expected_col:
        print("Could not find Measured or Expected columns. Headers:", headers)
        return

    print(f"Using columns - Measured: {meas_col}, Expected: {expected_col}, Status: {status_col}")

    results = []
    for r in range(2, ws.max_row + 1):
        tc = ws.cell(row=r, column=tc_col).value if tc_col else f"row{r}"
        meas = ws.cell(row=r, column=meas_col).value
        exp = ws.cell(row=r, column=expected_col).value
        # detect mV string and normalize to V for comparison
        meas_raw = str(meas) if meas is not None else ''
        meas_num = parse_number(meas)
        if meas_raw.lower().find('mv') != -1:
            # convert mV to V
            if meas_num is not None:
                meas_num = meas_num / 1000.0
        exp_range = parse_expected_range(exp)
        verdict = "SKIP"
        reason = ""
        if meas_num is None:
            verdict = "NO_MEASURED"
            reason = f"Measured not numeric ({meas})"
        elif exp_range is None:
            verdict = "NO_EXPECTED"
            reason = f"Expected not numeric-range ({exp})"
        else:
            low, high = exp_range
            if low is not None and high is not None:
                if low <= meas_num <= high:
                    verdict = "PASS"
                else:
                    verdict = "FAIL"
                    reason = f"{meas_num} not in [{low}, {high}]"
            elif low is not None and high is None:
                if meas_num >= low:
                    verdict = "PASS"
                else:
                    verdict = "FAIL"
                    reason = f"{meas_num} < {low}"
            else:
                verdict = "UNCERTAIN"
        results.append((tc, meas_num, exp, verdict, reason))

    # print summary
    for tc, meas_num, exp, verdict, reason in results:
        print(f"{tc}: {verdict}", end='')
        if reason:
            print(f" - {reason}")
        else:
            print()

    passed = sum(1 for r in results if r[3] == 'PASS')
    failed = sum(1 for r in results if r[3] == 'FAIL')
    print(f"\nSummary: {len(results)} rows, PASS={passed}, FAIL={failed}")


if __name__ == '__main__':
    latest = find_latest_report(OUT)
    if not latest:
        print("No report found in", OUT)
        raise SystemExit(1)
    print("Validating:", latest)
    wb = load_workbook(filename=str(latest), read_only=True)
    ws = wb.worksheets[0]
    print('Sheet:', ws.title)
    validate_sheet(ws)
    wb.close()
