from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
import time
import calendar
from datetime import datetime
import os
import getpass

# ==========================================
# CONFIG: Add all employee names here!
# ==========================================
EMPLOYEE_LIST = [
    "Anup Kumar", "Ezhilamuthan M", "Govind Sharma", "Gurpartap Singh", "Janvi Jain", 
    "Jashan Khurana", "Nakul Verma", "Poorab Saini", "Tanishq Goyal", "Yash Bhatnagar"
]
OUTPUT_FILE = "Team_Attendance.xlsx"

# Dynamic Calculation to lock columns strictly to the current date
now = datetime.now()
current_day = now.day  # Today's date boundary

# Create an absolute list of days ONLY up to today
ALL_MONTH_DAYS = [str(day) for day in range(1, current_day + 1)]

# ==========================================
# START CHROME WITH PERSISTENT PROFILE
# ==========================================
options = Options()
options.add_argument("--start-maximized")

# --- Force Chrome to enable the password manager ---
prefs = {
    "credentials_enable_service": True,
    "profile.password_manager_enabled": True
}
options.add_experimental_option("prefs", prefs)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
# ---------------------------------------------------

# Define a dedicated folder to save your Chrome session data securely
profile_path = os.path.join(os.getcwd(), "Selenium_Chrome_Profile")
options.add_argument(f"user-data-dir={profile_path}")

print("Launching Chrome with dedicated automation profile...")
driver = webdriver.Chrome(options=options)

# ==========================================
# SMART LOGIN / SESSION RESUME
# ==========================================
print("Establishing connection to U-Shin portal...")
# Always hit the main login URL first to set the 'customer_code' context
driver.get("https://www.myemploywise.com/asperm/servlet/ggs.erm.servlet.setup3.LoginS?customer_code=u-shin")

# Give the page a basic moment to load its elements
time.sleep(3) 

# Check if the login form is present on the screen
login_fields = driver.find_elements(By.ID, "User_Name")

if login_fields:
    print("Login screen detected. Waiting for Chrome Password Manager to auto-fill...")
    saved_username = ""
    
    # POLL THE FIELD: Check every 1 second (up to 10 seconds)
    for _ in range(10):
        try:
            # Force human interaction: Click the field and send an invisible key to trigger Chrome's DOM update
            login_fields[0].click()
            login_fields[0].send_keys(Keys.NULL)
        except Exception:
            pass
            
        saved_username = login_fields[0].get_attribute("value")
        if saved_username:
            break  # Chrome officially committed the text! Break out of the waiting loop.
        time.sleep(1)
    
    if saved_username:
        print(f"\n✅ Auto-filled credentials detected for user: {saved_username}. Auto-submitting...")
        driver.find_element(By.ID, "loginButton").click()
        time.sleep(5) # Wait for the login to process
    else:
        print("\n--- Session expired or first run. Secure Login Required ---")
        EMPLOYEE_CODE = input("Enter your Employee Code: ")
        EMPLOYEE_PASS = getpass.getpass("Enter your Password (typing will be hidden): ")

        # Force clear and type Employee Code
        login_fields[0].send_keys(Keys.CONTROL + "a")
        login_fields[0].send_keys(Keys.DELETE)
        login_fields[0].send_keys(EMPLOYEE_CODE)

        # Force clear and type Password
        pass_field = driver.find_element(By.ID, "Password")
        pass_field.send_keys(Keys.CONTROL + "a")
        pass_field.send_keys(Keys.DELETE)
        pass_field.send_keys(EMPLOYEE_PASS)

        # Login
        driver.find_element(By.ID, "loginButton").click()
        
        print("\nProcessing login... If Chrome asks to save your password, click 'SAVE' now!")
        # Pausing for 5 seconds to give you time to click the Chrome "Save Password" popup
        time.sleep(5) 
else:
    print("\n✅ Active session found! Skipped login.")

# Now that we are officially authenticated, jump to the calendar page
print("Navigating to the Calendar page...")
driver.get("https://www.myemploywise.com/asperm/servlet/ggs.erm.servlet.setup6.LeaveProcessS?mode=leave_mycalendar")
time.sleep(3)

all_team_rows = []  # Master list to store rows for all employees
scraped_names = set()

# ==========================================
# LOOP THROUGH EACH EMPLOYEE
# ==========================================
try:
    for employee in EMPLOYEE_LIST:
        print(f"Navigating to calendar for {employee}...")
        
        try:
            # Dynamically target the employee's name in the sidebar
            xpath_target = f"//div[@id='myteam']//font[contains(text(), '{employee}')]"
            
            # Wait up to 10 seconds for the employee name to become clickable
            employee_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_target))
            )
            
            # Click the name to load their calendar
            employee_link.click()
            
            # Give the calendar table a moment to fetch and render the new data
            time.sleep(3) 
            
        except Exception as e:
            print(f"⚠️ Could not locate or click {employee} in the sidebar. Skipping to next.")
            continue # Skips to the next employee in the loop
        
        records = []
        processed = set()
        all_elements = driver.find_elements(By.XPATH, "//div | //span | //td | //p")

        for elem in all_elements:
            try:
                txt = elem.text.strip()
                if not txt or len(txt) > 200:
                    continue

                upper = txt.upper()
                
                # Broaden the detection to find "Out on Work" even if there are no timeblocks
                has_time = bool(re.search(r'\d{1,2}:\d{2}[ap]m\s*-\s*\d{1,2}:\d{2}[ap]m', txt, re.IGNORECASE))
                has_keywords = any(k in upper for k in ["PRESENT", "ABSENT", "LEAVE", "WEEKLY OFF", "OUT ON WORK"])
                
                if not (has_time or has_keywords):
                    continue

                if txt in processed:
                    continue
                processed.add(txt)

                status = ""
                if "PRESENT" in upper: status = "PRESENT"
                elif "ABSENT" in upper: status = "ABSENT"
                elif "LEAVE" in upper: status = "LEAVE"
                elif "WEEKLY OFF" in upper: status = "WEEKLY OFF"
                
                if "OUT ON WORK" in upper:
                    status = (status + " & OUT ON WORK") if status else "OUT ON WORK"

                date_match = re.search(r'(?:PRESENT|ABSENT|LEAVE|OFF|WORK).*?(\d{1,2})', txt, re.IGNORECASE)
                if not date_match:
                    date_match = re.search(r'\b(\d{1,2})\b', txt)

                if date_match:
                    date = date_match.group(1)
                    if int(date) > current_day:
                        continue
                else:
                    continue

                time_match = re.search(r'(\d{1,2}:\d{2}[ap]m)\s*-\s*(\d{1,2}:\d{2}[ap]m)', txt, re.IGNORECASE)
                in_time = time_match.group(1) if time_match else ""
                out_time = time_match.group(2) if time_match else ""

                records.append({
                    "Name": employee,
                    "Date": date,
                    "Status": status,
                    "In Time": in_time,
                    "Out Time": out_time
                })
            except Exception:
                pass

        if records:
            df = pd.DataFrame(records)
            df["Date"] = pd.to_numeric(df["Date"], errors='coerce')
            df = df.dropna(subset=["Date"]).astype({"Date": int}).sort_values("Date")
            
            def find_best_value(series):
                non_empty = [str(i) for i in series if str(i).strip() != ""]
                if not non_empty:
                    return ""
                with_time = [i for i in non_empty if ":" in i]
                return with_time[0] if with_time else non_empty[0]

            df_cleaned = df.groupby(["Name", "Date"]).agg({
                "Status": find_best_value,
                "In Time": find_best_value,
                "Out Time": find_best_value
            }).reset_index()

            horizontal_row = {"Name": employee, "IsSkipped": False}
            for _, row in df_cleaned.iterrows():
                day_num = row["Date"]
                status = row["Status"]
                in_t = row["In Time"]
                out_t = row["Out Time"]
                
                if in_t and out_t:
                    cell_value = f"{status} ({in_t} - {out_t})"
                elif status:
                    cell_value = status
                else:
                    cell_value = "N/A"
                    
                horizontal_row[str(day_num)] = cell_value
            
            all_team_rows.append(horizontal_row)
            scraped_names.add(employee)
            print(f"✅ Successfully collected data for {employee}!")
        else:
            print(f"❌ Failed to find any data for {employee}.")

# ==========================================
# FINAL EXPORT & GRAPHICS GENERATION
# ==========================================
finally:
    print("\n==========================================")
    print("Executing final data export routine...")
    print("==========================================")
    
    skipped_names = set()
    for employee in EMPLOYEE_LIST:
        if employee not in scraped_names:
            all_team_rows.append({"Name": employee, "IsSkipped": True})
            skipped_names.add(employee)

    if all_team_rows:
        df_final = pd.DataFrame(all_team_rows)
        
        for day in ALL_MONTH_DAYS:
            if day not in df_final.columns:
                df_final[day] = None
                
        fixed_headers = ["Name"] + ALL_MONTH_DAYS
        df_excel_out = df_final.reindex(columns=fixed_headers)
        
        try:
            df_excel_out.to_excel(OUTPUT_FILE, index=False)
            print(f"\n🎉 Success! Consolidated sheet saved as: {OUTPUT_FILE}")
        except PermissionError:
            fallback = f"Team_Attendance_{int(time.time())}.xlsx"
            df_excel_out.to_excel(fallback, index=False)
            print(f"\n⚠️ File locked! Data safely saved to backup: {fallback}")

        # ------------------------------------------
        # VISUALIZATION LOGIC
        # ------------------------------------------
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import numpy as np
            from matplotlib.colors import ListedColormap

            print("\n📊 Generating modified visual arrival dashboard...")

            df_long = df_final.melt(id_vars=["Name", "IsSkipped"], value_vars=ALL_MONTH_DAYS, var_name="Date", value_name="Details")
            
            def evaluate_punch_in(row_item):
                if row_item["IsSkipped"] == True:
                    return 5  # White block
                    
                cell = row_item["Details"]
                if pd.isna(cell):
                    return 0
                    
                cell_str = str(cell).upper()
                
                # Identify "Out on Work" -> Assign Code 6 (Purple)
                if "OUT ON WORK" in cell_str:
                    return 6
                
                # Standard Evaluation for Presence
                if "PRESENT" not in cell_str:
                    return 0
                
                time_match = re.search(r'(\d{1,2}:\d{2})\s*([ap]m)', cell_str, re.IGNORECASE)
                if not time_match:
                    return 0
                    
                time_str = f"{time_match.group(1)} {time_match.group(2).upper()}"
                try:
                    actual_time = datetime.strptime(time_str, "%I:%M %p").time()
                    limit_840 = datetime.strptime("08:40 AM", "%I:%M %p").time()
                    limit_900 = datetime.strptime("09:00 AM", "%I:%M %p").time()
                    
                    if actual_time <= limit_840:
                        return 1  # Green
                    elif actual_time <= limit_900:
                        return 2  # Blue
                    else:
                        return 3  # Red
                except Exception:
                    return 0

            df_long["Status_Code"] = df_long.apply(evaluate_punch_in, axis=1)
            df_long["Date"] = pd.to_numeric(df_long["Date"])

            df_pivot = df_long.pivot(index="Name", columns="Date", values="Status_Code").fillna(0)
            df_pivot = df_pivot.reindex(columns=sorted(df_pivot.columns))

            # Create a parallel pivot table just for extracting the time text
            df_details_pivot = df_long.pivot(index="Name", columns="Date", values="Details").fillna("")
            df_details_pivot = df_details_pivot.reindex(columns=sorted(df_pivot.columns))

            for idx, row in df_pivot.iterrows():
                if idx in skipped_names:
                    continue
                    
                row_str = "".join(row.values.astype(int).astype(str))
                
                # Rule 1: 12+ consecutive days of absence -> Black / ✈️
                for match in re.finditer(r'0{12,}', row_str):
                    start, end = match.start(), match.end()
                    df_pivot.iloc[df_pivot.index.get_loc(idx), start:end] = 4
                    
                # Rule 2: 3+ consecutive days of "Out on Work" (Code 6) -> Black / ✈️
                for match in re.finditer(r'6{3,}', row_str):
                    start, end = match.start(), match.end()
                    df_pivot.iloc[df_pivot.index.get_loc(idx), start:end] = 4

            color_palette = ["#f1c40f", "#2ecc71", "#3498db", "#e74c3c", "#1a1a1a", "#ffffff", "#9b59b6"]
            custom_cmap = ListedColormap(color_palette)

            # Increased figure size so the multiline text fits comfortably in the boxes
            plt.figure(figsize=(max(12, current_day * 0.8), max(8, len(df_pivot) * 0.75)))
            
            annot_mask = np.empty(df_pivot.shape, dtype=object)
            for r_idx in range(df_pivot.shape[0]):
                for c_idx in range(df_pivot.shape[1]):
                    val = df_pivot.iloc[r_idx, c_idx]
                    details_text = str(df_details_pivot.iloc[r_idx, c_idx])
                    
                    if val == 4:
                        annot_mask[r_idx, c_idx] = "✈️"
                    elif val == 6:
                        annot_mask[r_idx, c_idx] = "Out"
                    elif val == 0:
                        annot_mask[r_idx, c_idx] = "Leave"
                    elif val in [1, 2, 3]:
                        # Extract the in-time and out-time specifically to build a small stack of text
                        time_match = re.search(r'(\d{1,2}:\d{2})\s*([ap]m)\s*-\s*(\d{1,2}:\d{2})\s*([ap]m)', details_text, re.IGNORECASE)
                        if time_match:
                            in_time_str = f"{time_match.group(1)} {time_match.group(2).upper()}"
                            out_time_str = f"{time_match.group(3)} {time_match.group(4).upper()}"
                            # Stack them using a newline character
                            annot_mask[r_idx, c_idx] = f"{in_time_str}\n{out_time_str}"
                        else:
                            annot_mask[r_idx, c_idx] = "In" # Fallback if times somehow aren't in details
                    else:
                        annot_mask[r_idx, c_idx] = ""

            ax = sns.heatmap(
                df_pivot, 
                cmap=custom_cmap, 
                annot=annot_mask, 
                fmt="", 
                annot_kws={"size": 6.5, "weight": "bold"}, # Reduced default text size slightly to fit times
                linewidths=1.5, 
                linecolor="#e0e0e0", 
                cbar=False, 
                vmin=0, 
                vmax=6
            )

            # Iterating through texts to dynamically resize and color based on content
            for text in ax.texts:
                t_val = text.get_text()
                if t_val == "✈️":
                    text.set_color("white")
                    text.set_size(14)
                elif t_val == "Out":
                    text.set_color("white")
                    text.set_size(10)
                elif t_val == "Leave":
                    text.set_color("#2c3e50")
                    text.set_size(8)
                elif "\n" in t_val: # This applies to our stacked time annotations
                    text.set_color("#1c2833") # Very dark grey for best readability
                    text.set_size(7)

            plt.title(f"Team Punctuality & Attendance Dashboard (1-{current_day} {now.strftime('%B %Y')})", fontsize=16, fontweight='bold', pad=20)
            plt.xlabel("Day of the Month", fontsize=12, labelpad=10)
            plt.ylabel("Employee Name", fontsize=12)
            plt.xticks(rotation=0)
            plt.yticks(rotation=0)

            from matplotlib.patches import Patch
            legend_labels = [
                Patch(facecolor="#2ecc71", edgecolor="#7f8c8d", label="Logged In Before 8:40 AM (Green)"),
                Patch(facecolor="#3498db", edgecolor="#7f8c8d", label="Logged In 8:40 AM - 9:00 AM (Blue)"),
                Patch(facecolor="#e74c3c", edgecolor="#7f8c8d", label="Logged In After 9:00 AM (Red)"),
                Patch(facecolor="#f1c40f", edgecolor="#7f8c8d", label="Blank / Regular Leave (Yellow)"),
                Patch(facecolor="#9b59b6", edgecolor="#7f8c8d", label="Out on Work < 3 Days (Purple)"),
                Patch(facecolor="#1a1a1a", edgecolor="#7f8c8d", label="Onsite Visit (✈️) / Long Absence"),
                Patch(facecolor="#ffffff", edgecolor="#b0b0b0", label="Skipped / No Scanned Data (White)")
            ]
            ax.legend(handles=legend_labels, loc='upper left', bbox_to_anchor=(1.01, 1), title="Updated Status Key")

            plt.tight_layout()

            chart_filename = "Team_Punctuality_Heatmap.png"
            plt.savefig(chart_filename, dpi=300)
            print(f"🎨 Custom Dashboard successfully generated and saved to: {chart_filename}")
            plt.show()

        except ImportError:
            print("\n❌ Rendering dependencies are missing. Please run: pip install matplotlib seaborn openpyxl")
        except Exception as e:
            print(f"\n❌ Graphics compilation error occurred: {e}")

    else:
        print("\n❌ No data collected for any employees.")

print("\nClosing automated browser window...")
driver.quit()