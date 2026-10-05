# transition-trends-canada

# Dev

`poetry run python make_ghg_plots.py`

`poetry run python make_emissions_plots.py`

`poetry run python make_ev_registration_plots.py`


# Global Greenhouse Gases

How fast is each gas accumulating in the atmosphere? Emission cuts show up here as a falling growth rate.
- Grey dots: change vs. the same month a year earlier (updated monthly, noisy).
- Coloured line: 12-month running mean of those dots.
- Black bars: average growth rate per decade, the long-term signal.
- Bottom strip: El Niño (red) / La Niña (blue). El Niño years raise CO<sub>2</sub> growth for a few months to a year (less uptake by tropical forests, more fires), so spikes lined up with red are mostly natural, not emissions.

## CO<sub>2</sub>
![co2](plots/co2.png)
![co2 concentration](plots/co2_concentration.png)

## CH<sub>4</sub>
![ch4](plots/ch4.png)
![ch4 concentration](plots/ch4_concentration.png)

## N<sub>2</sub>O
![n2o](plots/n2o.png)
![n2o concentration](plots/n2o_concentration.png)

# Greenhouse Gas Emissions

Emissions measured at the source rather than in the atmosphere.
- Top: yearly fossil CO<sub>2</sub> and all greenhouse gases (CO<sub>2</sub>-equivalent, excluding land use), from the Global Carbon Budget via Our World in Data. Updated once a year, roughly 1-2 years behind.
- Bottom: yearly % change (bars), plus a monthly-updated trailing-12-month % change from Carbon Monitor (~2 months behind; not available for Canada). The dashed line is the ~7.5%/yr global cut needed for 1.5°C (UNEP Emissions Gap Report 2024).

## World
![world](plots/emissions/world.png)

Per-country plots: [United States](plots/emissions/usa.png) · [China](plots/emissions/china.png) · [France](plots/emissions/france.png) · [Canada](plots/emissions/canada.png)

# Canadian New Vehicle Registrations

## Canada
![canada](plots/new_vehicle_registrations/canada_fuel_types.png)
![canada](plots/new_vehicle_registrations/canada_fuel_types_percentages.png)
![canada](plots/new_vehicle_registrations/canada_evs_percentages.png)
