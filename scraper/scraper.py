import csv
import re
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JobScraper:
    def __init__(self, base_url, technologies):
        self.base_url = base_url
        self.technologies = technologies
        self.jobs = []

    def fetch_jobs(self):
        driver = webdriver.Chrome()
        page_number = 1
        while True:
            url = f"{self.base_url}"
            if page_number > 1:
                url = f"{self.base_url}&page={page_number}"
            print(f"Fetching page {page_number}")

            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-list-item"))
            )

            jobs = driver.find_elements(By.CLASS_NAME, "job-list-item")

            if not jobs:
                print("No job elements found on the page.")
                break

            for job in jobs:
                self.jobs.append(self.parse_job(job))

            try:
                next_button = driver.find_element(
                    By.CSS_SELECTOR,
                    ".pagination .page-item:not(.disabled) .bi-chevron-right"
                )
                next_button.click()
                page_number += 1
            except NoSuchElementException:
                print("No more pages to fetch.")
                break

        driver.quit()
