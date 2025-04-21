import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==== CONFIGURABLE CREDENTIALS ====
USERNAME = "seif.tolba"
PASSWORD = "basri4-kosnuz-gepVoh"

# ==== SETUP SELENIUM ====
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.page_load_strategy = "eager"

# Format the login URL
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/Scheduling/GroupSchedule.aspx"

# Initialize WebDriver & Open URL
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

wait = WebDriverWait(driver, 10)
# Wait for the schedule table to load
table = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_scdTbl")))

# ==== CONSTANTS & REGEX ====
default_period_names = ["First Period", "Second Period", "Third Period", "Fourth Period", "Fifth Period"]
weekdays = {"Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}

lecture_pattern = re.compile(r"\bH\d{1,2}\b")  # Matches "H13", "H16"
tut_pattern = re.compile(r"\b[CABD]\d+\.\d+\b")  # Matches "C5.104", "B7.02"

schedule_list = []

# ==== PARSE SCHEDULE TABLE ====
rows = table.find_elements(By.XPATH, "./tbody/tr") or table.find_elements(By.XPATH, "./tr")

for row in rows:
    cells = row.find_elements(By.XPATH, "./td")
    if len(cells) != 6:
        continue  # Skip rows that don't match expected format

    day_text = cells[0].text.strip()
    if day_text not in weekdays:
        continue  # Skip invalid rows

    day_entry = {"day": day_text, "periods": {}}

    for i in range(5):
        cell_text = cells[i+1].get_attribute("innerText").strip() or "Free"

        # Extract location
        lecture_match = lecture_pattern.search(cell_text)
        tut_match = tut_pattern.search(cell_text)

        if lecture_match:
            location = lecture_match.group()
        elif tut_match:
            location = tut_match.group()
        else:
            location = "Unknown" if cell_text != "Free" else "None"

        # Remove location from course text
        clean_course = re.sub(lecture_pattern, "", cell_text)
        clean_course = re.sub(tut_pattern, "", clean_course)
        clean_course = re.sub(r"\s+", " ", clean_course).strip()  # Remove extra spaces/tabs

        day_entry["periods"][default_period_names[i]] = {
            "course": clean_course,
            "location": location
        }

    schedule_list.append(day_entry)

# ==== SAVE OUTPUT ====
output_filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(schedule_list, f, indent=2, ensure_ascii=False)

driver.quit()
print(f"✅ Schedule extracted and saved to {output_filename}")
