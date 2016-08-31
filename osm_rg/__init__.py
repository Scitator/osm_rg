##
# Author: Kolesnikov Sergey
##
import os
import time
import click
import zipfile
from scipy.spatial import cKDTree as KDTree
# from osm_rg import cKDTree_MP as KDTree_MP
from cKDTree_MP import cKDTree_MP as KDTree_MP


import pandas as pd
from ast import literal_eval
from geopy.geocoders import Nominatim as osm_geolocator

GN_URL = "http://download.geonames.org/export/dump/"
GN_CITIES1000 = "cities1000"
GN_CITIES5000 = "cities5000"
GN_CITIES15000 = "cities15000"

GN_COLUMNS = {
    "geoNameId": 0,
    "name": 1,
    "asciiName": 2,
    "alternateNames": 3,
    "latitude": 4,
    "longitude": 5,
    "featureClass": 6,
    "featureCode": 7,
    "countryCode": 8,
    "cc2": 9,
    "admin1Code": 10,
    "admin2Code": 11,
    "admin3Code": 12,
    "admin4Code": 13,
    "population": 14,
    "elevation": 15,
    "dem": 16,
    "timezone": 17,
    "modificationDate": 18
}

GN_COLUMNS_OF_INTEREST = [
    "geoNameId",
    "name",
    "asciiName",
    "latitude",
    "longitude"
]

RG_COLUMNS = [
    "geo_id",
    "lat",
    "lon",
    "name",
    "ascii_name",
    "address"
]

OSM_COLUMNS = [
    "land",
    "track",
    "town",
    "viewpoint",
    "alcohol",
    "toilets",
    "retail",
    "chalet",
    "nursing_home",
    "garden",
    "junction",
    "county",
    "farmyard",
    "manor",
    "travel_agency",
    "electronics",
    "bus_station",
    "department_store",
    "island",
    "bicycle",
    "library",
    "country_code",
    "taxi",
    "footway",
    "castle",
    "roman_road",
    "common",
    "construction",
    "dentist",
    "services",
    "residential",
    "police",
    "car",
    "household",
    "country",
    "outdoor",
    "marina",
    "caravan_site",
    "bus_stop",
    "arts_centre",
    "grave_yard",
    "nightclub",
    "sports_centre",
    "bridleway",
    "bicycle_parking",
    "optician",
    "butcher",
    "continent",
    "pub",
    "state",
    "bar",
    "estate_agent",
    "hamlet",
    "road",
    "pedestrian",
    "allotments",
    "fire_station",
    "prison",
    "community_centre",
    "computer",
    "clinic",
    "recycling",
    "supermarket",
    "beverages",
    "attraction",
    "toys",
    "ferry_terminal",
    "post_office",
    "bank",
    "nature_reserve",
    "locality",
    "cinema",
    "region",
    "postcode",
    "doctors",
    "commercial",
    "hotel",
    "newsagent",
    "clothes",
    "ruins",
    "telephone",
    "courthouse",
    "dry_cleaning",
    "place_of_worship",
    "sports",
    "traffic_signals",
    "theatre",
    "museum",
    "park",
    "florist",
    "guest_house",
    "fast_food",
    "pitch",
    "archaeological_site",
    "convenience",
    "industrial",
    "townhall",
    "beauty",
    "kindergarten",
    "furniture",
    "memorial",
    "public_building",
    "hospital",
    "pet",
    "parking",
    "hairdresser",
    "hifi",
    "mobile_phone",
    "village",
    "state_district",
    "administrative",
    "shop",
    "veterinary",
    "house_number",
    "pharmacy",
    "car_wash",
    "city",
    "post_box",
    "water",
    "laundry",
    "books",
    "theme_park",
    "monument",
    "swimming_pool",
    "tree",
    "path",
    "neighbourhood",
    "aerodrome",
    "doityourself",
    "cycleway",
    "jewelry",
    "fort",
    "cafe",
    "hostel",
    "city_district",
    "bakery",
    "atm",
    "house",
    "shoes",
    "building",
    "car_rental",
    "mall",
    "stadium",
    "school",
    "slipway",
    "zoo",
    "chemist",
    "hardware",
    "motel",
    "university",
    "farm",
    "college",
    "fuel",
    "car_repair",
    "restaurant",
    "playground",
    "garden_centre",
    "stationery",
    "wood",
    "information",
    "suburb",
    "artwork",
    "general"
]

COLUMNS_OF_INTEREST = [
    "geo_id",
    "country",
    "country_code",
    "city",
    "town",
    "village"
]

RG_FILE_1000 = "rg_cities1000.csv"
RG_FILE_5000 = "rg_cities5000.csv"
RG_FILE_15000 = "rg_cities15000.csv"

A = 6378.137  # major axis in kms
E2 = 0.00669437999014


def singleton(cls):
    instances = {}

    def getinstance(mode=1, precision_mode=2):
        if cls not in instances:
            instances[cls] = cls(mode=mode,
                                 precision_mode=precision_mode)
        return instances[cls]

    return getinstance


def parse_address(local_filename):
    df = pd.read_csv(local_filename)

    df.address = df.address.apply(lambda x: literal_eval(x))

    for col in OSM_COLUMNS:
        df[col] = df.address.apply(
            lambda x: x.get(col, None) \
                if x.get(col, None) is None \
                else str(x.get(col, None)))

    df.drop(["address"], axis=1, inplace=True)

    df.to_csv(local_filename, index=False)


@singleton
class OSM_RG:
    def __init__(self, mode=1, precision_mode=2):
        self.mode = mode

        if precision_mode == 0:
            loc_path = RG_FILE_1000
        elif precision_mode == 1:
            loc_path = RG_FILE_5000
        else:
            loc_path = RG_FILE_15000

        if not os.path.exists(loc_path):
            loc_path = rel_path(loc_path)

        # coordinates, locations = self.extract(path)
        coordinates, self.locations = self.extract(loc_path)

        if mode == 1:  # Single-process
            self.tree = KDTree(coordinates)
        else:  # Multi-process
            self.tree = KDTree_MP.cKDTree_MP(coordinates)

    def query(self, coordinates):
        """
        Find closest match to this list of coordinates
        """
        try:
            if self.mode == 1:
                distances, indices = self.tree.query(coordinates, k=1)
            else:
                distances, indices = self.tree.pquery(coordinates, k=1)
        except ValueError as e:
            raise e
        else:
            return [self.locations[index] for index in indices]

    def extract(self, local_filename):
        """
        Extract geocode data from zip
        """
        if os.path.exists(local_filename):
            df = pd.read_csv(local_filename)
            # rows = csv.DictReader(open(local_filename, "rt"))
        elif "rg_cities" in local_filename:
            url_filename = \
                local_filename[
                local_filename.rfind("/") + 4:local_filename.rfind(".")]
            gn_cities_url = GN_URL + url_filename + ".zip"

            cities_zipfilename = url_filename + ".zip"
            cities_filename = url_filename + ".txt"

            if not os.path.exists(cities_zipfilename):
                import urllib.request
                urllib.request.urlretrieve(gn_cities_url,
                                           cities_zipfilename)

            z = zipfile.ZipFile(open(cities_zipfilename, "rb"))
            open(cities_filename, "wb").write(z.read(cities_filename))

            df = pd.read_csv(cities_filename, delimiter="\t",
                             names=sorted(GN_COLUMNS, key=GN_COLUMNS.get))
            df.drop([x for x in GN_COLUMNS if x not in GN_COLUMNS_OF_INTEREST],
                    axis=1, inplace=True)

            geolocator = osm_geolocator()
            address_list = []
            with click.progressbar(length=len(df),
                                   label="reversing geodata") as bar:
                for i, row in df.iterrows():
                    time.sleep(1)
                    bar.update(1)
                    lat = row["latitude"]
                    lon = row["longitude"]

                    address = None
                    while address is None:
                        try:
                            address = geolocator.reverse(
                                (lat, lon), timeout=10,
                                language="en").raw["address"]
                        except Exception as ex:
                            time.sleep(5)
                            address = None

                    address_list.append(address)

            df["address"] = address_list
            df.rename(columns={"latitude": "lat",
                               "longitude": "lon",
                               "geoNameId": "geo_id"},
                      inplace=True)
            df.to_csv(local_filename, index=False)

            os.remove(cities_filename)
            os.remove(cities_zipfilename)

            parse_address(local_filename)
        else:
            raise Exception("Geocoded file not found", local_filename)

        # Load all the coordinates and locations
        geo_coords, locations = [], []
        for i, row in df.iterrows():
            geo_coords.append((float(row["lat"]), float(row["lon"])))
            locations.append(
                {k: v for k, v in row.items() if k in COLUMNS_OF_INTEREST})
        return geo_coords, locations


def rel_path(filename):
    return os.path.join(os.getcwd(), os.path.dirname(__file__), filename)


def get(geo_coord, mode=1, precision_mode=2):
    if type(geo_coord) != tuple or type(geo_coord[0]) != float:
        raise TypeError("Expecting a tuple")

    rg = OSM_RG(mode=mode, precision_mode=precision_mode)
    return rg.query([geo_coord])[0]


def search(geo_coords, mode=1, precision_mode=2):
    if not isinstance(geo_coords, (tuple, list)):
        raise TypeError("Expecting a tuple or a tuple/list of tuples")
    elif not isinstance(geo_coords[0], tuple):
        geo_coords = [geo_coords]

    rg = OSM_RG(mode=mode, precision_mode=precision_mode)
    return rg.query(geo_coords)


if __name__ == "__main__":
    print("Testing single coordinate through get...")
    city = (-33.86785, 151.20732)
    print("Reverse geocoding 1 city...")
    result = search(city)
    print(result)
