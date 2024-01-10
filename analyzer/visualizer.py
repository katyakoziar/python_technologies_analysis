import pandas as pd
import matplotlib.pyplot as plt


class DataReader:
    @staticmethod
    def read_data(file_path):
        data = pd.read_csv(file_path)
        return data
