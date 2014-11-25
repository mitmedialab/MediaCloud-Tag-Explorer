import os, sys, time, json, logging, csv
from operator import itemgetter
from flask import Flask, render_template
import jinja2

import mediacloud
import mediacloud.api
from mediameter import mc_server, cliff_server
import mediameter.tags, mediameter.geonames

app = Flask(__name__)

# setup logging
base_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=os.path.join(base_dir,'mc-tag-explorer.log'),level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route("/")
@app.route("/tags/public")
def index():
    tag_sets = mediameter.tags.publicMediaTagSets()
    return render_template("public-tags.html",
        tag_sets = tag_sets
    )

@app.route("/tags/country")
def locations():
    tag_prefix = "geonames"
    # grab just the geo tag set
    geo_tag_set = mediameter.tags.geoTagSet()
    # remove any non-geo ones and add in country details
    tags_to_remove = []
    for tag in geo_tag_set['tags']:
        if tag_prefix in tag['tag']:
            geonames_id = mediameter.tags.geonamesIdFromTagName(tag['tag'])
            tag['geonames_id'] = geonames_id
            tag['geoname'] = mediameter.geonames.countryInfo(geonames_id)
            if tag['geoname'] is None:
                tags_to_remove.append(tag)
        else:
            tags_to_remove.append(tag)
    [geo_tag_set['tags'].remove(tag) for tag in tags_to_remove]
    return render_template("country-tags.html",
        tag_set = geo_tag_set
    )

@app.route("/tags/geo/<tags_id>")
def geonames(tags_id):
    tag = mediameter.tags.geoTag(tags_id)
    logger.debug(repr(tag))
    geonames_id = mediameter.tags.geonamesIdFromTagName(tag['tag'])
    geonames_info = mediameter.cliff_server.geonamesLookup(geonames_id)
    return render_template("geo-tag.html",
        tags_id = tags_id,
        geoname = geonames_info
    )    

if __name__ == "__main__":
    app.debug = True
    app.run()
