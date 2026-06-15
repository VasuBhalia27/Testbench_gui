"""
M-Track Form Automation
Reads rows from a Google Sheet and submits them as new requests in m-track.
"""

import argparse
import json
import re
import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


CONFIG_FILE = Path(__file__).parent / "config.json"
WAIT_TIMEOUT = 20


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


# ── Google Sheets ─────────────────────────────────────────────────────────────

def _parse_sheet_url(value: str) -> tuple[str, str]:
    """Accept a full Google Sheets URL or a bare sheet ID. Returns (sheet_id, gid)."""
    if "spreadsheets/d/" in value:
        m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", value)
        sheet_id = m.group(1) if m else value
        g = re.search(r"[?&#]gid=(\d+)", value)
        gid = g.group(1) if g else "0"
    else:
        sheet_id = value
        gid = "0"
    return sheet_id, gid


def fetch_sheet_via_driver(driver: webdriver.Chrome, sheet_id: str, gid: str) -> pd.DataFrame:
    """Fetch Google Sheet CSV by reusing the browser's Google session cookies.
    No file download, no admin rights, no extra packages.
    Shows a Google login prompt in the browser window if not already signed in."""
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    # Navigate to docs.google.com — triggers Google login redirect if not signed in
    driver.get("https://docs.google.com")
    time.sleep(3)

    if "accounts.google.com" in driver.current_url:
        print("\n" + "=" * 60)
        print("ACTION REQUIRED: Sign into Google in the browser window.")
        print("The script will continue automatically after you log in.")
        print("=" * 60)
        try:
            WebDriverWait(driver, 300).until(
                lambda d: "accounts.google.com" not in d.current_url
            )
        except Exception:
            raise RuntimeError("Google login timed out (5 min).")
        # Return to docs.google.com so all relevant cookies are set
        driver.get("https://docs.google.com")
        time.sleep(2)

    # Copy auth cookies from the Selenium session into a requests session
    session = requests.Session()
    for ck in driver.get_cookies():
        session.cookies.set(ck["name"], ck["value"])

    print(f"Fetching Google Sheet: {export_url}")
    response = session.get(export_url, timeout=30)
    response.raise_for_status()

    return pd.read_csv(StringIO(response.text))


def load_sheet_data(config: dict, driver: webdriver.Chrome) -> pd.DataFrame:
    local_csv = config.get("local_csv_path", "")
    if local_csv:
        csv_path = Path(__file__).parent / local_csv
        print(f"Reading local CSV: {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        raw = config["google_sheet_id"]
        sheet_id, auto_gid = _parse_sheet_url(raw)
        gid = config.get("sheet_gid") or auto_gid
        df = fetch_sheet_via_driver(driver, sheet_id, gid)

    df = df.dropna(how="all")
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    return df


# ── Selenium helpers ──────────────────────────────────────────────────────────

# Persistent Chrome profile stored per-user — survives between runs so Google
# login is only needed once. Lives in the user's home folder, never in the repo.
_CHROME_PROFILE = Path.home() / ".mtrack_automation" / "chrome_profile"


def create_driver(headless: bool = False) -> webdriver.Chrome:
    _CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    # Reuse the same Chrome profile every run → Google session is preserved
    options.add_argument(f"--user-data-dir={_CHROME_PROFILE}")
    options.add_argument("--profile-directory=Default")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def wait_and_click(driver: webdriver.Chrome, xpaths: list, description: str) -> bool:
    """Try each xpath in turn until one is clickable, then click it."""
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    for xpath in xpaths:
        try:
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(0.3)
            element.click()
            print(f"  Clicked: {description}")
            return True
        except Exception:
            continue
    print(f"  WARNING: Could not find '{description}' with provided selectors.")
    return False


_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = "abcdefghijklmnopqrstuvwxyz"


def _ci(attr: str) -> str:
    """XPath 1.0 expression to lower-case an attribute or string for case-insensitive compare."""
    return f"translate(normalize-space({attr}),'{_UPPER}','{_LOWER}')"


def resolve_element(driver: webdriver.Chrome, selector_str: str):
    """
    Find a form element using a selector string:
      label:Text   -> find input/select/textarea linked to a matching label (case-insensitive)
      id:value     -> By.ID
      name:value   -> By.NAME
      css:value    -> By.CSS_SELECTOR
      xpath:value  -> By.XPATH
    """
    prefix, _, value = selector_str.partition(":")
    val_lower = value.lower()

    if prefix == "label":
        # Build a case-insensitive comparison expression for XPath 1.0
        ci_eq = f"{_ci('.')}='{val_lower}'"
        ci_contains = f"contains({_ci('.')},'{val_lower}')"

        # Try each strategy in order, return the first element found
        xpaths = [
            # 1. <label for="id"> exact match (case-insensitive) -> linked input
            f"//label[{ci_eq}]",
            # 2. label wraps or is adjacent to the input (case-insensitive contains)
            f"//label[{ci_contains}]",
            # 3. aria-label on the input itself
            f"//*[self::input or self::select or self::textarea]"
            f"[{_ci('@aria-label')}='{val_lower}']",
            # 4. placeholder on input
            f"//input[{_ci('@placeholder')}='{val_lower}']",
            # 5. Any element whose direct text matches (e.g. <th>, <span> acting as label)
            f"//*[{ci_eq}]/following::input[1]",
            f"//*[{ci_eq}]/following::select[1]",
            f"//*[{ci_eq}]/following::textarea[1]",
        ]

        for xpath in xpaths:
            try:
                els = driver.find_elements(By.XPATH, xpath)
                if not els:
                    continue
                el = els[0]
                tag = el.tag_name.lower()
                # If we landed on a <label>, resolve to its associated input
                if tag == "label":
                    for_id = el.get_attribute("for")
                    if for_id:
                        linked = driver.find_elements(By.ID, for_id)
                        if linked:
                            return linked[0]
                    # label wraps the input
                    child = el.find_elements(By.XPATH, ".//input | .//select | .//textarea")
                    if child:
                        return child[0]
                    # input immediately follows the label
                    sibling = driver.find_elements(
                        By.XPATH, f"({xpath})/following::input[1] | ({xpath})/following::select[1]"
                    )
                    if sibling:
                        return sibling[0]
                else:
                    return el
            except Exception:
                continue

        raise Exception(f"Could not find form element for label: '{value}'")

    wait = WebDriverWait(driver, 10)
    if prefix == "id":
        return wait.until(EC.presence_of_element_located((By.ID, value)))
    elif prefix == "name":
        return wait.until(EC.presence_of_element_located((By.NAME, value)))
    elif prefix == "css":
        return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, value)))
    elif prefix == "xpath":
        return wait.until(EC.presence_of_element_located((By.XPATH, value)))
    else:
        raise ValueError(f"Unknown selector prefix '{prefix}' in '{selector_str}'")


def fill_field(driver: webdriver.Chrome, element, value: str):
    """Fill a form field based on its tag type."""
    tag = element.tag_name.lower()
    if tag == "select":
        sel = Select(element)
        try:
            sel.select_by_visible_text(str(value))
        except Exception:
            sel.select_by_value(str(value))
    elif tag in ("input", "textarea"):
        input_type = (element.get_attribute("type") or "").lower()
        if input_type == "checkbox":
            current = element.is_selected()
            target = str(value).strip().lower() in ("true", "yes", "1", "on")
            if current != target:
                element.click()
        elif input_type == "radio":
            if not element.is_selected():
                element.click()
        else:
            element.clear()
            element.send_keys(str(value))
    else:
        element.clear()
        element.send_keys(str(value))


# ── Form discovery ────────────────────────────────────────────────────────────

def discover_form_fields(driver: webdriver.Chrome):
    """Print all discoverable form fields on the page."""
    print("\n=== Form Fields Discovered ===")
    fields = driver.find_elements(By.XPATH, "//input | //select | //textarea")
    rows = []
    for el in fields:
        tag = el.tag_name
        name = el.get_attribute("name") or ""
        el_id = el.get_attribute("id") or ""
        placeholder = el.get_attribute("placeholder") or ""
        label_text = ""
        if el_id:
            labels = driver.find_elements(By.XPATH, f"//label[@for='{el_id}']")
            if labels:
                label_text = labels[0].text.strip()
        rows.append({
            "tag": tag,
            "name": name,
            "id": el_id,
            "placeholder": placeholder,
            "label": label_text,
        })
        print(f"  tag={tag}  name='{name}'  id='{el_id}'  label='{label_text}'  placeholder='{placeholder}'")

    print("\nSuggested field_mapping entries (copy into config.json):")
    for r in rows:
        if r["label"]:
            print(f'  "Your Sheet Column": "label:{r["label"]}"')
        elif r["name"]:
            print(f'  "Your Sheet Column": "name:{r["name"]}"')
        elif r["id"]:
            print(f'  "Your Sheet Column": "id:{r["id"]}"')
    print("==============================\n")


# ── Main flow ─────────────────────────────────────────────────────────────────

def submit_row(driver: webdriver.Chrome, config: dict, row: pd.Series, row_index: int):
    """Navigate to the new request form, fill it, and submit for one data row."""
    buttons = config["button_selectors"]

    # Step 1: Navigate to the m-track URL
    driver.get(config["mtrack_url"])
    time.sleep(2)

    # Step 2: Click "Request Form" button (bottom right corner)
    if not wait_and_click(driver, buttons["request_form_button"], "Request Form"):
        print(f"  Row {row_index}: Skipping - could not open Request Form panel.")
        return False

    time.sleep(1)

    # Step 3: Click "+New Request"
    if not wait_and_click(driver, buttons["new_request_button"], "+New Request"):
        print(f"  Row {row_index}: Skipping - could not click New Request.")
        return False

    time.sleep(1.5)

    # Step 4: Fill form fields
    # Auto-map each sheet column to label:<column> by default.
    # field_mapping in config provides overrides for columns whose header differs from the form label.
    # skip_columns lists columns that exist in the sheet but have no matching form field.
    field_mapping = {
        k: v for k, v in config.get("field_mapping", {}).items()
        if not k.startswith("_")
    }
    skip_columns = {c for c in config.get("skip_columns", []) if not str(c).startswith("_")}

    for sheet_col in row.index:
        if sheet_col in skip_columns:
            print(f"  SKIP (configured): '{sheet_col}'")
            continue
        value = row[sheet_col]
        if pd.isna(value) or str(value).strip() == "":
            continue
        selector = field_mapping.get(sheet_col, f"label:{sheet_col}")
        try:
            element = resolve_element(driver, selector)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            fill_field(driver, element, value)
            print(f"  Filled '{sheet_col}' = '{value}'")
        except Exception as e:
            print(f"  ERROR: Could not fill '{sheet_col}' (selector: {selector}): {e}")

    time.sleep(0.5)

    # Step 5: Submit
    delay = config.get("submit_delay_seconds", 1)
    print(f"  Waiting {delay}s before submitting...")
    time.sleep(delay)

    if not wait_and_click(driver, buttons["submit_button"], "Submit"):
        print(f"  Row {row_index}: Could not click Submit button.")
        return False

    time.sleep(2)
    print(f"  Row {row_index}: Submitted successfully.")
    return True


def run_discover(config: dict):
    """Open m-track, navigate to the new request form, and print all fields."""
    driver = create_driver(headless=False)
    try:
        driver.get(config["mtrack_url"])
        time.sleep(2)
        wait_and_click(driver, config["button_selectors"]["request_form_button"], "Request Form")
        time.sleep(1)
        wait_and_click(driver, config["button_selectors"]["new_request_button"], "+New Request")
        time.sleep(1.5)
        discover_form_fields(driver)
        input("Press Enter to close the browser...")
    finally:
        driver.quit()


def run_probe(config: dict):
    """Open the new-request form and test which sheet columns can be matched to form fields."""
    field_mapping = {
        k: v for k, v in config.get("field_mapping", {}).items()
        if not k.startswith("_")
    }
    skip_columns = {c for c in config.get("skip_columns", []) if not str(c).startswith("_")}

    driver = create_driver(headless=False)
    try:
        df = load_sheet_data(config, driver)
        if df.empty:
            print("No data in sheet.")
            return
        driver.get(config["mtrack_url"])
        time.sleep(2)
        wait_and_click(driver, config["button_selectors"]["request_form_button"], "Request Form")
        time.sleep(1)
        wait_and_click(driver, config["button_selectors"]["new_request_button"], "+New Request")
        time.sleep(1.5)

        print("\n=== Field Probe Results ===")
        found, missing = [], []
        for col in df.columns:
            if col in skip_columns:
                print(f"  [SKIP]  {col}")
                continue
            selector = field_mapping.get(col, f"label:{col}")
            try:
                el = resolve_element(driver, selector)
                tag = el.tag_name
                el_id = el.get_attribute("id") or ""
                print(f"  [OK]    {col!r:45s}  -> <{tag}> id={el_id!r}  selector={selector!r}")
                found.append(col)
            except Exception:
                print(f"  [MISS]  {col!r:45s}  -> no element found for selector={selector!r}")
                missing.append(col)

        print(f"\nMatched: {len(found)}   Missing: {len(missing)}")
        if missing:
            print("\nFor missing columns, either:")
            print("  1. Add the column to 'skip_columns' in config.json if it has no form field.")
            print("  2. Add an override in 'field_mapping' pointing to the correct selector.")
            print("     Run --discover to see all available form fields.")
        input("\nPress Enter to close the browser...")
    finally:
        driver.quit()


def run_automation(config: dict, dry_run: bool = False, row_limit: int = None):
    driver = create_driver(headless=config.get("headless", False))
    try:
        df = load_sheet_data(config, driver)

        if df.empty:
            print("No data found in the Google Sheet.")
            return

        if row_limit:
            df = df.head(row_limit)
            print(f"Processing first {row_limit} row(s).")

        if dry_run:
            print("\n-- DRY RUN: showing sheet data only --")
            print(df.to_string())
            return

        success = 0
        failed = 0
        for idx, (_, row) in enumerate(df.iterrows(), start=1):
            print(f"\nProcessing row {idx}/{len(df)}...")
            ok = submit_row(driver, config, row, idx)
            if ok:
                success += 1
            else:
                failed += 1
    finally:
        driver.quit()

    print(f"\nDone. Success: {success}  Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(description="M-Track Form Automation")
    parser.add_argument(
        "--discover", action="store_true",
        help="Open m-track new request form and print all detectable fields"
    )
    parser.add_argument(
        "--probe", action="store_true",
        help="Test which sheet columns can be matched to form fields (no data submitted)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch sheet data and print it without opening the browser"
    )
    parser.add_argument(
        "--rows", type=int, default=None,
        help="Limit the number of rows to process (default: all)"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to a custom config JSON file"
    )
    args = parser.parse_args()

    global CONFIG_FILE
    if args.config:
        CONFIG_FILE = Path(args.config)

    config = load_config()

    if args.discover:
        run_discover(config)
    elif args.probe:
        run_probe(config)
    else:
        run_automation(config, dry_run=args.dry_run, row_limit=args.rows)


if __name__ == "__main__":
    main()
