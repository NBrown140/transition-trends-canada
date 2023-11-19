from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt


def plot_monthly_yearly_growth_rate(url: str, header: int, gas: str, color: str, out: str):
    df = pd.read_csv(url, header=header)
    df["average_diff12"] = df["average"].diff(12)
    df["average_diff12_rollmean12"] = df["average"].diff(12).rolling(12, center=True).mean()

    fig, ax = plt.subplots()
    ax.set_title(f"Global Monthly Mean Atmospheric {gas} - Yearly Growth Rate")
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
    plt.savefig(out, dpi=200)