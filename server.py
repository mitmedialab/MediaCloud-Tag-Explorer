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
logging.basicConfig(filename=os.path.join(base_dir,'mc-tag-explorer.log'),level=logging.INFO)
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
    tag_set_name = "rahulb@media.mit.edu"
    tag_prefix = "geonames"
    # grab just the geo tag set
    all_tag_sets = mediameter.tags.allTagSets()
    tag_sets = [ tag_set for tag_set in all_tag_sets if tag_set_name in tag_set['name']]
    geo_tag_set = tag_sets[0]
    # remove any non-geo ones and add in country details
    tags_to_remove = []
    for tag in geo_tag_set['tags']:
        if tag_prefix in tag['tag']:
            geonames_id = tag['tag'][9:]
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

if __name__ == "__main__":
    app.debug = True
    app.run()
