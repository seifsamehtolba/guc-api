import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

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
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/Attendance/ClassAttendance_ViewStudentAttendance_001.aspx"

# Initialize WebDriver & Open URL
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

wait = WebDriverWait(driver, 10)

# Function to extract attendance data
def extract_attendance_data():
    attendance_data = []
    table = driver.find_element(By.ID, "DG_StudentCourseAttendance")
    rows = table.find_elements(By.TAG_NAME, "tr")
    
    for row in rows[1:]:  # Skip the header row
        cells = row.find_elements(By.TAG_NAME, "td")
        row_number = cells[0].text
        attendance_status = cells[1].text
        session_description = cells[2].text
        attendance_data.append({
            "RowNumber": row_number,
            "Attendance": attendance_status,
            "SessionDsc": session_description
        })
    
    return attendance_data

# Locate the dropdown element
dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_DDL_Courses"))

# Get all options from the dropdown (skip the first one which is "[Choose Course]")
options = dropdown.options[1:]

# Iterate through each option
for i in range(len(options)):
    # Re-fetch the dropdown and options after each selection
    dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_DDL_Courses"))
    options = dropdown.options[1:]
    
    # Get the current option
    option = options[i]
    course_name = option.text
    course_value = option.get_attribute("value")
    
    print(f"Fetching attendance for: {course_name}")
    
    # Select the course
    dropdown.select_by_value(course_value)
    
    # Wait for the attendance table to update
    wait.until(EC.presence_of_element_located((By.ID, "DG_StudentCourseAttendance")))
    
    # Extract attendance data
    attendance_data = extract_attendance_data()
    
    # Print or save the attendance data
    print(json.dumps(attendance_data, indent=4))
    print("-" * 50)

# Close the browser
driver.quit()