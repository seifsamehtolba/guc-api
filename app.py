from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import re
from datetime import datetime
import json

app = FastAPI()

# Configure CORS: You can adjust allowed origins as needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or list specific origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=chrome_options)
    return driver

@app.get("/student")
def get_student_details(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/index.aspx"
    driver = get_chrome_driver()
    driver.get(URL)
    try:
        wait = WebDriverWait(driver, 5, poll_frequency=0.1)
        elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[contains(@id, 'ContentPlaceHolderright_ContentPlaceHoldercontent_Label')]")
            )
        )
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail="Error fetching student details")
        
    data = {elem.get_attribute("id").split("_")[-1]: elem.text.strip() for elem in elements}
    student_details = {
        "Student Name": data.get("LabelFullName", "N/A"),
        "Student ID": data.get("LabelUniqAppNo", "N/A"),
        "Student Mail": data.get("LabelMail", "N/A"),
        "Study Group": data.get("Labelsg", "N/A")
    }
    driver.quit()
    return student_details

@app.get("/notifications")
def get_notifications(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/Main/Notifications.aspx"
    driver = get_chrome_driver()
    driver.get(URL)
    try:
        wait = WebDriverWait(driver, 10)
        table_xpath = "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div/div/div/div"
        table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail="Error fetching notifications")
        
    rows = table.find_elements(By.XPATH, ".//tbody/tr")[:10]
    notifications = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 6:
            continue
        try:
            button = cols[1].find_element(By.TAG_NAME, "button")
            full_message = button.get_attribute("data-body_text").strip()
        except Exception:
            full_message = "No message available"
        raw_title = cols[2].text.strip()
        title = re.sub(r"^Notification System:\s*", "", raw_title)
        date = cols[3].text.strip()
        staff = cols[4].text.strip()
        importance = cols[5].text.strip() if cols[5].text.strip() else "Normal"
        notifications.append({
            "Title": title,
            "Date": date,
            "Staff": staff,
            "Importance": importance,
            "Full_Message": full_message
        })
    driver.quit()
    return notifications

@app.get("/schedule")
def get_schedule(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/Scheduling/GroupSchedule.aspx"
    driver = get_chrome_driver()
    driver.get(URL)
    try:
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_scdTbl")))
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail="Error fetching schedule")
        
    default_period_names = ["First Period", "Second Period", "Third Period", "Fourth Period", "Fifth Period"]
    weekdays = {"Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
    
    lecture_pattern = re.compile(r"\bH\d{1,2}\b")
    tut_pattern = re.compile(r"\b[CABD]\d+\.\d+\b")
    
    schedule_list = []
    rows = table.find_elements(By.XPATH, "./tbody/tr") or table.find_elements(By.XPATH, "./tr")
    for row in rows:
        cells = row.find_elements(By.XPATH, "./td")
        if len(cells) != 6:
            continue
        day_text = cells[0].text.strip()
        if day_text not in weekdays:
            continue
        day_entry = {"day": day_text, "periods": {}}
        for i in range(5):
            cell_text = cells[i+1].get_attribute("innerText").strip() or "Free"
            lecture_match = lecture_pattern.search(cell_text)
            tut_match = tut_pattern.search(cell_text)
            if lecture_match:
                location = lecture_match.group()
            elif tut_match:
                location = tut_match.group()
            else:
                location = "Unknown" if cell_text != "Free" else "None"
            clean_course = re.sub(lecture_pattern, "", cell_text)
            clean_course = re.sub(tut_pattern, "", clean_course)
            clean_course = re.sub(r"\s+", " ", clean_course).strip()
            day_entry["periods"][default_period_names[i]] = {
                "course": clean_course,
                "location": location
            }
        schedule_list.append(day_entry)
    driver.quit()
    return schedule_list

@app.get("/exam_seats")
def get_exam_seats(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/Exam/ViewExamSeat_01.aspx"
    driver = get_chrome_driver()
    driver.get(URL)
    try:
        wait = WebDriverWait(driver, 10)
        table_xpath = "/html/body/form/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/table"
        table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail="Error fetching exam seats")
        
    rows = table.find_elements(By.XPATH, ".//tbody/tr")[1:]
    exam_details = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
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
        
        def format_time(raw_time):
            try:
                return datetime.strptime(raw_time, "%I:%M:%S %p").strftime("%I:%M %p")
            except ValueError:
                return raw_time
        
        start_time = format_time(raw_start_time)
        end_time = format_time(raw_end_time)
        
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

@app.get("/payment_details")
def get_payment_details(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/Financial/BalanceView_001.aspx"
    driver = get_chrome_driver()
    driver.get(URL)

    wait = WebDriverWait(driver, 10)

    # Dictionary to store the output
    output = {
        "Payment Requests": []
    }

    try:
        # Wait for the user information section to load
        wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_lbl_Name")))

        # Extract Payment Requests
        payment_table = driver.find_element(By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_DG_PaymentRequest")
        rows = payment_table.find_elements(By.TAG_NAME, "tr")

        # Process all payment requests (skip the header row)
        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")

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

        if not output["Payment Requests"]:
            output["Payment Requests"].append({"Message": "No payment requests found."})

    except Exception as e:
        output["Error"] = str(e)

    finally:
        # Close the browser
        driver.quit()

    return output

@app.get("/grades")
def get_grades(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/Grade/CheckGrade_01.aspx"
    driver = get_chrome_driver()
    driver.get(URL)
    wait = WebDriverWait(driver, 10)
    
    grades_data = {}
    
    # Get course dropdown
    dropdown = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_smCrsLst")))
    total_options = len(dropdown.find_elements(By.TAG_NAME, "option"))
    
    for i in range(1, total_options):  # Skip "Choose a Course"
        dropdown = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_smCrsLst")))
        options = dropdown.find_elements(By.TAG_NAME, "option")
        
        option = options[i]
        course_name = option.text
        option_value = option.get_attribute("value")
        
        print(f"Processing: {course_name}")
        
        # Select course
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", dropdown, option_value)
        
        # Wait for grades table
        wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_nttTr")))
        
        # Extract grades
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
    
    driver.quit()
    return grades_data
@app.get("/attendance")
def get_attendance(username: str = Query(...), password: str = Query(...)):
    URL = f"https://{username}:{password}@apps.guc.edu.eg/student_ext/Attendance/ClassAttendance_ViewStudentAttendance_001.aspx"
    driver = get_chrome_driver()
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

    try:
        # Locate the dropdown element
        dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolderright_ContentPlaceHoldercontent_DDL_Courses"))

        # Get all options from the dropdown (skip the first one which is "[Choose Course]")
        options = dropdown.options[1:]

        attendance_results = {}

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
            
            # Store attendance data for the course
            attendance_results[course_name] = attendance_data

    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

    finally:
        # Close the browser
        driver.quit()

    return attendance_results