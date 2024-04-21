import pandas as pd

from utils import get_legacy_session


BASE_URL = "https://population.un.org/dataportalapi/api/v1"

# Locations:
# World: 900
# Canada: 124

target = BASE_URL + "/data/indicators/49/locations/124/start/2005/end/2010"
# target = BASE_URL + "/locations/"
response = get_legacy_session().get(target)  # Need to use legacy SSL. https://stackoverflow.com/a/73519818
if response.status_code != 200:
    raise ValueError(f"Status code: {response.status_code}")
j = response.json()
df = pd.json_normalize(j['data']) # pd.json_normalize flattens the JSON to accomodate nested lists within the JSON structure

while j['nextPage'] != None:
    target = j['nextPage']
    response = get_legacy_session().get(target)
    j = response.json()
    df_temp = pd.json_normalize(j['data'])
    df = pd.concat([df, df_temp], ignore_index=True)
print(df)





