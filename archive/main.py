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
chrome_options.add_argument("--headless=new")  # Faster headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # No images
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.page_load_strategy = "eager"  # Loads only DOM, skips scripts

# Format the login URL
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/index.aspx"

# Open browser
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

# Wait for elements (max 5s, polling every 0.1s)
wait = WebDriverWait(driver, 5, poll_frequency=0.1)
elements = wait.until(
    EC.presence_of_all_elements_located(
        (By.XPATH, "//span[contains(@id, 'ContentPlaceHolderright_ContentPlaceHoldercontent_Label')]")
    )
)

# Extract text from elements
data = {elem.get_attribute("id").split("_")[-1]: elem.text.strip() for elem in elements}

# Assign extracted values to variables
student_name = data.get("LabelFullName", "N/A")
student_id = data.get("LabelUniqAppNo", "N/A")
student_mail = data.get("LabelMail", "N/A")
study_group = data.get("Labelsg", "N/A")

# Close browser
driver.quit()

# Print extracted student details
print(f"✅ Student Name: {student_name}")
print(f"✅ Student ID: {student_id}")
print(f"✅ Student Mail: {student_mail}")
print(f"✅ Study Group: {study_group}")
