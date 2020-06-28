import os
import logging
import csv
import tagexplorer

logger = logging.getLogger(__name__)

GEONAMES_COUNTRY_FILE = os.path.join(tagexplorer.base_dir, 'geonames-country-list.csv')

geonames_cache = {}  # id to geoname


def country_lookup():
    lookup = {}
    with open(GEONAMES_COUNTRY_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lookup[row['geonameid']] = {
                'id': row['geonameid'],
                'countryCode': row['#ISO'],
                'name': row['Country']
            }
    return lookup


country_cache = country_lookup()


def country_info(geonames_id):
    if geonames_id in country_cache:
        return country_cache[geonames_id]
    return None


# cache to reduce hits to cliff
def geoname(geonames_id):
    if geonames_id not in geonames_cache:
        result = tagexplorer.cliff_server.geonames_lookup(geonames_id)
        geonames_cache[geonames_id] = result
        logger.debug("added %s to geonames cache" % geonames_id)
    return geonames_cache[geonames_id]
