#! /usr/bin/env python

import ConfigParser
import json
from pubsub import pub
import nltk

from readability.readabilitytests import ReadabilityTool

from mediacloud.api import MediaCloud
from mediacloud.storage import *
import mediacloud.examples

'''
This example file fetches the latest 25 stories from MediaCloud and saves their metadata 
to a 'mediacloud' database.  It adds in the computed Flesh-Kindcaid reading grade Level to 
the story pre-save event subscription.
'''

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))

config = ConfigParser.ConfigParser()
config.read('mc-client.config')

# set up a connection to a local DB
# db = CouchStoryDatabase('mediacloud', config.get('db','host'), config.get('db','port') )
db = MongoStoryDatabase('mediacloud')

# connect to MC and fetch some articles
mc = MediaCloud( config.get('api','user'), config.get('api','pass') )
results = mc.allProcessed()
print "Fetched "+str(len(results))+" stories"

def addFleshKincaidGradeLevelToStory(db_story, raw_story):
    '''
    Simple hook to add the Flesch-Kincaid Grade to the database.  This uses a pre-save
    callback to add a new 'fk_grade_level' column. This relies on patched ntlk_contrib
    code, stored in the readability module (because their published code don't work!)
    '''
    text = raw_story['story_text']
    r = ReadabilityTool()
    gradeLevel = None
    if isEnglish(text):
        try:
            if (text!=None) and (len(text)>0) :
                gradeLevel = r.FleschKincaidGradeLevel(text.encode('utf-8'))
        except (KeyError, UnicodeDecodeError):
            pass
    if (gradeLevel != None):
        db_story['fk_grade_level'] = gradeLevel

def isEnglish(text):
    '''
    A simple hack to detect if an article is in english or not.
    See http://www.algorithm.co.il/blogs/programming/python/cheap-language-detection-nltk/
    '''
    matchesEnglish = False
    if (text!=None) and (len(text)>0) :
        text = text.lower()
        words = set(nltk.wordpunct_tokenize(text))
        matchesEnglish = len(words & ENGLISH_STOPWORDS) > 0
    return matchesEnglish

# set up my callback function that adds the Flesh-Kincaid reading grade level
pub.subscribe(addFleshKincaidGradeLevelToStory, StoryDatabase.EVENT_PRE_STORY_SAVE)

# save all the stories in the db (this will fire the callback above)
saved = 0
for story in results:
    worked = db.addStory(story)
    if worked:
      saved = saved + 1

print "Saved "+str(saved)+" stories"
