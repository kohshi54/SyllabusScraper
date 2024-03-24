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

        size_select = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlPageSize"))
        size_select.select_by_value("50")

        search_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btn_search")
        search_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        search_results_page_source = driver.page_source
        soup = BeautifulSoup(search_results_page_source, 'html.parser')

        fields = {
            "title": "_lbl_title_j",
            "instructor": "_lbl_instructor",
            "schedule": "_lbl_schedule",
            "courseno": "_lbl_course_no",
            "room": "_lbl_room",
            "teaching mode": "_lbl_online_flg",
            "lang": "_lbl_lang",
            "year": "_lbl_ay",
            "term": "_lbl_season"
        }
        courses_data = []
        course_rows = soup.find_all('tr')
        for row in course_rows:
            course_data = {}
            for field, end in fields.items():
                element = row.find(id=lambda x: x and x.endswith(end))
                course_data[field] = element.text.strip() if element and element.text else "NO DATA"
            if not all(value == 'NO DATA' for value in course_data.values()):
                courses_data.append(course_data)

        with open('/app/data/courses_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['title', 'instructor', 'schedule', 'courseno', 'room', 'teaching mode', 'lang', 'year', 'term'])
            for course in courses_data:
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

if __name__ == "__main__":
    main()

