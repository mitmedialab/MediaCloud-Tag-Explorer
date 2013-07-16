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
        results = self._resultsToDict(rawResults)
        # fill in any blanks so we can chart this easily
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

    def _resultsToDict(self, rawResults, id_key='_id'):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in rawResults:
            if not math.isnan(doc[id_key]):
                results[ doc[id_key] ] = doc['value']
        return results
