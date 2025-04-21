from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import uvicorn

app = FastAPI()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.page_load_strategy = "eager"
    return webdriver.Chrome(options=chrome_options)

def build_auth_url(base_url: str, username: str, password: str) -> str:
    protocol, rest = base_url.split("://")
    return f"{protocol}://{username}:{password}@{rest}"

def get_student_info(username: str, password: str):
    driver = get_driver()
    base_url = "https://apps.guc.edu.eg/student_ext/index.aspx"
    auth_url = build_auth_url(base_url, username, password)
    driver.get(auth_url)
    wait = WebDriverWait(driver, 5, poll_frequency=0.1)
    elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//span[contains(@id, 'ContentPlaceHolderright_ContentPlaceHoldercontent_Label')]")
        )
    )
    data = {elem.get_attribute("id").split("_")[-1]: elem.text for elem in elements}
    driver.quit()
    return {
        "Student_Name": data.get("LabelFullName", "N/A"),
        "Student_ID": data.get("LabelUniqAppNo", "N/A"),
        "Student_Mail": data.get("LabelMail", "N/A"),
        "Study_Group": data.get("Labelsg", "N/A")
    }

def get_notifications(username: str, password: str):
    driver = get_driver()
    base_url = "https://apps.guc.edu.eg/student_ext/Main/Notifications.aspx"
    auth_url = build_auth_url(base_url, username, password)
    driver.get(auth_url)
    wait = WebDriverWait(driver, 10)
    table_xpath = "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div/div/div/div"
    table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    rows = table.find_elements(By.XPATH, ".//tbody/tr")[:10]
    notifications = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 6:
            continue
        button = cols[1].find_element(By.TAG_NAME, "button")
        title = cols[2].text.strip()
        date = cols[3].text.strip()
        staff = cols[4].text.strip()
        importance = cols[5].text.strip() if cols[5].text.strip() else "Normal"
        full_message = button.get_attribute("data-body_text").strip()
        notifications.append({
            "Title": title,
            "Date": date,
            "Staff": staff,
            "Importance": importance,
            "Full_Message": full_message
        })
    driver.quit()
    return notifications

def get_schedule_data(username: str, password: str):
    driver = get_driver()
    base_url = "https://apps.guc.edu.eg/student_ext/Scheduling/GroupSchedule.aspx"
    auth_url = build_auth_url(base_url, username, password)
    driver.get(auth_url)
    wait = WebDriverWait(driver, 10)
    table = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_scdTbl")))
    rows = table.find_elements(By.XPATH, "./tbody/tr")
    if not rows:
        rows = table.find_elements(By.XPATH, "./tr")
    default_period_names = ["First Period", "Second Period", "Third Period", "Fourth Period", "Fifth Period"]
    weekdays = {"Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
    schedule_list = []
    for row in rows:
        cells = row.find_elements(By.XPATH, "./td")
        if len(cells) != 6:
            continue
        day_text = cells[0].text.strip()
        if day_text not in weekdays:
            continue
        day_entry = {"day": day_text, "periods": {}}
        for i in range(5):
            cell_text = cells[i+1].get_attribute("innerText").strip()
            if not cell_text:
                cell_text = "Free"
            day_entry["periods"][default_period_names[i]] = cell_text
        schedule_list.append(day_entry)
    driver.quit()
    return schedule_list

def get_exam_seats(username: str, password: str):
    driver = get_driver()
    base_url = "https://apps.guc.edu.eg/student_ext/Exam/ViewExamSeat_01.aspx"
    auth_url = build_auth_url(base_url, username, password)
    driver.get(auth_url)
    wait = WebDriverWait(driver, 10)
    table_xpath = "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/table"
    table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    rows = table.find_elements(By.XPATH, ".//tbody/tr")[1:]
    exam_details = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 8:
            continue
        course_name = cols[0].text.strip()
        exam_day = cols[1].text.strip()
        raw_date = cols[2].text.strip()
        raw_start_time = cols[3].text.strip()
        raw_end_time = cols[4].text.strip()
        hall = cols[5].text.strip()
        seat = cols[6].text.strip()
        exam_type = cols[7].text.strip()
        try:
            parsed_date = datetime.strptime(raw_date, "%d - %B - %Y")
            formatted_date = parsed_date.strftime("%B %d, %Y")
        except ValueError:
            formatted_date = raw_date
        try:
            start_time = datetime.strptime(raw_start_time, "%I:%M:%S %p").strftime("%I:%M %p")
            end_time = datetime.strptime(raw_end_time, "%I:%M:%S %p").strftime("%I:%M %p")
        except ValueError:
            start_time = raw_start_time
            end_time = raw_end_time
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
    driver.quit()
    return exam_details

@app.get("/student")
def api_student(username: str, password: str):
    try:
        return get_student_info(username, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications")
def api_notifications(username: str, password: str):
    try:
        return get_notifications(username, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedule")
def api_schedule(username: str, password: str):
    try:
        return get_schedule_data(username, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/seats")
def api_seats(username: str, password: str):
    try:
        return get_exam_seats(username, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
