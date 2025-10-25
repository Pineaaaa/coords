import time
import requests # type: ignore
import math
import folium # type: ignore
import webbrowser
import os
import clipboard # type: ignore
import geopandas as gpd # type: ignore
from shapely.geometry import Point # type: ignore
from shapely.ops import unary_union # type: ignore
import sys

fetches=0

pathtoshapefile = "C:/Users/thoma/countryfolder/updated_countries.shp"
world = gpd.read_file(pathtoshapefile)

if len(sys.argv)>1:
    region = " ".join(sys.argv[1:]).lower()
else:
    print("Enter the region you'd like to generate coordinates within.\n For example, 'Europe' or 'France'.")
    region=input().lower()
print()

def randomnum(min_val, max_val):
    global fetches

    url = "https://www.random.org/decimal-fractions/?num=1&dec=10&col=1&format=plain&rnd=new"
    response = requests.get(url)
    if response.status_code == 200:
        fetches+=1
        rand_fraction = float(response.text.strip())
        return min_val + (max_val - min_val) * rand_fraction
    else:
        raise RuntimeError("Failed to fetch random number from random.org")

def generate_coordinates(region):
    if region == "europe":
        countries = world[world["CONTINENT"].str.lower() == "europe"]
    elif region == "africa":
        countries = world[world["CONTINENT"].str.lower() == "africa"]
    elif region == "asia":
        countries = world[world["CONTINENT"].str.lower() == "asia"]
    elif region == "oceania":
        countries = world[world["CONTINENT"].str.lower() == "oceania"]
    elif region == "antarctica":
        countries = world[world["CONTINENT"].str.lower() == "antarctica"]
    elif region == "north america":
        countries = world[world["CONTINENT"].str.lower() == "north america"]
    elif region == "south america":
        countries = world[world["CONTINENT"].str.lower() == "south america"]
    else:
        countries = world[world["ADMIN"].str.lower() == region]

    if countries.empty:
        raise ValueError(f"Region '{region}' not found.")

    polygon = unary_union(countries.geometry)
    minx, miny, maxx, maxy=polygon.bounds

    for _ in range(10000):
        lon = randomnum(minx, maxx)
        umin=(1-math.cos(math.radians(miny)+math.pi/2))/2
        umax=(1-math.cos(math.radians(maxy)+math.pi/2))/2
        u = randomnum(umin,umax)
        lat = math.degrees(math.acos(1-2*u)-math.pi/2)
        point = Point(lon, lat)
        if polygon.contains(point):
            return lat, lon

    raise RuntimeError(f"Could not generate a point inside {region}")

iteration = 1

while True:
    print("This may take a moment...\n")
    time.sleep(0.5)

    coordinates = generate_coordinates(region)
    print(f"Success after {fetches} iterations.")
    print(f"Coordinates found in {region.capitalize()}...\n")
    print(f"Coordinates: {coordinates[0]:.5f}, {coordinates[1]:.5f}")

    map_centre = coordinates
    my_map = folium.Map(location=map_centre, zoom_start=5)
    folium.Marker(location=coordinates, popup=f"Lat: {coordinates[0]:.5f}, Lon: {coordinates[1]:.5f}").add_to(my_map)

    file_name = f"generatedcoords{iteration}.html"
    file_path = os.path.abspath(file_name)
    
    my_map.save(file_path)
    print(f"Saved map as: {file_path}")
    
    clipboard.copy(f"{coordinates[0]:.5f}, {coordinates[1]:.5f}")
    print("Copied coordinates to clipboard")

    webbrowser.open("file://" + file_path)

    iteration += 1

    user_input = input("\nPress enter to generate another coordinate: \n\n")
