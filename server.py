import os, sys, time, json, logging, csv
from operator import itemgetter
from flask import Flask, render_template, jsonify, request, redirect, url_for
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

@app.route("/tags/<tags_id>")
def tag_info(tags_id):
    tag = mediameter.tags.tag(tags_id)
    # add in any geographic info (if it is in the geo tag set)
    geoname = None
    if tag['tag_sets_id']==mediameter.tags.geoTagSetId():
        geoname = _geoname_from_tag(tag)
    # add in usage stats
    sentences_in_tagged_stories = mediameter.mc_server.sentenceCount("*","+tags_id_stories:"+tags_id)['count']
    sentences_tagged = mediameter.mc_server.sentenceCount("*","+tags_id_story_sentences:"+tags_id)['count']
    return render_template("tag-info.html",
        tag = tag,
        geoname = geoname,
        sentences_in_tagged_stories = {
            'count':sentences_in_tagged_stories,
            'search_url':'https://dashboard.mediameter.org/#query/["+tags_id_stories:'+tags_id+'"]/[{}]/[""]/[""]/[{"uid":1}]'
        },
        sentences_tagged = {
            'count':sentences_tagged,
            'search_url':'https://dashboard.mediameter.org/#query/["+tags_id_story_sentences:'+tags_id+'"]/[{}]/[""]/[""]/[{"uid":2}]'
        }
    )

@app.route("/tags/country")
def country_tags():
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

@app.route("/tags/search",methods=['POST'])
def search():
    search_type = request.form['searchType']
    search_id = request.form['searchId']
    if search_type=="tag_id":
        return redirect(url_for('tag_info',tags_id=search_id))
    elif search_type=="geoname_id":
        return redirect(url_for('tag_by_geonames_id', geonames_id=search_id))
    return abort(400)

@app.route("/tags/for_geoname/<geonames_id>")
def tag_by_geonames_id(geonames_id):
    tag = mediameter.mc_server.tagList(tag_sets_id=mediameter.tags.geoTagSetId(),name_like="geonames_"+str(geonames_id),rows=1)[0]
    return redirect(url_for('tag_info', tags_id=tag['tags_id']))

@app.route("/stories/<story_id>/map")
def story_map(story_id):
    geo_tag_set_id = mediameter.tags.geoTagSetId()
    story = mediameter.mc_server.story(story_id,sentences=True)
    about_geonames = [_geoname_from_tag(t) for t in story['story_tags'] if t['tag_sets_id']==geo_tag_set_id]
    sentence_tag_ids = []
    for sentence in story['story_sentences']:
        sentence['geonames'] = [_geoname_from_tag(mediameter.tags.tag(tag_id)) for tag_id in sentence['tags']]
    mentioned_geonames = []
    for s in story['story_sentences']:
        mentioned_geonames = mentioned_geonames + s['geonames']
    return render_template('story-map.html', story=story, mentioned_geonames=mentioned_geonames, about_geonames=about_geonames)

def _geoname_from_tag(tag):
    geonames_id = mediameter.tags.geonamesIdFromTagName(tag['tag'])
    return mediameter.geonames.geoname(geonames_id)

@app.template_filter('number_format')
def number_format(value):
    return '{:,}'.format(value)

if __name__ == "__main__":
    app.debug = True
    app.run()
