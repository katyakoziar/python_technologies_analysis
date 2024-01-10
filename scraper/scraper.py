import csv
import re
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JobScraper:
    def __init__(self, base_url: str, technologies: list) -> None:
        self.base_url = base_url
        self.technologies = technologies
        self.jobs = []

    def fetch_jobs(self) -> None:
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
                    ".pagination .page-item:not(.disabled) .bi-chevron-right",
                )
                next_button.click()
                page_number += 1
            except NoSuchElementException:
                print("No more pages to fetch.")
                break

        driver.quit()

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
            print("Necessary elements not found in job listing.")
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

        print(f"Data written to {file_path}")
