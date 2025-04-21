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
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/Grade/CheckGrade_01.aspx"

# Initialize WebDriver & Open URL
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)
wait = WebDriverWait(driver, 10)

# Dictionary to store results
grades_data = {}

# Get total number of options
dropdown = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_smCrsLst")))
total_options = len(dropdown.find_elements(By.TAG_NAME, "option"))

for i in range(1, total_options):  # Skip first "Choose a Course" option
    dropdown = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_smCrsLst")))
    options = dropdown.find_elements(By.TAG_NAME, "option")
    
    option = options[i]
    course_name = option.text
    option_value = option.get_attribute("value")
    
    print(f"Processing: {course_name}")
    
    # Select course
    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", dropdown, option_value)
    
    # Wait for table to load
    wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_nttTr")))
    
    # Extract grades table
    rows = driver.find_elements(By.XPATH, "//table[@class='table table-bordered']/tbody/tr")[1:]  # Skip header
    grades = []
    
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 4:
            quiz_name = cols[0].text.strip()
            element_name = cols[1].text.strip()
            grade = cols[2].text.strip()
            instructor = cols[3].text.strip()
            grades.append({
                "quiz_name": quiz_name,
                "element_name": element_name,
                "grade": grade,
                "instructor": instructor
            })
    
    grades_data[course_name] = grades

# Save results as JSON
with open("grades.json", "w", encoding="utf-8") as f:
    json.dump(grades_data, f, indent=4, ensure_ascii=False)

print("Grades saved to grades.json")

# Close driver
driver.quit()
