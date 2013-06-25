from mediacloud.storage import MongoStoryDatabase
from bson.code import Code

class ExampleMongoStoryDatabase(MongoStoryDatabase):
    '''
    Simply supports the server example by making queries easier
    '''

    def englishStoryCount(self):
        return self._db.stories.find({"is_english":True}).count()

    def storyReadingLevelFreq(self,media_id):
        if media_id == None:
            map = Code("function () {"
                    "       if(this.fk_grade_level){"
                    "           emit(Math.round(this.fk_grade_level),1);"
                    "       }"
                    "}")
            results_name = "story_reading_level_freq"
        else:
            map = Code("function () {"
                    "     if(this.fk_grade_level){"
                    "       if(this.media_id==\""+str(media_id)+"\"){"
                    "         emit(Math.round(this.fk_grade_level),1);"
                    "     }"
                    "   }"                    
                    "}")
            results_name = "story_reading_level_freq_"+str(media_id)
        reduce = Code("function (key, values) {"
                        "   var total = 0;"
                        "   for (var i = 0; i < values.length; i++) {"
                        "       total += values[i];"
                        "   }"
                        "   return total;"
                        "}")
        rawResults = self._db.stories.map_reduce(map, reduce, "story_reading_level_freq")
        results = self._resultsToDict(rawResults)
        print results
        # fill in any blanks so we can chart this easily
        maxLevel = int(max(results.keys(), key=int))
        for level in range(maxLevel):
            if not (level in results.keys()):
                results[level] = 0
        return results

    def storyCountForMediaId(self, media_id):
        return self._db.stories.find({'media_id':str(media_id)}).count()

    def storyCountByMediaId(self):
        map = Code("function () {"
                    "   emit(this.media_id, 1);"
                    "}")
        reduce  = Code("function (key, values) {"
                        "   var total = 0;"
                        "   for (var i = 0; i < values.length; i++) {"
                        "       total += values[i];"
                        "   }"
                        "   return total;"
                        "}")
        rawResults = self._db.stories.map_reduce(map, reduce, "story_count_by_media_id")
        return self._resultsToDict(rawResults)

    def _resultsToDict(self, rawResults):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in rawResults.find():
            results[ doc['_id'] ] = doc['value']
        return results
