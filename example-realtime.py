#! /usr/bin/env python
import time
start_time = time.time()

import ConfigParser
import json
from pubsub import pub
import nltk
import logging

from mediacloud.api import MediaCloud
from mediacloud.storage import *
import mcexamples.algorithms

'''
This example is meant to be run from a cron job on a server.  It fetches all stories 
created after the latest one it has in it's db.  It saves the metadata for all those to 
a 'mediacloud' database.
'''

MAX_PAGES_TO_FETCH = 5
CONFIG_FILENAME = 'mc-client.config'

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILENAME)

# setup logging
logging.basicConfig(filename='mc-realtime.log',level=logging.DEBUG)
log = logging.getLogger('mc-realtime')
log.info("---------------------------------------------------------------------------")

# setup a connection to a local DB
#db = CouchStoryDatabase('mediacloud', config.get('db','host'), config.get('db','port') )
db = MongoStoryDatabase('mediacloud')

# setup the mediacloud connection
mc = MediaCloud( config.get('api','user'), config.get('api','pass') )

max_story_id = db.getMaxStoryId()

# set up my callback function that adds the reading grade level to the story
pub.subscribe(mcexamples.algorithms.addReadingLevelToStory, StoryDatabase.EVENT_PRE_STORY_SAVE)

# set up a callback that adds the name of the media source to the story
pub.subscribe(mcexamples.algorithms.addSourceNameToStory, StoryDatabase.EVENT_PRE_STORY_SAVE)

# save all the stories in the db (this will fire the callback above)
saved = 0
first_page = int(config.get('api','first_page'))
for page in xrange(MAX_PAGES_TO_FETCH):
  query_page = first_page+page
  results = mc.allProcessed(query_page)
  page_has_existing_stories = False
  log.info("Fetched "+str(len(results))+" stories (page "+str(query_page)+")")
  for story in results:
    #if int(story['stories_id']) < int(max_story_id):
      #log.warning("  Story id "+str(story['stories_id'])+" is lower than max id ("+str(max_story_id)+")!"); 
      #log.info("  Stopping on page "+str(query_page)+" because found a story lower than existing max id")
      #page_has_existing_stories = True
      #break
    #else:
    worked = db.addStory(story)
    if worked:
      saved = saved + 1
    else:
      log.warning("  unable to save story "+str(story['stories_id']))
  if page_has_existing_stories:
    break # bail once we start getting stories we should have already
  config.set('api','first_page',query_page)
  with open(CONFIG_FILENAME,'wb') as config_file_handle: 
    config.write(config_file_handle)

max_story_id = db.getMaxStoryId()

end_time = time.time()
duration = end_time - start_time
log.info("Saved "+str(saved)+" stories - new max id "+str(max_story_id))
if saved > 0:
  log.info("  took "+str(duration)+" secs ("+str(round(duration/saved,2))+" secs per story)")
