# Annual emissions: Our World in Data CO2 & GHG dataset (Global Carbon Budget for fossil CO2,
#   Jones et al. for total GHG). https://github.com/owid/co2-data
# Near-real-time fossil CO2 (daily, ~2 months lag): Carbon Monitor. https://carbonmonitor.org

from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd

from utils import download

OWID_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
CARBON_MONITOR_URL = "https://datas.carbonmonitor.org/API/downloadFullDataset.php?source=carbon_global"
START_YEAR = 1990
# UNEP Emissions Gap Report 2024: global cuts of ~7.5%/yr to 2035 are needed for 1.5°C.
PATHWAY_1P5C_PCT = -7.5
INK = "#2b2b2b"
MUTED = "#6b6b6b"
CO2_COLOR = "#6a9a23"
GHG_COLOR = "#555555"
# x-axis is in decimal years: annual values sit mid-year, so each bar spans the calendar year it covers
MID_YEAR = 0.5


def read_owid() -> pd.DataFrame:
    cols = ["country", "year", "co2", "total_ghg_excluding_lucf"]
    return pd.read_csv(BytesIO(download(OWID_URL)), usecols=cols)


def read_carbon_monitor() -> pd.DataFrame | None:
    """Daily fossil CO2 emissions (Mt) by country, summed over sectors."""
    try:
        df = pd.read_csv(BytesIO(download(CARBON_MONITOR_URL)), usecols=["country", "date", "value"])
    except Exception as e:  # Optional near-real-time layer, never block the plots on it
        print(f"Could not download Carbon Monitor data, skipping monthly layer: {e}")
        return None
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    return df.pivot_table(index="date", columns="country", values="value", aggfunc="sum")


def rolling_12m_change(daily: pd.Series) -> pd.DataFrame:
    """% change of the trailing 12 months vs. the same 12 months a year earlier, sampled at each month end.

    The series only starts in 2019, so during its second year the window is shortened to the months
    available (Jan vs. Jan, Jan-Feb vs. Jan-Feb, ...), always comparing the same calendar days. By the
    end of that year the window is a full 12 months, so both parts join seamlessly.
    Returns the change, the window length in days, and `x`: the window's end date as a decimal year.
    """
    daily = daily.dropna()
    rows = []
    for end in daily.resample("ME").last().index:
        values = daily.loc[:end]
        window = min(365, len(values) - 365)
        if window < 28:
            continue
        current, previous = values.iloc[-window:].sum(), values.iloc[-window - 365:-365].sum()
        last = values.index[-1]
        x = last.year + last.dayofyear / (366 if last.is_leap_year else 365)
        rows.append({"end": end, "change": (current / previous - 1) * 100, "window": window, "x": x})
    return pd.DataFrame(rows).set_index("end")


def style_axes(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED)


def plot_emissions(owid: pd.DataFrame, cm_daily: pd.Series | None, name: str, out: str):
    df = owid[owid["year"] >= START_YEAR].set_index("year")
    co2 = df["co2"].dropna()
    ghg = df["total_ghg_excluding_lucf"].dropna()
    co2_change = co2.pct_change() * 100
    peak_year = co2.idxmax()
    last_year = co2.index[-1]

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=False, height_ratios=[3, 2])
    style_axes(ax)
    style_axes(ax2)

    # Top: absolute annual emissions
    ax.plot(ghg.index + MID_YEAR, ghg, color=GHG_COLOR, linewidth=2, label="All greenhouse gases (Mt CO$_2$e, excl. land use)")
    ax.plot(co2.index + MID_YEAR, co2, color=CO2_COLOR, linewidth=2, label="Fossil CO$_2$ (Mt CO$_2$)")
    for series, color in ((ghg, GHG_COLOR), (co2, CO2_COLOR)):
        ax.annotate(f"{series.iloc[-1]:,.0f}", xy=(series.index[-1] + MID_YEAR, series.iloc[-1]), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=8, color=INK)
    if peak_year != last_year:
        ax.scatter([peak_year + MID_YEAR], [co2[peak_year]], s=30, color=CO2_COLOR, edgecolor="white", linewidth=1.5, zorder=3)
        ax.annotate(f"peak {peak_year}", xy=(peak_year + MID_YEAR, co2[peak_year]), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=8, color=MUTED)
    ax.set_ylim(0, max(ghg.max(), co2.max()) * 1.12)
    ax.set_ylabel("Mt per year", color=MUTED)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.legend(loc="lower left", frameon=False, fontsize=8)

    vs_peak = (co2.iloc[-1] / co2[peak_year] - 1) * 100
    vs_2005 = (co2.iloc[-1] / co2[2005] - 1) * 100
    headline = f"Fossil CO$_2$ in {last_year}: {co2_change.iloc[-1]:+.1f}% vs. {last_year - 1}, {vs_2005:+.0f}% vs. 2005"
    if peak_year != last_year:
        headline += f", {vs_peak:+.0f}% vs. {peak_year} peak"
    ax.set_title(f"Greenhouse gas emissions - {name}", loc="left", fontsize=14, color=INK, pad=24)
    ax.text(0, 1.03, headline, transform=ax.transAxes, fontsize=9, color=MUTED)

    # Bottom: rate of change, the "are we bending the curve" view
    ax2.bar(co2_change.index + MID_YEAR, co2_change, width=0.7, color="#cfcfcf", label="Annual change (Global Carbon Budget)")
    if cm_daily is not None:
        cm = rolling_12m_change(cm_daily)
        full = cm[cm["window"] == 365]
        partial = cm.loc[: full.index[0]]  # includes the first full point so the two segments connect
        ax2.plot(full["x"], full["change"], color=CO2_COLOR, linewidth=2,
                 label="Trailing 12 months vs. same months a year earlier (Carbon Monitor)")
        ax2.plot(partial["x"], partial["change"], color=CO2_COLOR, linewidth=1.5, linestyle=(0, (2, 1.5)),
                 label="Same, with < 12 months of data available (Carbon Monitor starts in 2019)")
        ax2.annotate(f"{cm.index[-1]:%Y-%m}: {cm['change'].iloc[-1]:+.1f}%", xy=(cm["x"].iloc[-1], cm["change"].iloc[-1]),
                     xytext=(4, 0), textcoords="offset points", va="center", fontsize=7, color=MUTED)
    else:
        ax2.text(0.99, 1.02, "No monthly (Carbon Monitor) data for this country", transform=ax2.transAxes,
                 ha="right", fontsize=7, color=MUTED)
    ax2.axhline(0, color=INK, linewidth=0.8)
    ax2.axhline(PATHWAY_1P5C_PCT, color=MUTED, linewidth=1, linestyle="--")
    ax2.text(START_YEAR + 0.2, PATHWAY_1P5C_PCT, "1.5°C pathway: −7.5%/yr (UNEP 2024)", va="bottom", fontsize=7, color=MUTED)
    lo = min(co2_change.min(), PATHWAY_1P5C_PCT, cm['change'].min() if cm_daily is not None else 0)
    hi = max(co2_change.max(), 3, cm['change'].max() if cm_daily is not None else 0)
    ax2.set_ylim(lo - 1.5, hi + 1.5)
    ax2.set_ylabel("Fossil CO$_2$, % change per year", color=MUTED)
    ax2.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=2 if cm_daily is None else 1, frameon=False, fontsize=8)

    xlim = (START_YEAR, datetime.now().year + 1.5)
    ax.set_xlim(xlim)
    ax2.set_xlim(xlim)
    sources = "Our World in Data / Global Carbon Budget" + (", Carbon Monitor" if cm_daily is not None else "")
    fig.text(0.99, 0.01, f"Data: {sources} · Updated on: {datetime.now():%Y-%m-%d}", ha="right", fontsize=7, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    owid = read_owid()
    carbon_monitor = read_carbon_monitor()
    regions = [
        # (OWID name, Carbon Monitor name or None if not covered, title, output)
        ("World", "WORLD", "World", "plots/emissions/world.png"),
        ("United States", "United States", "United States", "plots/emissions/usa.png"),
        ("China", "China", "China", "plots/emissions/china.png"),
        ("France", "France", "France", "plots/emissions/france.png"),
        ("Canada", None, "Canada", "plots/emissions/canada.png"),
    ]
    for owid_name, cm_name, title, out in regions:
        cm_daily = carbon_monitor[cm_name] if carbon_monitor is not None and cm_name else None
        plot_emissions(owid[owid["country"] == owid_name], cm_daily, title, out)
