import pandas as pd


df1 = pd.read_csv("preprocessing/data/ninja_wind_maan.csv", skiprows=[0,1,2], header=[0], index_col=[1])
df2 = pd.read_csv("preprocessing/data/ninja_wind_tafila.csv", skiprows=[0,1,2], header=[0], index_col=[1])

df = pd.concat([df1.electricity, df2.electricity], axis=1, sort=False)
df.columns = ["Maan", "Tafila"]
df.to_csv("ninja-wind_profiles.csv")

pv = pd.read_csv("preprocessing/data/ninja_pv_quweira.csv", skiprows=[0,1,2], header=[0], index_col=[1])
pv.to_csv("ninja-pv-profiles.csv")


df = pd.read_csv("preprocessing/ninja-pv-profiles.csv")
    
