# StatsCAN data
# https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002401
# Citation: Statistics Canada. Table 20-10-0024-01  New motor vehicle registrations, quarterly

from datetime import datetime
from zipfile import ZipFile
from io import BytesIO
import urllib.request as urllib2

import matplotlib.pyplot as plt
import pandas as pd


STATCAN_REGISTRATIONS_DATASET_URL = "https://www150.statcan.gc.ca/n1/tbl/csv/20100024-eng.zip"
STACAN_REGISTRATIONS_CSV_NAME = "20100024.csv"

def date_to_quarter(date_str: str):
    year, month = date_str.split("-")
    if month == "01":
        return f"{year}-Q1"
    elif month == "04":
        return f"{year}-Q2"
    elif month == "07":
        return f"{year}-Q3"
    elif month == "10":
        return f"{year}-Q4"
    else:
        raise ValueError()


def read_and_clean_dataset():
    dtypes = {
        "GEO": "category",
        "Fuel type": "category",
        "Vehicle type": "category",
        "VALUE": "float32"  # Can't use int because nans
    }

    r = urllib2.urlopen(STATCAN_REGISTRATIONS_DATASET_URL).read()
    registrations_csv = ZipFile(BytesIO(r)).open(STACAN_REGISTRATIONS_CSV_NAME)
    registrations = pd.read_csv(registrations_csv, dtype=dtypes)
    registrations.drop(columns=["DGUID", "Statistics", "UOM", "UOM_ID", "SCALAR_FACTOR", "SCALAR_ID", "VECTOR", "COORDINATE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS"], inplace=True)
    # Convert dates to quarters
    registrations["Quarter"] = registrations["REF_DATE"].apply(lambda x: date_to_quarter(x))
    # Aggregate by Fuel type
    df = registrations.copy()
    return df.pivot_table(index=['Quarter', 'GEO'], columns='Fuel type', values='VALUE', aggfunc='sum').reset_index()


def plot_bar_chart_by_fuel_type(clean_dataset: pd.DataFrame, region: str, out: str):
    # Select region
    df = clean_dataset[clean_dataset["GEO"]==region]

    #Plot
    quarters = df["Quarter"].values
    fuel_types = {
        "Battery electric": df["Battery electric"].values,
        "Plug-in hybrid electric": df["Plug-in hybrid electric"].values,
        "Hybrid electric": df["Hybrid electric"].values,
        "Gasoline": df["Gasoline"].values,
        "Diesel": df["Diesel"].values,
        "Other fuel types": df["Other fuel types"].values,
    }
    width = 0.5
    fig, ax = plt.subplots(figsize=(10,8))
    bottom = [0 for _ in range(len(quarters))]
    for label, fuel_type in fuel_types.items():
        p = ax.bar(quarters, fuel_type, width, label=label, bottom=bottom)
        bottom += fuel_type

    ax.set_title(f"New motor vehicle registrations - {region}")
    ax.legend(loc="upper right")
    ax.set_xticks(quarters)
    ax.set_xticklabels(quarters, rotation=45, ha="right")
    ax.text(0.82, -0.13, f"Updated on: {datetime.now().strftime('%Y-%m-%d')}", size=8, transform=plt.gca().transAxes)
    plt.savefig(out, dpi=200)


def plot_percentages_scatter_by_fuel_type(clean_dataset: pd.DataFrame, region: str, evs_only: bool, out: str):
    # Select region
    df = clean_dataset[clean_dataset["GEO"]==region]

    # Percentages
    quarters = df["Quarter"].values
    fuel_types_percentages = {
        "Battery electric": df["Battery electric"].values / df["All fuel types"].values * 100,
        "Plug-in hybrid electric": df["Plug-in hybrid electric"].values / df["All fuel types"].values * 100,
    }
    if not evs_only:
        fuel_types_percentages.update({
            "Hybrid electric": df["Hybrid electric"].values / df["All fuel types"].values * 100,
            "Gasoline": df["Gasoline"].values / df["All fuel types"].values * 100,
            "Diesel": df["Diesel"].values / df["All fuel types"].values * 100,
            "Other fuel types": df["Other fuel types"].values / df["All fuel types"].values * 100,
        })
    fig, ax = plt.subplots(figsize=(10,8))
    for label, fuel_type_percentage in fuel_types_percentages.items():
        p = ax.plot(quarters, fuel_type_percentage, label=label)

    ax.set_title(f"New motor vehicle registrations percentages - {region}")
    ax.legend(loc="upper right")
    ax.set_xticks(quarters)
    ax.set_xticklabels(quarters, rotation=45, ha="right")
    ax.text(0.82, -0.13, f"Updated on: {datetime.now().strftime('%Y-%m-%d')}", size=8, transform=plt.gca().transAxes)
    plt.savefig(out, dpi=200)


if __name__ == "__main__":
    clean_dataset = read_and_clean_dataset()

    regions = ["Canada", "Quebec", "Ontario", "British Columbia and the Territories", "Manitoba", "Saskatchewan", "New Brunswick", "Prince Edward Island"]  # No data: ["Alberta", "Nova Scotia", "Newfoundland and Labrador"]
    for region in regions:
        reg_name = region.replace(" ", "").lower()
        plot_bar_chart_by_fuel_type(clean_dataset, region, f"plots/new_vehicle_registrations/{reg_name}_fuel_types.png")
        plot_percentages_scatter_by_fuel_type(clean_dataset, region, False, f"plots/new_vehicle_registrations/{reg_name}_fuel_types_percentages.png")
        plot_percentages_scatter_by_fuel_type(clean_dataset, region, True, f"plots/new_vehicle_registrations/{reg_name}_evs_percentages.png")

