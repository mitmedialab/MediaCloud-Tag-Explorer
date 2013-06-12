MediaCloud Python API Client Examples
=====================================

This is a set of examples to demonstrate how you can use the MediaCloud API python client
library.

Installation
------------

First [download the latest zip of the python api client module](https://github.com/c4fcm/MediaCloud-API-Client/tree/master/dist) 
and install it like this:

    python setup.py install

Now to run these examples make sure you have Python > 2.6 (and setuptools) and then install 
these python modules:
    
    pip install pypubsub
    pip install nltk
    pip install couchdb
    pip install pymongo
    
Install and run [CouchDB](http://couchdb.apache.org) or [MongoDb](http://mongodb.org) to store 
article info.

Copy the `mc-client.config.template` to `mc-client.config` and edit it, putting in the 
API username and password.  Then if you are using CouchDB run the `example_create_views.py` 
script to create the views that the various scripts and webpages use.

### Ubuntu

On Ubuntu, you may need to do this first to get nltk and pymongo to install:

    sudo apt-get install build-essential python-dev

### Setup NLTK

To run some of the examples, you need the `stopwords` corpora for NLTK. To get this, first
enter the python console.  Then do `import nltk`.  Then `nltk.download()`.  Then follow the
instructions and download the `stopwords` library.  To the same thing for the `punkt` library.

Examples
--------

### Adding Metadata via PubSub

If you want to light-weight synchrounous processing, you can add callbacks to modify the stories 
that you fetch before they are saved to the database.  This examples shows how to do that by adding
the word count to the story.

    python example-readability.py

