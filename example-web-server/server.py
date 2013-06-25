import os, sys
from flask import Flask, render_template
import json

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
import mediacloud
import mediacloud.api
from mcexamples.db import ExampleMongoStoryDatabase

app = Flask(__name__)

db = ExampleMongoStoryDatabase('mediacloud')

@app.route("/")
def index():
    story_count_by_media_id = db.storyCountByMediaId()
    media_info = {}
    media_info_json = []
    for media_id in story_count_by_media_id.keys():
        clean_id = str(int(media_id))
        media_info[clean_id] = {
            'id': int(media_id),
            'name': _media_name(media_id),
            'story_count': story_count_by_media_id[media_id]
        }
        media_info_json.append({
            'id': int(media_id),
            'name': _media_name(media_id),            
        })
    story_count = db.storyCount()
    return render_template("base.html",
        story_count = story_count,
        english_story_pct = int(round(100*db.englishStoryCount()/story_count)),
        media_info = media_info,
        media_info_json = json.dumps(media_info_json),
        max_story_id = db.getMaxStoryId()
    )

@app.route("/media/all/info")
def all_domain_info():
    return render_template("data.js",
        reading_level_info = _reading_level_info()
    )

@app.route("/media/<media_id>/info")
def domain_info(media_id):
    return render_template("data_for_media_source.js",
        media_name = _media_name(media_id),
        story_count = db.storyCountForMediaId(media_id),
        reading_level_info = _reading_level_info(media_id)
    )

def _media_name(media_id):
    return mediacloud.api.mediaSource(int(media_id))['name']

def _reading_level_info(domain=None, items_to_show=20):
    data = db.storyReadingLevelFreq(domain)
    return _assemble_info(data,1,items_to_show)

def _assemble_info(data,bucket_size,items_to_show):
    values = []
    for key in sorted(data.iterkeys()):
        values.append(data[key])
    values = values[:items_to_show]
    return {'values': values,
            'values_json': json.dumps(values),
            'final_bucket': bucket_size*items_to_show,
            'items_to_show': items_to_show,
            'biggest_value': max(values)
    }

if __name__ == "__main__":
    app.debug = True
    app.run()
