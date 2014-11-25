import os, sys, time, json, logging, ConfigParser, csv
from operator import itemgetter
from flask import Flask, render_template
import jinja2

currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import mediacloud
import mediacloud.api

TAG_SETS_PER_PAGE = 100
TAGS_PER_PAGE = 100

TAG_DATA_FILE = 'static/data/mediacloud-tags.json'

app = Flask(__name__)

# setup logging
logger = logging.getLogger(__name__)
log_file = logging.FileHandler('mc-api-examples-server.log')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_file)
logger.info("---------------------------------------------------------------------------")

# connect to the database
config = ConfigParser.ConfigParser()
config.read(parentdir+'/mc-client.config')
mc = mediacloud.api.MediaCloud( config.get('api','key') )

def geonameCountryLookup():
    lookup = {}
    file_path = os.path.join(currentdir,'geonames-country-list.csv');
    with open(file_path, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        spamreader.next()
        for row in spamreader:
            lookup[row[0]] = {
                'id':row[0],
                'countryCode':row[1],
                'name':row[2]
            }
    return lookup

geonames_cache = geonameCountryLookup()

def allTagSets():
    if os.path.isfile(TAG_DATA_FILE):
        json_data=open(TAG_DATA_FILE)
        data = json.load(json_data)
        logger.debug("Loading tag sets from "+TAG_DATA_FILE)
        return data
    # fetch all the tag sets
    logger.debug("Fething tag sets:")
    tag_sets = []
    more_tag_sets_id = True
    max_tag_set = 0
    while more_tag_sets_id:
        logger.debug("  from "+str(max_tag_set))
        results = mc.tagSetList(max_tag_set, TAG_SETS_PER_PAGE)
        #print json.dumps(results)
        tag_sets = tag_sets + results
        more_tag_sets_id = len(results)>0
        if len(results)>0:
            max_tag_set = results[-1]['tag_sets_id']
    logger.debug("  found "+str(len(tag_sets))+" sets")
    # now fill in all the tags
    for tag_set in tag_sets:
        logger.debug("Fetching tags in set "+str(tag_set['tag_sets_id']))
        tags = []
        more_tags = True
        max_tags_id = 0
        while more_tags:
            logger.debug(" from "+str(max_tags_id))
            results = mc.tagList(tag_set['tag_sets_id'],max_tags_id,TAGS_PER_PAGE)
            #print json.dumps(results)
            tags = tags + results
            more_tags = len(results) > 0
            if len(results)>0:
                max_tags_id = results[-1]['tags_id']
        logger.debug("    found "+str(len(tags))+" tags in the set")
        tag_set['tags'] = tags
    # dump to a file
    with open(TAG_DATA_FILE, 'w') as outfile:
        json.dump(tag_sets, outfile)
        logger.debug("Wrote tag sets to "+TAG_DATA_FILE)
    return tag_sets

def publicMediaTagSets():
    tag_sets = allTagSets()
    logger.debug("Finding just public data sets")
    tag_sets_to_remove = []
    for tag_set in tag_sets:
        logger.debug("  looking into tag set '"+tag_set['name']+"' "+str(tag_set['tag_sets_id']))
        if tag_set['show_on_media'] in (0, None):
            logger.debug("  private - checking tags")
            removed_tag_count = 0
            tags_to_remove = []
            for tag in tag_set['tags']:
                if tag['show_on_media'] in (0, None):
                    tags_to_remove.append(tag)
                    #logger.debug("    removing tag '"+tag['tag']+"'"+str(tag['tags_id']))
            [tag_set['tags'].remove(tag) for tag in tags_to_remove]
            logger.debug("    removed "+str(removed_tag_count)+" tags")
        if len(tag_set['tags'])==0:
            tag_sets_to_remove.append(tag_set)
    [tag_sets.remove(tag_set) for tag_set in tag_sets_to_remove]
    return tag_sets

@app.route("/")
def index():
    tag_sets = publicMediaTagSets()
    return render_template("tags.html",
        tag_sets = tag_sets
    )

def geoname_lookup(geonames_id):
    if geonames_id in geonames_cache:
        return geonames_cache[geonames_id]
    return None

@app.route("/geonames")
def locations():
    tag_set_name = "rahulb@media.mit.edu"
    tag_prefix = "geonames"
    all_tag_sets = allTagSets()
    tag_sets = [ tag_set for tag_set in all_tag_sets if tag_set_name in tag_set['name']]
    geo_tag_set = tag_sets[0]
    # remove any non-geo ones
    tags_to_remove = []
    for tag in geo_tag_set['tags']:
        if tag_prefix in tag['tag']:
            geonames_id = tag['tag'][9:]
            tag['geonames_id'] = geonames_id
            tag['geoname'] = geoname_lookup(geonames_id)
            if tag['geoname'] is None:
                tags_to_remove.append(tag)
        else:
            tags_to_remove.append(tag)
    [geo_tag_set['tags'].remove(tag) for tag in tags_to_remove]
    return render_template("geonames.html",
        tag_set = geo_tag_set
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
