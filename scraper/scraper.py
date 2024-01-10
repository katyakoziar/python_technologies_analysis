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


