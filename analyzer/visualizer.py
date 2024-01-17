from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt


class DataReader:
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        data = pd.read_csv(file_path)
        return data


class DataCleaner:
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        data.dropna(subset=["Technologies"], inplace=True)
        data["Technologies"] = data["Technologies"].apply(
            lambda x: x.split(", ") if isinstance(x, str) else []
        )
        return data.explode("Technologies")


class Visualizer:
    @staticmethod
    def plot_technology_counts(
        technology_counts: pd.DataFrame, experience_levels: list
    ) -> None:
        for level in experience_levels:
            level_data = technology_counts[
                technology_counts["Experience Level"] == level
            ]
            level_data = level_data.sort_values("Counts", ascending=False)
            plt.figure(figsize=(15, 5))
            plt.bar(level_data["Technologies"], level_data["Counts"], color="teal")
            plt.title(f"Top 20 Technologies for {level.capitalize()} Level")
            plt.ylabel("Counts")
            plt.xticks(rotation=90)

            timestamp = datetime.now().strftime("%Y%m%d")
            file_name = f"data/plot_{level}_{timestamp}.png"

            plt.savefig(file_name)
            plt.close()

        plt.tight_layout()
        plt.show()
