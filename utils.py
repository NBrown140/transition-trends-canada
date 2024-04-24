import urllib3
import ssl
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import requests


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


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session