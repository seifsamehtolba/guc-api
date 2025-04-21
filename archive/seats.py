import json
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
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/Exam/ViewExamSeat_01.aspx"

# Initialize WebDriver & Open URL
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

wait = WebDriverWait(driver, 10)

# ==== WAIT FOR EXAM TABLE TO LOAD ====
table_xpath = "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/table"
table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))

# Fetch all rows except the header row
rows = table.find_elements(By.XPATH, ".//tbody/tr")[1:]  # Skip headers

exam_details = []

for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    
    # Extract raw data
    course_name = cols[0].text.strip()
    exam_day = cols[1].text.strip()
    raw_date = cols[2].text.strip()
    raw_start_time = cols[3].text.strip()
    raw_end_time = cols[4].text.strip()
    hall = cols[5].text.strip()
    seat = cols[6].text.strip()
    exam_type = cols[7].text.strip()

    # ==== FORMAT DATE ====
    try:
        parsed_date = datetime.strptime(raw_date, "%d - %B - %Y")
        formatted_date = parsed_date.strftime("%B %d, %Y")  # Example: "April 3, 2025"
    except ValueError:
        formatted_date = raw_date  # Fallback

    # ==== FORMAT TIME (12-hour format) ====
    def format_time(raw_time):
        try:
            return datetime.strptime(raw_time, "%I:%M:%S %p").strftime("%I:%M %p")  # Example: "01:45 PM"
        except ValueError:
            return raw_time  # Fallback

    start_time = format_time(raw_start_time)
    end_time = format_time(raw_end_time)

    # ==== STORE AS DICTIONARY ====
    exam_details.append({
        "Course": course_name,
        "Exam_Day": exam_day,
        "Date": formatted_date,
        "Start_Time": start_time,
        "End_Time": end_time,
        "Hall": hall,
        "Seat": seat,
        "Exam_Type": exam_type
    })

# ==== SAVE OUTPUT ====
output_filename = f"exam_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(exam_details, f, indent=2, ensure_ascii=False)

driver.quit()
print(f"✅ Exam schedule extracted and saved to {output_filename}")
