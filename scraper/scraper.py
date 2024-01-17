from __future__ import annotations
import csv
import os
import re
import logging
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


log_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "analyzer.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class JobScraper:
    def __init__(self, base_url: str, technologies: list) -> None:
        self.base_url = base_url
        self.technologies = technologies
        self.jobs = []

    def fetch_jobs(self) -> None:
        driver = webdriver.Chrome()
        page_number = 1

        try:
            while True:
                content = self.fetch_page(driver, page_number)
                if not content:
                    logging.error("No more pages to fetch.")
                    break

                self.parse_page(content)
                if not self.navigate_to_next_page(driver):
                    logging.info("No more pages to fetch.")
                    break

                page_number += 1
        finally:
            driver.quit()

    def fetch_page(self, driver: WebDriver, page_number: int) -> list | None:
        url = f"{self.base_url}&page={page_number}" if page_number > 1 else self.base_url
        logging.info(f"Fetching page {page_number}")
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-list-item"))
            )
            return driver.find_elements(By.CLASS_NAME, "job-list-item")
        except NoSuchElementException:
            return None

    def parse_page(self, jobs: list) -> None:
        for job in jobs:
            self.jobs.append(self.parse_job(job))

    def navigate_to_next_page(self, driver: WebDriver) -> bool:
        try:
            next_button = driver.find_element(
                By.CSS_SELECTOR, ".pagination .page-item:not(.disabled) .bi-chevron-right"
            )
            next_button.click()
            return True
        except NoSuchElementException:
            return False

    def parse_job(self, job: WebElement) -> dict:
        title_element = job.find_element(By.CLASS_NAME, "job-list-item__link")
        title = title_element.text.strip()
        try:
            more_details_button = job.find_element(
                By.CSS_SELECTOR, "[data-toggle='show-more']"
            )
            more_details_button.click()
            WebDriverWait(job, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-original-text]")
                )
            )
        except NoSuchElementException:
            pass
        description_element = job.find_element(
            By.CLASS_NAME, "job-list-item__description"
        )
        description = description_element.text.lower()
        print(description)
        experience = self.parse_experiance(job)
        found_techs = self.find_technologies(description)

        return {"title": title, "technologies": found_techs, "experience": experience}

    def find_technologies(self, description: str) -> list:
        description = re.sub(r"[^a-zA-Z]", "", description).lower()
        return [tech for tech in self.technologies if tech.lower() in description]

    def parse_experiance(self, job: WebElement) -> str:
        try:
            job_info_element = job.find_element(
                By.CLASS_NAME, "job-list-item__job-info"
            )
            job_info = job_info_element.text.lower()
            job_title_element = job.find_element(By.CLASS_NAME, "job-list-item__link")
            job_title = job_title_element.text.lower()
        except NoSuchElementException:
            logging.error("Necessary elements not found in job listing.")
            return "Not specified"

        text_to_check = job_info + " " + job_title
        levels = ["junior", "senior", "middle"]

        for level in levels:
            if level in text_to_check:
                return level

        years_of_experience_keywords = ["year", "years", "рік", "роки", "років"]
        for word in text_to_check.split():
            if word.isdigit():
                next_word_index = text_to_check.split().index(word) + 1
                if (
                    next_word_index < len(text_to_check.split())
                    and text_to_check.split()[next_word_index]
                    in years_of_experience_keywords
                ):
                    years_of_experience = int(word)
                    if years_of_experience <= 1:
                        return "junior"
                    elif 1 < years_of_experience <= 3:
                        return "middle"
                    else:
                        return "senior"

        return "Not specified"

    def write_to_csv(self, file_path: str) -> None:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Job Title", "Experience Level", "Technologies"])
            for job in self.jobs:
                writer.writerow(
                    [job["title"], job["experience"], ", ".join(job["technologies"])]
                )

        logging.info(f"Data written to {file_path}")
