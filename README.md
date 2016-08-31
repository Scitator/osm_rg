OSM Reverse Geocoder
=================
A Python library for offline reverse geocoding. It improves on an existing library called [reverse-geocoder](https://github.com/thampiman/reverse-geocoder) developed by [Ajay Thampi]

## Features
1. Besides city/town and country code, this library also returns the nearest latitude and longitude and also administrative regions 1 and 2.
2. This library also uses a parallelised implementation of K-D trees which promises an improved performance especially for large inputs.
3. Many extra information from OSM

The K-D tree is populated with cities that have a population > 1000. The source of the data is [GeoNames](http://download.geonames.org/export/dump/).

### Dependencies
1. scipy
2. numpy
3. geopy
4. pandas
5. ast

## Usage
The library supports two modes:

1. Mode 1: Single-threaded K-D Tree (default, similar to [reverse_geocode] (https://pypi.python.org/pypi/reverse_geocode/1.0))
2. Mode 2: Multi-threaded K-D Tree

```python
import osm_rg as rg

city = (-33.86785, 151.20732)

results = rg.get(city) # default mode = 1, precision = 2

print results
```

The above code will output the following:
```
[{
    'town': nan, 'village': nan, 
    'country': 'Australia', 
    'city': 'Sydney', 
    'country_code': 'au', 
    'geo_id': 2147714
}]
```

If you'd like to use the multi-threaded K-D tree, set mode = 2 as follows:
```python
results = rg.get(city, mode=2)
```

## Acknowledgements
1. Major inspiration is from Ajay Thampi's [reverse_geocoder] (https://github.com/thampiman/reverse-geocoder) library
2. Parallelised implementation of K-D Trees is extended from this [article](http://folk.uio.no/sturlamo/python/multiprocessing-tutorial.pdf) by [Sturla Molden](https://github.com/sturlamolden)
3. Geocoded data is from [GeoNames](http://download.geonames.org/export/dump/)
