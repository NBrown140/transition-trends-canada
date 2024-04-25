from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt


def plot_monthly_yearly_growth_rate(url: str, header: int, gas: str, gas_unit: str, color: str, out: str):
    df = pd.read_csv(url, header=header)
    df["average_diff12"] = df["average"].diff(12)
    df["average_diff12_rollmean12"] = df["average"].diff(12).rolling(12, center=True).mean()
    fig, ax = plt.subplots()
    ax.set_title(f"Global Monthly Mean Atmospheric {gas} - Yearly Growth Rate")
    ax.set_ylabel(f"[{gas_unit}]", style='italic')
    # for i, row in df_annual_gr.iterrows():
    #     if i == len(df_annual_gr)-1:  # Only add legend label once
    #         kwargs = {"label": "Annual Growth Rate"}
    #     else:
    #         kwargs = {}
    #     hline = ax.hlines(row["ann inc"], row["year"], row["year"] + 1, color="grey", **kwargs)
    ax.scatter(df["decimal"], df["average_diff12"], s=1, c="#cdcdcd", label="YoY Growth Rate")
    ax.plot(df["decimal"], df["average_diff12_rollmean12"], linewidth=1, color=color, label="12-month Running Mean")
    ax.legend(loc="lower right")
    ax.text(0.71, -0.12, f"Updated on: {datetime.now().strftime('%Y-%m-%d')}", size=8, transform=plt.gca().transAxes)
    # Annotate the date of last data point
    last_row = list(df.itertuples())[-1]
    ax.annotate(f"{int(last_row.year)}-{int(last_row.month):02}", xy=(last_row.decimal, last_row.average_diff12), xycoords='data', xytext=(2,2), textcoords='offset points', family='sans-serif', fontsize=5, color='darkslategrey')
    plt.savefig(out, dpi=200)


if __name__ == "__main__":
    # CO2
    url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv"
    header = 38
    gas = "$CO_{2}$"
    gas_unit = "ppm"
    color = "#8abb3f"
    out = "plots/co2.png"
    plot_monthly_yearly_growth_rate(url, header, gas, gas_unit, color, out)

    # CH4
    url = "https://gml.noaa.gov/webdata/ccgg/trends/ch4/ch4_mm_gl.csv"
    header = 45
    gas = "$CH_{4}$"
    gas_unit = "ppb"
    color = "#821155"
    out = "plots/ch4.png"
    plot_monthly_yearly_growth_rate(url, header, gas, gas_unit, color, out)

    # NO2
    url = "https://gml.noaa.gov/webdata/ccgg/trends/n2o/n2o_mm_gl.csv"
    header = 45
    gas = "$NO_{2}$"
    gas_unit = "ppb"
    color = "#1A2E7B"
    out = "plots/no2.png"
    plot_monthly_yearly_growth_rate(url, header, gas, gas_unit, color, out)