import pandas as pd
import matplotlib.pyplot as plt


class DataReader:
    @staticmethod
    def read_data(file_path):
        data = pd.read_csv(file_path)
        return data


class DataCleaner:
    @staticmethod
    def clean_data(data):
        data.dropna(subset=["Technologies"], inplace=True)
        data["Technologies"] = data["Technologies"].apply(lambda x: x.split(', ') if isinstance(x, str) else [])
        return data.explode("Technologies")
