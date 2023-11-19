import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv", header=38)
df["average_diff12"] = df["average"].diff(12)
df["average_diff12_rollmean12"] = df["average"].diff(12).rolling(12).mean()

fig, ax = plt.subplots()
ax.set_title("Global Monthly Mean Atmospheric $CO_{2}$ - Yearly Growth Rate")
# for i, row in df_annual_gr.iterrows():
#     if i == len(df_annual_gr)-1:  # Only add legend label once
#         kwargs = {"label": "Annual Growth Rate"}
#     else:
#         kwargs = {}
#     hline = ax.hlines(row["ann inc"], row["year"], row["year"] + 1, color="grey", **kwargs)
ax.scatter(df["decimal"], df["average_diff12"], s=1, c="#cdcdcd", label="YoY Growth Rate")
ax.plot(df["decimal"], df["average_diff12_rollmean12"], linewidth=1, color="#8abb3f", label="12-month Running Mean")
ax.legend(loc="lower right")
plt.show()




