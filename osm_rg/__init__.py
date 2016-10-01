##
# Author: Kolesnikov Sergey
##
import os
from scipy.spatial import cKDTree as KDTree
try: # ide version
    from osm_rg import cKDTree_MP as KDTree_MP
except: # script version
    from cKDTree_MP import cKDTree_MP as KDTree_MP


import pandas as pd

RG_FILE = "wikidata_cities.csv"

A = 6378.137  # major axis in kms
E2 = 0.00669437999014


def singleton(cls):
    instances = {}

    def getinstance(mode=1):
        if cls not in instances:
            instances[cls] = cls(mode=mode)
        return instances[cls]

    return getinstance


@singleton
class OSM_RG:
    def __init__(self, mode=1):
        self.mode = mode

        loc_path = RG_FILE
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
        else:
            raise Exception("Geocoded file not found", local_filename)

        # Load all the coordinates and locations
        geo_coords, locations = [], []
        for i, row in df.iterrows():
            geo_coords.append((float(row["latitude"]), float(row["longitude"])))
            locations.append({k: v for k, v in row.items()})
        return geo_coords, locations


def rel_path(filename):
    return os.path.join(os.getcwd(), os.path.dirname(__file__), filename)


def get(geo_coord, mode=1):
    if type(geo_coord) != tuple or type(geo_coord[0]) != float:
        raise TypeError("Expecting a tuple")

    rg = OSM_RG(mode=mode)
    return rg.query([geo_coord])[0]


def search(geo_coords, mode=1, precision_mode=2):
    if not isinstance(geo_coords, (tuple, list)):
        raise TypeError("Expecting a tuple or a tuple/list of tuples")
    elif not isinstance(geo_coords[0], tuple):
        geo_coords = [geo_coords]

    rg = OSM_RG(mode=mode)
    return rg.query(geo_coords)


if __name__ == "__main__":
    print("Testing single coordinate through get...")
    city = (-33.86785, 151.20732)
    print("Reverse geocoding 1 city...")
    result = search(city)
    print(result)
