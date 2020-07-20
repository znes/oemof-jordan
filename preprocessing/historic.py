import os
import re

import pandas as pd
import numpy as np

load_df = pd.DataFrame()
wind_df = pd.DataFrame()
solar_df = pd.DataFrame()


for file in os.listdir("preprocessing/data"):

    df = pd.read_excel(
        "preprocessing/data/" + file,
        skiprows=4,
        index_col=3,
        parse_dates=True)

    year = re.sub("[^0-9]", "", file)
    df = df.dropna(how="all")

    df = df[[i for i in  range(1, 25)]]

    df.reset_index(inplace=True)

    df = df.drop(df.index[pd.isna(df["DATE"])])

    df = df.drop(df.index[df["DATE"] == "1.04"])

    df.set_index("DATE", inplace=True)

    ls = df.stack()

    ls.name = year

    ls.index.name = "date"

    index = ls.index[ls == 0]

    ls[index] = np.nan

    ls = ls.interpolate()

    ls.reset_index(drop=True, inplace=True)

    load_df = pd.concat([load_df, ls], axis=1, sort=False)

load_df.to_csv("preprocessing/load.csv")

load_df.sum()/1e6

for file in os.listdir("preprocessing/data"):
    df = pd.read_excel(
        "preprocessing/data/" + file,
        skiprows=4,
        index_col=3,
        parse_dates=True)

    year = re.sub("[^0-9]", "", file)

    if int(year) > 2015:
        df = df.dropna(how="all")

        df = df[[str(i) + ".1" for i in  range(1, 25)]]

        df.reset_index(inplace=True)

        df = df.drop(df.index[pd.isna(df["DATE"])])

        df = df.drop(df.index[df["DATE"] == "1.04"])

        df.set_index("DATE", inplace=True)

        ls = df.stack()

        ls.name = year

        ls.index.name = "date"

        ls = ls.interpolate()

        ls.reset_index(drop=True, inplace=True)

        wind_df = pd.concat([wind_df, ls], axis=1, sort=False)

wind_df.to_csv("preprocessing/wind.csv")



for file in os.listdir("preprocessing/data"):
    df = pd.read_excel(
        "preprocessing/data/" + file,
        skiprows=4,
        index_col=3,
        parse_dates=True)

    year = re.sub("[^0-9]", "", file)

    if int(year) > 2015:
        df = df.dropna(how="all")

        df = df[[str(i) + ".2" for i in  range(1, 25)]]

        df.reset_index(inplace=True)

        df = df.drop(df.index[pd.isna(df["DATE"])])

        df = df.drop(df.index[df["DATE"] == "1.04"])

        df.set_index("DATE", inplace=True)

        ls = df.stack()

        ls.name = year

        ls.index.name = "date"


        ls = ls.interpolate()

        ls.reset_index(drop=True, inplace=True)

        solar_df = pd.concat([solar_df, ls], axis=1, sort=False)

solar_df.to_csv("preprocessing/solar.csv")


profiles = pd.concat(
    [(load_df["2018"] / load_df["2018"].sum())[0:8759],
      solar_df["2018"] / solar_df["2018"].max(),
      wind_df["2018"] / wind_df["2018"].max()],
      axis=1
)
profiles.columns = ["load", "pv", "wind"]
profiles = profiles.fillna(method="ffill")
profiles.index = pd.date_range(start="2018", periods=8760, freq="H")
profiles.to_csv("preprocessing/profiles-2018.csv")


(profiles["wind"] *  280).sum() / 1000
(profiles["pv"] * 698.5).sum() / 1000
