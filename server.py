import os
import logging
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.serving import run_simple

import tagexplorer.tags
import tagexplorer.geonames

app = Flask(__name__)


@app.route("/")
@app.route("/tags/public")
def index():
    tag_sets = tagexplorer.tags.public_media_tag_sets()
    return render_template("public-tags.html", tag_sets=tag_sets)


@app.route("/tags/<tags_id>")
def tag_info(tags_id):
    tag = tagexplorer.tags.tag(tags_id)
    # add in any geographic info (if it is in the geo tag set)
    geoname = None
    if tag['tag_sets_id']==tagexplorer.tags.geo_tag_set_id():
        geoname = _geoname_from_tag(tag)
    # add in usage stats
    tagged_stories_count = tagexplorer.mc_server.storyCount("* AND tags_id_stories:{}".format(tags_id))['count']
    # TODO: add in media list count
    return render_template("tag-info.html", tag=tag, geoname=geoname,
                           tagged_stories={
                               'count': tagged_stories_count,
                               'search_url': 'https://explorer.mediacloud.org/#/queries/search?qs=%5B%7B%22label%22%3A%22*%20AND%20tags_id_stories%3A88836...%22%2C%22q%22%3A%22*%20AND%20tags_id_stories%3A{}%22%2C%22color%22%3A%22%231f77b4%22%2C%22startDate%22%3A%222020-01-01%22%2C%22endDate%22%3A%222020-06-01%22%2C%22sources%22%3A%5B%5D%2C%22collections%22%3A%5Bnull%5D%2C%22searches%22%3A%5B%5D%7D%5D'.format(tags_id)
                           })


@app.route("/tags/country")
def country_tags():
    tag_prefix = "geonames"
    # grab just the geo tag set
    geo_tag_set = tagexplorer.tags.geo_tag_set()
    # remove any non-geo ones and add in country details
    tags_to_remove = []
    for tag in geo_tag_set['tags']:
        if tag_prefix in tag['tag']:
            geonames_id = tagexplorer.tags.geonames_id_from_tag_name(tag['tag'])
            tag['geonames_id'] = geonames_id
            tag['geoname'] = tagexplorer.geonames.country_info(geonames_id)
            if tag['geoname'] is None:
                tags_to_remove.append(tag)
        else:
            tags_to_remove.append(tag)
    [geo_tag_set['tags'].remove(tag) for tag in tags_to_remove]
    return render_template("country-tags.html", tag_set=geo_tag_set)


@app.route("/tags/search",methods=['POST'])
def search():
    search_type = request.form['searchType']
    search_id = request.form['searchId']
    if search_type == "tag_id":
        return redirect(url_for('tag_info',tags_id=search_id))
    elif search_type == "geoname_id":
        return redirect(url_for('tag_by_geonames_id', geonames_id=search_id))
    elif search_type == "story_id":
        return redirect(url_for('story_map', story_id=search_id))
    elif search_type == "sentence_id":
        return redirect(url_for('sentence_map', story_sentences_id=search_id))
    return abort(400)


@app.route("/tags/for_geoname/<geonames_id>")
def tag_by_geonames_id(geonames_id):
    tag = tagexplorer.mc_server.tagList(tag_sets_id=tagexplorer.tags.geo_tag_set_id(),
                                        name_like="geonames_"+str(geonames_id),
                                        rows=1)[0]
    return redirect(url_for('tag_info', tags_id=tag['tags_id']))


@app.route("/stories/<story_id>/map")
def story_map(story_id):
    geo_tag_set_id = tagexplorer.tags.geo_tag_set_id()
    story = tagexplorer.mc_server.story(story_id,sentences=True)
    about_geonames = [_geoname_from_tag(t) for t in story['story_tags'] if t['tag_sets_id']==geo_tag_set_id]
    for sentence in story['story_sentences']:
        sentence['geonames'] = [_geoname_from_tag(tagexplorer.tags.tag(tag_id)) for tag_id in sentence['tags']]
    mentioned_geonames = []
    for s in story['story_sentences']:
        mentioned_geonames = mentioned_geonames + s['geonames']
    unique_mentioned_geonames = {g['id']: g for g in mentioned_geonames}.values()
    return render_template('story-map.html', story=story, mentioned_geonames=unique_mentioned_geonames,
                           about_geonames=about_geonames)


@app.route("/sentences/<story_sentences_id>/map")
def sentence_map(story_sentences_id):
    sentence = tagexplorer.mc_server.sentence(story_sentences_id)
    return redirect("/stories/%s/map#sentence%s" % (sentence['stories_id'],sentence['story_sentences_id']))


def _geoname_from_tag(tag):
    geonames_id = tagexplorer.tags.geonames_id_from_tag_name(tag['tag'])
    return tagexplorer.geonames.geoname(geonames_id)


@app.template_filter('number_format')
def number_format(value):
    return '{:,}'.format(value)


if __name__ == "__main__":
    run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True)
