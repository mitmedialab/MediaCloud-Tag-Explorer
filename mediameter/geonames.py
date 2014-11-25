import os, json, logging, csv
import mediameter

logger = logging.getLogger(__name__)

GEONAMES_COUNTRY_FILE = os.path.join(mediameter.base_dir, 'geonames-country-list.csv')

def countryLookup():
    lookup = {}
    with open(GEONAMES_COUNTRY_FILE, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        spamreader.next()
        for row in spamreader:
            lookup[row[0]] = {
                'id':row[0],
                'countryCode':row[1],
                'name':row[2]
            }
    return lookup

country_cache = countryLookup()

def countryInfo(geonames_id):
    if geonames_id in country_cache:
        return country_cache[geonames_id]
    return None
