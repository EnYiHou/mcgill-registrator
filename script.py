from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import time
from enum import Enum


class Course:
    class Season(Enum):
        WINTER = "01"
        SUMMER = "05"
        FALL = "09"

    def __init__(self, year, season, subject, course_number, type):
        self.year = year
        self.season = season
        self.subject = subject
        self.course_number = course_number
        self.type = type
        self.term = str(year) + season.value

    def __str__(self):
        return f"{self.subject} {self.course_number} ({self.type}) - {self.term}"


# Variables to be set by the user
# ----------------------------------
# ----------------------------------

student_id = "username"
password = "password"

courses = [
    Course(2025, Course.Season.WINTER, "PHYS", "183", "Lecture"),
    Course(2025, Course.Season.WINTER, "COMP", "250", "Lecture"),
    Course(2025, Course.Season.WINTER, "COMP", "322", "Lecture"),
]

# ----------------------------------
# ----------------------------------


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)


def register(CRN):
    print("Attempting to register...")
    register_button = driver.find_element(
        By.CSS_SELECTOR, "input[type='submit'][name='ADD_BTN'][value*='Register']"
    )
    register_button.click()

    CRN_input = driver.find_element(by=By.ID, value="crn_id1")
    CRN_input.send_keys(CRN)

    submit_button = driver.find_element(
        By.CSS_SELECTOR, "input[type='submit'][name='REG_BTN'][value*='Submit Changes']"
    )
    submit_button.click()


def check_registration(title):
    try:
        schedule_table = driver.find_element(
            By.CSS_SELECTOR, "table.datadisplaytable[summary='Current Schedule']"
        )
        schedule_rows = schedule_table.find_elements(By.TAG_NAME, "tr")
        for row in schedule_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if columns and title in columns[10].text:
                return True
        return False
    except:
        return False


def login():
    driver.get("https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin")

    username_input = driver.find_element(by=By.NAME, value="sid")
    username_input.send_keys(student_id)

    password_input = driver.find_element(by=By.NAME, value="PIN")
    password_input.send_keys(password)

    login_button = driver.find_element(by=By.ID, value="mcg_id_submit")
    login_button.click()

    print("Logged in successfully.")


def is_logged_in():
    try:
        driver.find_element(By.XPATH, "//h2[text()='User Login']")
        return False
    except:
        return True


def check_availability(course: Course):

    term = course.term
    subject = course.subject
    type = course.type
    course_number = course.course_number

    term_selection_url = "https://horizon.mcgill.ca/pban1/bwskfcls.p_sel_crse_search"

    driver.get(term_selection_url)
    time.sleep(1)

    if not is_logged_in():
        login()

    if not is_logged_in():
        print("Login failed.")
        driver.quit()
        exit()

    driver.get(term_selection_url)

    term_selection_input = driver.find_element(by=By.NAME, value="p_term")
    select = Select(term_selection_input)
    select.select_by_value(term)

    submit_button = driver.find_element(
        By.CSS_SELECTOR, "input[type='submit'][value*='Submit']"
    )
    submit_button.click()

    advanced_search_button = driver.find_element(
        By.CSS_SELECTOR, "input[type='submit'][value*='Advanced Search']"
    )
    advanced_search_button.click()

    subject_input = driver.find_element(by=By.ID, value="subj_id")
    select = Select(subject_input)
    select.select_by_value(subject)

    course_number_input = driver.find_element(by=By.ID, value="crse_id")
    course_number_input.send_keys(course_number)

    submit_button = driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][name='SUB_BTN'][value*='Get Course Sections']",
    )
    submit_button.click()
    try:
        found_sections_table = driver.find_element(
            By.CSS_SELECTOR, "table.datadisplaytable"
        )
    except Exception as e:
        print(f"No classes were found that meet your search criteria in term {term}")
        driver.quit()
        exit()
    rows = found_sections_table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")

        if (
            columns and len(columns) == 20
        ):  # ensure that we are fetching from the correct row
            crn = columns[1].text
            subj = columns[2].text
            crse = columns[3].text
            c_type = columns[5].text
            title = columns[7].text
            remaining = columns[12].text
            waitlist_capacity = columns[13].text
            waitlist_remaining = columns[15].text
            if len(remaining.strip()) == 0 or c_type != type:
                continue
            print(
                f"CRN: {crn}, Course: {subj} {crse}, Type: {c_type}, Remaining: {remaining} seats"
                + (f", Waitlist: {waitlist_remaining} seats" if waitlist_capacity.strip() != "0" else "")
            )

            if waitlist_capacity.strip() != "0":
                if int(waitlist_remaining) > 0:
                    print("WAITLIST AVAILABLE")
                    return crn, title, True

                else:
                    print("NO WAITLIST AVAILABLE")
                    return None, None, False

            if int(remaining) > 0:
                print("SEATS AVAILABLE")
                return crn, title, True

    print("NO SEATS AVAILABLE")
    return None, None, False


if __name__ == "__main__":
    while True:
        print("________________________________________")
        print("Checking for available courses...")
        if len(courses) == 0:
            print("Registration complete.")
            driver.quit()
            exit()
        print(f"Remaining courses:\n\t{'\n\t'.join([str(course) for course in courses])}")
        for course in courses:
            print(f"\nChecking availability for {course}")
            crn, title, available = check_availability(course)
            if available:
                register(crn)
                if check_registration(title):
                    print(f"Successfully registered for {title}")
                else:
                    print(f"Failed to register for {title}")
                courses.remove(course)
                break
        time.sleep(5)
