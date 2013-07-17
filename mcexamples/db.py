import math
from mediacloud.storage import MongoStoryDatabase
from bson.code import Code

class ExampleMongoStoryDatabase(MongoStoryDatabase):
    '''
    Simply supports the server example by making queries easier
    '''

    def englishStoryCount(self):
        return self._db.stories.find({"is_english":True}).count()

    def storyReadingLevelFreq(self,media_id):
        # @see http://wiki.summercode.com/mongodb_aggregation_functions_and_ruby_grouping_elaborated
        # @see http://api.mongodb.org/python/2.2.1/api/pymongo/collection.html
        key = ['fk_grade_level']
        condition = {"is_english": True}
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        if media_id != None:
            condition["media_id"] = int(media_id)
        rawResults = self._db.stories.group(key, condition, initial, reduce);
        results = self._resultsToDict(rawResults,'fk_grade_level', [0,21])
        # fill in any blanks so we can chart this easily
        if len(results)==0: # handle situation where there are no grade levels in the DB
            maxLevel = 20
        else:
            maxLevel = int(max(results.keys(), key=int))
        for level in range(maxLevel):
            if not (level in results.keys()):
                results[level] = 0
        return results

    def storyCountForMediaId(self, media_id):
        return self._db.stories.find({'media_id':int(media_id)}).count()

    def storyCountByMediaId(self):
        key = ['media_id']
        condition = None
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        rawResults = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(rawResults,'media_id')

    # assumes key is integer!
    def _resultsToDict(self, rawResults, id_key, key_min_max=None):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in rawResults:
            key_ok = False
            try:
                # first make sure key is an integer
                throwaway = int(doc[id_key])
                # now check optional range
                if key_min_max!=None:
                    key = int(doc[id_key])
                    if key>key_min_max[0] and key<key_min_max[1]:
                        key_ok = True
                else:
                    key_ok = True
            except:
                # we got NaN, so ignore it
                key_ok = False
            if key_ok:
                results[ int(doc[id_key]) ] = doc['value']
        print results.keys()
        return results
