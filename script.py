from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import time

winter = "01"
summer = "05"
fall = "09"


# Variables to be set by the user
#----------------------------------
#----------------------------------

student_id = "username"
password = "password"

year = 2025
season = winter
subject = "PHYS"
course_number = "183"
type = "Lecture"

#----------------------------------
#----------------------------------


term = str(year) + season
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

def register(CRN): 
    print("Attempting to register...")
    register_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][name='ADD_BTN'][value*='Register']")
    register_button.click()

    CRN_input = driver.find_element(by=By.ID, value="crn_id1")
    CRN_input.send_keys(CRN)

    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][name='REG_BTN'][value*='Submit Changes']")
    submit_button.click()

    print("Registration attempt completed.")



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



def check_availability():
    term_selection_url = "https://horizon.mcgill.ca/pban1/bwskfcls.p_sel_crse_search"

    driver.get(term_selection_url)
    time.sleep(1)
    
    if not is_logged_in():
        login()

    driver.get(term_selection_url)

    term_selection_input = driver.find_element(by=By.NAME, value="p_term")
    select = Select(term_selection_input)
    select.select_by_value(term)

    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value*='Submit']")
    submit_button.click()

    advanced_search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value*='Advanced Search']")
    advanced_search_button.click()


    subject_input = driver.find_element(by=By.ID, value="subj_id")
    select = Select(subject_input)
    select.select_by_value(subject)

    course_number_input = driver.find_element(by=By.ID, value="crse_id")
    course_number_input.send_keys(course_number)

    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][name='SUB_BTN'][value*='Get Course Sections']")
    submit_button.click()
    try:
        found_sections_table = driver.find_element(By.CSS_SELECTOR, "table.datadisplaytable")
    except Exception as e:
        print(f"No classes were found that meet your search criteria in term {term}")
        driver.quit()
        exit()
    rows = found_sections_table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")

        if columns and len(columns) == 20: #ensure that we are fetching from the correct row
            crn = columns[1].text
            subj = columns[2].text
            crse = columns[3].text
            c_type = columns[5].text
            remaining = columns[12].text
            if len(remaining.strip()) == 0 or c_type != type:
                continue
            print(f"CRN: {crn}, Course: {subj} {crse}, Type: {c_type}, Remaining: {remaining} seats")

            if int(remaining) > 0:
                print("SEATS AVAILABLE")
                return crn, True
            
    print("NO SEATS AVAILABLE")
    return None, False


if __name__ == "__main__":
    while True:
        CRN, available = check_availability()
        if available:
            register(CRN)
            driver.quit()
            break
        else:
            seconds = 20
            print(f"No seats available, retrying in {seconds} seconds...")
            time.sleep(seconds)