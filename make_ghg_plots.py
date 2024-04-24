from utils import plot_monthly_yearly_growth_rate


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