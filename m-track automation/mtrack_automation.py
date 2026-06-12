"""
M-Track Form Automation
Reads rows from a Google Sheet and submits them as new requests in m-track.
"""

import argparse
import json
import sys
import time
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

def fetch_sheet_public(sheet_id: str, gid: str) -> pd.DataFrame:
    """Fetch sheet via public CSV export (works for publicly shared sheets)."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    print(f"Fetching Google Sheet: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    from io import StringIO
    df = pd.read_csv(StringIO(response.text))
    return df


def fetch_sheet_service_account(sheet_id: str, credentials_file: str) -> pd.DataFrame:
    """Fetch sheet using a Google service account JSON key."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("Install gspread and google-auth: pip install gspread google-auth")
        sys.exit(1)

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)


def load_sheet_data(config: dict) -> pd.DataFrame:
    sheet_id = config["google_sheet_id"]
    gid = config.get("sheet_gid", "0")

    if config.get("use_service_account"):
        creds = config.get("credentials_file", "credentials/service_account.json")
        creds_path = Path(__file__).parent / creds
        df = fetch_sheet_service_account(sheet_id, str(creds_path))
    else:
        df = fetch_sheet_public(sheet_id, gid)

    # Drop completely empty rows
    df = df.dropna(how="all")
    print(f"Loaded {len(df)} rows from Google Sheet")
    print(f"Columns: {list(df.columns)}")
    return df


# ── Selenium helpers ──────────────────────────────────────────────────────────

def create_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
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


def resolve_element(driver: webdriver.Chrome, selector_str: str):
    """
    Find a form element using a selector string:
      label:Text   -> find input associated with <label> containing Text
      id:value     -> By.ID
      name:value   -> By.NAME
      css:value    -> By.CSS_SELECTOR
      xpath:value  -> By.XPATH
    """
    wait = WebDriverWait(driver, 10)
    prefix, _, value = selector_str.partition(":")

    if prefix == "label":
        # Find input/select/textarea linked to a label
        xpath = (
            f"//label[normalize-space()='{value}']/following::input[1] | "
            f"//label[normalize-space()='{value}']/following::select[1] | "
            f"//label[normalize-space()='{value}']/following::textarea[1] | "
            f"//label[contains(.,'{value}')]/..//input | "
            f"//label[contains(.,'{value}')]/..//select | "
            f"//label[contains(.,'{value}')]/..//textarea"
        )
        return wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    elif prefix == "id":
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

    # Step 4: Fill form fields from field_mapping
    field_mapping = {
        k: v for k, v in config.get("field_mapping", {}).items()
        if not k.startswith("_")
    }

    if not field_mapping:
        print("  WARNING: field_mapping in config.json is empty.")
        print("  Run with --discover to detect available form fields, then update config.json.")
        discover_form_fields(driver)
        return False

    for sheet_col, selector in field_mapping.items():
        if sheet_col not in row.index:
            print(f"  SKIP: Sheet has no column '{sheet_col}'")
            continue
        value = row[sheet_col]
        if pd.isna(value) or str(value).strip() == "":
            print(f"  SKIP: Empty value for '{sheet_col}'")
            continue
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


def run_automation(config: dict, dry_run: bool = False, row_limit: int = None):
    df = load_sheet_data(config)

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

    driver = create_driver(headless=config.get("headless", False))
    success = 0
    failed = 0
    try:
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
    else:
        run_automation(config, dry_run=args.dry_run, row_limit=args.rows)


if __name__ == "__main__":
    main()
