from mediacloud.storage import MongoStoryDatabase

class ExampleMongoStoryDatabase(MongoStoryDatabase):
    '''
    Simply supports the server example by making queries easier
    '''

    def englishStoryCount(self):
        return self._db.stories.find({"is_english":True}).count()

    def storyLengthFreq(self, bucketSize=200, domain=None):
        if domain == None:
            map = Code("function () {"
                    "   var key = "+str(bucketSize)+"*Math.floor(this.word_count/"+str(bucketSize)+");"
                    "   if(!isNaN(key)) emit(key,1);"
                    "}")
            results_name = "story_length_freq"
        else:
            domain_parts = domain.split(".")
            map = Code("function () {"
                    "   if(this.domain.domain==\""+domain_parts[0]+"\" && this.domain.tld==\""+domain_parts[1]+"\"){"
                    "       var key = "+str(bucketSize)+"*Math.floor(this.word_count/"+str(bucketSize)+");"
                    "       if(!isNaN(key)) emit(key,1);"
                    "   }"
                    "}")
            results_name = "story_length_freq_"+domain[0]+"_"+domain[1]
        reduce = Code("function (key, values) {"
                        "   var total = 0;"
                        "   for (var i = 0; i < values.length; i++) {"
                        "       total += values[i];"
                        "   }"
                        "   return total;"
                        "}")
        rawResults = self._db.stories.map_reduce(map, reduce, results_name)
        results = self._resultsToDict(rawResults)
        # fill in any blanks so we can chart this easily
        maxWords = max(results.keys(), key=int)
        bucketCount = int(math.ceil( maxWords / bucketSize ))
        for bucket in range(bucketCount):
            if not (bucket*bucketSize in results.keys()):
                results[bucket*bucketSize] = 0
        return results

    def storyReadingLevelFreq(self,domain):
        if domain == None:
            map = Code("function () {"
                    "       if(this.fk_grade_level){"
                    "           emit(Math.round(this.fk_grade_level),1);"
                    "       }"
                    "}")
            results_name = "story_reading_level_freq"
        else:
            domain_parts = domain.split(".")
            map = Code("function () {"
                    "     if(this.fk_grade_level){"
                    "       if(this.domain.domain==\""+domain_parts[0]+"\" && this.domain.tld==\""+domain_parts[1]+"\"){"
                    "         emit(Math.round(this.fk_grade_level),1);"
                    "     }"
                    "   }"                    
                    "}")
            results_name = "story_reading_level_freq_"+domain[0]+"_"+domain[1]      
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

    def storyCountForSource(self, domain):
        parts = domain.split('.')
        return self._db.stories.find({'domain.domain':parts[0],'domain.tld':parts[1]}).count()

    def storyCountBySource(self):
        map = Code("function () {"
                    "   emit(this.domain.domain+'.'+this.domain.tld, 1);"
                    "}")
        reduce  = Code("function (key, values) {"
                        "   var total = 0;"
                        "   for (var i = 0; i < values.length; i++) {"
                        "       total += values[i];"
                        "   }"
                        "   return total;"
                        "}")
        rawResults = self._db.stories.map_reduce(map, reduce, "story_count_by_source")
        return self._resultsToDict(rawResults)

    def _resultsToDict(self, rawResults):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in rawResults.find():
            results[ doc['_id'] ] = doc['value']
        return results
