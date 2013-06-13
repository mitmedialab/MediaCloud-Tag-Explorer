
import nltk
from mcexamples.readability.readabilitytests import ReadabilityTool

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))

'''
This file holds some simple example functions that process a story and add some piece
of metadata to it, for saving into the database.  You can base your (hopefully more 
useful) plugin on these examples.
'''

def addReadingLevelToStory(db_story, raw_story):
    '''
    Simple hook to add the Flesch-Kincaid Grade to the database.  This uses a pre-save
    callback to add a new 'fk_grade_level' column. This relies on patched ntlk_contrib
    code, stored in the readability module (because their published code don't work!)
    '''
    text = raw_story['story_text']
    r = ReadabilityTool()
    gradeLevel = None
    is_english = isEnglish(text)
    db_story['is_english'] = is_english
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
    English detection hack: are there any english stopwords in the text?
    See http://www.algorithm.co.il/blogs/programming/python/cheap-language-detection-nltk/
    '''
    matchesEnglish = False
    if (text!=None) and (len(text)>0) :
        text = text.lower()
        words = set(nltk.wordpunct_tokenize(text))
        matchesEnglish = len(words & ENGLISH_STOPWORDS) > 0
    return matchesEnglish
