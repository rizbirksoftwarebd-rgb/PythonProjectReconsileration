import pandas as pd
import os

class FileProcessor:
    def __init__(self):
        self.df1 = None
        self.df2 = None

    def load_files(self, file1, file2):
        self.df1 = pd.read_excel(file1, dtype=str)
        self.df2 = pd.read_excel(file2, dtype=str)

    def process(self, col1, col2):
        df1, df2 = self.df1.copy(), self.df2.copy()
        df1["_match_key"] = df1[col1].fillna("").str.strip()
        df2["_match_key"] = df2[col2].fillna("").str.strip()

        matched = df1[df1["_match_key"].isin(df2["_match_key"])].copy()
        unmatched1 = df1[~df1["_match_key"].isin(df2["_match_key"])].copy()
        unmatched2 = df2[~df2["_match_key"].isin(df1["_match_key"])].copy()

        for d in [matched, unmatched1, unmatched2]:
            d.drop(columns=["_match_key"], inplace=True)

        return matched, unmatched1, unmatched2

    def save_output(self, file1_name, file2_name, matched, unmatched1, unmatched2):
        output_name = f"{os.path.splitext(file1_name)[0]}_vs_{os.path.splitext(file2_name)[0]}_matched.xlsx"
        with pd.ExcelWriter(output_name, engine="openpyxl", date_format="yyyy-mm-dd") as writer:
            matched.to_excel(writer, sheet_name="Matched_Data", index=False)
            unmatched1.to_excel(writer, sheet_name="Unmatched_File1", index=False)
            unmatched2.to_excel(writer, sheet_name="Unmatched_File2", index=False)
        return output_name
