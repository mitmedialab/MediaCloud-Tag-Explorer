import os, sys, time, json, logging, ConfigParser
from operator import itemgetter
from flask import Flask, render_template
import jinja2

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
import mediacloud
import mediacloud.api

TAG_SETS_PER_PAGE = 100
TAGS_PER_PAGE = 100

TAG_DATA_FILE = 'static/data/mediacloud-tags.json'

app = Flask(__name__)

cache = {}  # in-memory cache, controlled by _get_from_cache and _set_in_cache helpers

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

def publicTagsSets():
    tag_sets = allTagSets()
    logger.debug("Finding just public data sets")
    for tag_set in tag_sets:
        if tag_set['show_on_media']==0:
            logger.debug("  looking into tag set "+str(tag_set['tag_sets_id']))
            for tag in tag_set['tags']:
                if tag['show_on_media'] in (0, None):
                    tag_set['tags'].remove(tag)
                    #logger.debug("  removing tag "+str(tag['tags_id']))
        if len(tag_set['tags'])==0:
            tag_sets.remove(tag_set)
    return tag_sets

@app.route("/")
def index():
    tag_sets = publicTagsSets()
    return render_template("tags.html",
        tag_sets = tag_sets
    )

if __name__ == "__main__":
    app.debug = True
    app.run()
