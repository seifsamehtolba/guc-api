import json
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
URL = f"https://{USERNAME}:{PASSWORD}@apps.guc.edu.eg/student_ext/Financial/BalanceView_001.aspx"

# Initialize WebDriver & Open URL
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

wait = WebDriverWait(driver, 10)

# Dictionary to store the output
output = {
    "Payment Requests": []
}

# Wait for the page to load and ensure the user info is present
try:
    # Wait for the user information section to load
    wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_lbl_Name")))

    # Extract Payment Requests
    payment_table = driver.find_element(By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_DG_PaymentRequest")
    rows = payment_table.find_elements(By.TAG_NAME, "tr")

    # Process the first payment request (skip the header row)
    if len(rows) > 1:
        cols = rows[1].find_elements(By.TAG_NAME, "td")

        # Extract payment details
        payment_details = {
            "Reference": cols[0].text,
            "Payment Description": cols[1].text,
            "Currency": cols[2].text,
            "Amount": cols[3].text,
            "Due Date": cols[4].text,
            "Payment Link": cols[5].find_element(By.TAG_NAME, "a").get_attribute("href")
        }

        # If the payment link is a JavaScript postback, simulate the click
        if payment_details["Payment Link"].startswith("javascript:"):
            pay_button = cols[5].find_element(By.TAG_NAME, "a")
            pay_button.click()  # Simulate the click

            # Wait for the new page to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Update the Payment Link with the resulting URL
            payment_details["Payment Link"] = driver.current_url

        # Add payment details to the output
        output["Payment Requests"].append(payment_details)

    else:
        output["Payment Requests"].append({"Message": "No payment requests found."})

except Exception as e:
    output["Error"] = str(e)

finally:
    # Close the browser
    driver.quit()

# Convert the output to JSON and print it
print(json.dumps(output, indent=4))