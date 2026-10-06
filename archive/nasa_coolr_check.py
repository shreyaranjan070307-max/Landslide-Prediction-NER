import requests

url = "https://gis.earthdata.nasa.gov/gis05/rest/services/Landslides/COOLR_Events_Points/MapServer"

response = requests.get(
    url,
    params={"f": "json"}
)

print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("\nAvailable layers:")

    for layer in data.get("layers", []):
        print(layer["id"], "-", layer["name"])

else:
    print("\nRequest failed.")
    print(response.text[:500])
