import json
import re
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
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/Main/Notifications.aspx"

# Initialize WebDriver & Open URL
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

wait = WebDriverWait(driver, 10)

# ==== WAIT FOR NOTIFICATIONS TABLE TO LOAD ====
table_xpath = "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div/div/div/div"
table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))

# Fetch all notification rows and keep only the latest 10
rows = table.find_elements(By.XPATH, ".//tbody/tr")[:10]  # Get only the first 10 rows

notifications = []

for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    
    if len(cols) < 6:  # Ensure correct structure
        continue

    # Extract full message from the button
    try:
        button = cols[1].find_element(By.TAG_NAME, "button")
        full_message = button.get_attribute("data-body_text").strip()
    except:
        full_message = "No message available"

    # Extract title and remove "Notification System: "
    raw_title = cols[2].text.strip()
    title = re.sub(r"^Notification System:\s*", "", raw_title)  # Remove prefix

    date = cols[3].text.strip()  # Date
    staff = cols[4].text.strip()  # Staff name
    importance = cols[5].text.strip() if cols[5].text.strip() else "Normal"  # Importance

    # Store as a dictionary
    notifications.append({
        "Title": title,
        "Date": date,
        "Staff": staff,
        "Importance": importance,
        "Full_Message": full_message
    })

# ==== SAVE OUTPUT ====
output_filename = "notifications.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(notifications, f, indent=2, ensure_ascii=False)

driver.quit()
print(f"✅ Latest notifications extracted and saved to {output_filename}")
