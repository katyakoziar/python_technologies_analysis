import os

from analyzer.visualizer import DataReader, DataCleaner, Visualizer
from config import technologies
from scraper.scraper import JobScraper


def scrape_job_data(base_url, csv_path):
    scraper = JobScraper(base_url, technologies)
    try:
        scraper.fetch_jobs()
        scraper.write_to_csv(csv_path)
    except Exception as e:
        print(f"Failed to retrieve the webpage: {e}")
        return False
    return True


def process_and_visualize_data(csv_path, experience_levels):
    data_reader = DataReader()
    data_cleaner = DataCleaner()
    visualizer = Visualizer()
    try:
        data = data_reader.read_data(csv_path)
        data = data_cleaner.clean_data(data)
        technology_counts = (
            data.groupby(["Experience Level", "Technologies"])
            .size()
            .reset_index(name="Counts")
        )
        top_techs_by_level = (
            technology_counts.sort_values(
                ["Experience Level", "Counts"], ascending=[True, False]
            )
            .groupby("Experience Level")
            .head(20)
        )
        visualizer.plot_technology_counts(top_techs_by_level, experience_levels)
    except FileNotFoundError as e:
        print(f"Error reading the file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    base_url = "https://djinni.co/jobs/?primary_keyword=Python"

    csv_path = os.path.join("data", "data.csv")
    if scrape_job_data(base_url, csv_path):
        process_and_visualize_data(csv_path, ["junior", "middle", "senior"])


if __name__ == "__main__":
    main()