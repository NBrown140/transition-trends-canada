from datetime import datetime
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

from utils import download

NOAA_URL = "https://gml.noaa.gov/webdata/ccgg/trends/{gas}/{gas}_mm_gl.csv"
ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
ONI_SEASON_CENTER_MONTH = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}
INK = "#2b2b2b"
MUTED = "#6b6b6b"


def read_noaa_monthly(gas: str) -> pd.DataFrame:
    # NOAA prepends a variable-length comment header, so don't rely on a fixed header line.
    text = download(NOAA_URL.format(gas=gas)).decode()
    df = pd.read_csv(StringIO(text), comment="#", skip_blank_lines=True)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=15))
    return df.set_index("date")


def read_oni() -> pd.Series | None:
    """Oceanic Nino Index (3-month running SST anomaly in the Nino 3.4 region)."""
    try:
        text = download(ONI_URL).decode()
    except Exception as e:  # ENSO context is nice-to-have, never block the plot on it
        print(f"Could not download ONI, skipping ENSO strip: {e}")
        return None
    oni = pd.read_csv(StringIO(text), sep=r"\s+")
    oni["date"] = pd.to_datetime(dict(year=oni["YR"], month=oni["SEAS"].map(ONI_SEASON_CENTER_MONTH), day=15))
    return oni.set_index("date")["ANOM"]


def decade_means(growth: pd.Series) -> pd.DataFrame:
    """Mean growth rate per calendar decade, keeping only decades with at least 3 years of data."""
    df = growth.dropna().to_frame("growth")
    df["decade"] = df.index.year // 10 * 10
    df["date"] = df.index
    out = df.groupby("decade").agg(mean=("growth", "mean"), count=("growth", "count"),
                                   start=("date", "min"), end=("date", "max"))
    return out[out["count"] >= 36]


def plot_growth_rate(df: pd.DataFrame, oni: pd.Series | None, gas: str, gas_unit: str, color: str, out: str):
    yoy = df["average"].diff(12)  # change vs. the same month last year (cancels the seasonal cycle)
    yoy_smooth = yoy.rolling(12, center=True).mean()
    decades = decade_means(yoy)
    last_date = yoy.index[-1]
    last_12m = df["average"].iloc[-12:].mean() - df["average"].iloc[-24:-12].mean()

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)

    ax.scatter(yoy.index, yoy, s=3, color="#c8c8c8", label="Monthly year-over-year change", zorder=2)
    ax.plot(yoy_smooth.index, yoy_smooth, linewidth=2, color=color, label="12-month running mean", zorder=3)

    for decade, row in decades.iterrows():
        ax.hlines(row["mean"], row["start"], row["end"], color=INK, linewidth=2, zorder=4,
                  label="Decade average" if decade == decades.index[0] else None)
        ax.annotate(f"{row['mean']:.2f}", xy=(row["start"] + (row["end"] - row["start"]) / 2, row["mean"]),
                    xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8, color=INK, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))

    ax.annotate(f"{last_date:%Y-%m}: {yoy.iloc[-1]:.2f}", xy=(last_date, yoy.iloc[-1]), xytext=(4, 0),
                textcoords="offset points", va="center", fontsize=7, color=MUTED)

    ymin, ymax = np.nanmin(yoy), np.nanmax(yoy)
    pad = (ymax - ymin) * 0.08
    ax.set_ylim(min(0, ymin - pad), ymax + pad)
    ax.set_xlim(yoy.dropna().index[0] - pd.Timedelta(days=180), last_date + pd.Timedelta(days=600))

    if oni is not None:
        # ENSO strip along the bottom: El Nino (red) years tend to push CO2 growth up ~6 months later.
        oni = oni[oni.index >= yoy.dropna().index[0]]
        strip = ax.inset_axes([0, 0, 1, 0.035], sharex=ax)
        colors = plt.get_cmap("RdBu_r")(TwoSlopeNorm(0, -2.5, 2.5)(oni.to_numpy()))
        strip.bar(oni.index, 1, width=31, color=colors, linewidth=0)
        strip.set_axis_off()
        strip.text(1.0, 1.4, "ENSO index: El Niño (red) / La Niña (blue)", transform=strip.transAxes,
                   ha="right", va="bottom", fontsize=7, color=MUTED)

    ax.set_title(f"Global atmospheric {gas} growth rate", loc="left", fontsize=14, color=INK, pad=24)
    ax.text(0, 1.02, f"Last 12 months vs. previous 12: +{last_12m:.2f} {gas_unit}/yr", transform=ax.transAxes,
            fontsize=9, color=MUTED)
    ax.set_ylabel(f"{gas_unit} per year", color=MUTED)
    ax.tick_params(colors=MUTED)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    fig.text(0.99, 0.01, f"Data: NOAA GML, NOAA CPC (ONI) · Updated on: {datetime.now():%Y-%m-%d}",
             ha="right", fontsize=7, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def plot_concentration(df: pd.DataFrame, gas: str, gas_unit: str, color: str, out: str):
    """Monthly concentration with NOAA's de-seasonalized trend (seasonal cycle removed by curve fit)."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)

    ax.plot(df.index, df["average"], linewidth=0.8, color="#b5b5b5", label="Monthly mean")
    ax.plot(df.index, df["trend"], linewidth=2, color=color, label="De-seasonalized trend (NOAA)")
    last_date, last_trend = df.index[-1], df["trend"].iloc[-1]
    ax.annotate(f"{last_date:%Y-%m}: {last_trend:.1f}", xy=(last_date, last_trend), xytext=(4, 0),
                textcoords="offset points", va="center", fontsize=7, color=MUTED)
    ax.set_xlim(df.index[0] - pd.Timedelta(days=180), last_date + pd.Timedelta(days=900))

    ax.set_title(f"Global atmospheric {gas} concentration", loc="left", fontsize=14, color=INK, pad=24)
    ax.text(0, 1.02, f"{last_date:%Y-%m}: {last_trend:.1f} {gas_unit} (trend), "
            f"{last_trend - df['trend'].iloc[-121]:+.1f} {gas_unit} over the last 10 years",
            transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.set_ylabel(gas_unit, color=MUTED)
    ax.tick_params(colors=MUTED)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    fig.text(0.99, 0.01, f"Data: NOAA GML · Updated on: {datetime.now():%Y-%m-%d}", ha="right", fontsize=7, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    oni = read_oni()
    gases = [
        # (NOAA name, label, unit, color)
        ("co2", "$CO_{2}$", "ppm", "#6a9a23"),
        ("ch4", "$CH_{4}$", "ppb", "#821155"),
        ("n2o", "$N_{2}O$", "ppb", "#1A2E7B"),
    ]
    for noaa_name, gas, unit, color in gases:
        df = read_noaa_monthly(noaa_name)
        plot_growth_rate(df, oni, gas, unit, color, f"plots/{noaa_name}.png")
        plot_concentration(df, gas, unit, color, f"plots/{noaa_name}_concentration.png")
