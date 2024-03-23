from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import csv
import os

def main():
    hub_url = "http://selenium-chrome:4444/wd/hub"
    chrome_options = Options()
    driver = webdriver.Remote(command_executor=hub_url, options=chrome_options)

    try:
        driver.get("https://campus.icu.ac.jp/icumap/ehb/SearchCO.aspx")

        username_input = driver.find_element(By.ID, "username_input")
        password_input = driver.find_element(By.ID, "password_input")
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        username_input.send_keys(username)
        password_input.send_keys(password)

        login_button = driver.find_element(By.ID, "login_button")
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        year_select = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl_year"))
        year_select.select_by_value("2024")

        term_select = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddl_term"))
        term_select.select_by_value("1") # 1 -> Spring

        term_select = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlPageSize"))
        term_select.select_by_value("50")

        search_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btn_search")
        search_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        search_results_page_source = driver.page_source
        soup = BeautifulSoup(search_results_page_source, 'html.parser')

        courses_data = []
        course_rows = soup.find_all('tr')
        for row in course_rows:
            course_data = {
                "title": row.find(id=lambda x: x and x.endswith("_lbl_title_j")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_title_e")) else "NO DATA",
                "instructor": row.find(id=lambda x: x and x.endswith("_lbl_instructor")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_instructor")) else "NO DATA",
                "schedule": row.find(id=lambda x: x and x.endswith("_lbl_schedule")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_schedule")) else "NO DATA",
                "courseno": row.find(id=lambda x: x and x.endswith("_lbl_course_no")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_course_no")) else "NO DATA",
                "room": row.find(id=lambda x: x and x.endswith("_lbl_room")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_room")) else "NO DATA",
                "teaching mode": row.find(id=lambda x: x and x.endswith("_lbl_online_flg")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_online_flg")) else "NO DATA",
                "lang": row.find(id=lambda x: x and x.endswith("_lbl_lang")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_lang")) else "NO DATA",
                "year": row.find(id=lambda x: x and x.endswith("_lbl_ay")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_ay")) else "NO DATA",
                "term": row.find(id=lambda x: x and x.endswith("_lbl_season")).text.strip() if row.find(id=lambda x: x and x.endswith("_lbl_season")) else "NO DATA"
            }
            courses_data.append(course_data)

        with open('/app/data/courses_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['title', 'instructor', 'schedule', 'courseno', 'room', 'teaching mode', 'lang', 'year', 'term'])
            for course in courses_data:
                if not all(value == 'NO DATA' for value in course.values()):
                    writer.writerow([
                        course['title'],
                        course['instructor'],
                        course['schedule'],
                        course['courseno'],
                        course['room'],
                        course['teaching mode'],
                        course['lang'],
                        course['year'],
                        course['term']
                    ])

    finally:
        driver.quit()

main()
