import os, json, logging
import mediameter

logger = logging.getLogger(__name__)

TAG_SETS_PER_PAGE = 100
TAGS_PER_PAGE = 100
TAG_DATA_FILE = os.path.join(mediameter.base_dir, 'mediacloud-tags.json')

def sentenceCount(tags_id):
    return mediameter.mc_server.sentenceCount('+tags_id_stories:'+str(tags_id))['count']

def allTagSets():
    '''
    Return list of all tag sets, with tags under each
    '''
    if os.path.isfile(TAG_DATA_FILE):
        logger.debug("Loading tag sets from "+TAG_DATA_FILE)
        json_data=open(TAG_DATA_FILE)
        data = json.load(json_data)
        return data
    # fetch all the tag sets
    logger.info("Fething tag sets from MediaCloud:")
    tag_sets = []
    more_tag_sets_id = True
    max_tag_set = 0
    while more_tag_sets_id:
        logger.debug("  from "+str(max_tag_set))
        results = mediameter.mc_server.tagSetList(max_tag_set, TAG_SETS_PER_PAGE)
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
            results = mediameter.mc_server.tagList(tag_set['tag_sets_id'],max_tags_id,TAGS_PER_PAGE)
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
        logger.info("Wrote tag sets to "+TAG_DATA_FILE)
    return tag_sets

def publicMediaTagSets():
    '''
    Return list of all the public tag sets, with public tags under each
    '''
    tag_sets = allTagSets()
    logger.debug("Finding just public data sets")
    tag_sets_to_remove = []
    for tag_set in tag_sets:
        logger.debug("  looking into tag set '"+tag_set['name']+"' "+str(tag_set['tag_sets_id']))
        if tag_set['show_on_media'] in (0, None):
            logger.debug("  private - checking tags")
            removed_tag_count = 0
            tags_to_remove = []
            for tag in tag_set['tags']:
                if tag['show_on_media'] in (0, None):
                    tags_to_remove.append(tag)
                    #logger.debug("    removing tag '"+tag['tag']+"'"+str(tag['tags_id']))
            [tag_set['tags'].remove(tag) for tag in tags_to_remove]
            logger.debug("    removed "+str(removed_tag_count)+" tags")
        if len(tag_set['tags'])==0:
            tag_sets_to_remove.append(tag_set)
    [tag_sets.remove(tag_set) for tag_set in tag_sets_to_remove]
    return tag_sets
