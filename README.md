MediaCloud Tag Explorer
=======================

Small server to let users explore tags in the MediaCloud system.  Originally 
created as an example of how to use the [MediaCloud API client](https://github.com/c4fcm/MediaCloud-API-Client/) in a web app.

Installation
------------

* install python 3.x
* `pip install -r requirements.txt`

Then create a `.env` or set these two environment variables:
* CLIFF_URL: url to a CLIFF install
* MEDIA_CLOUD_API_KEY: your Media Cloud API key

Use
---

Run this command and then visit `localhost:5000` with a web browser
```
python server.py
```

Tags
----

The list of tags is cached locally, in `data/mediacloud-tags.json`.  If you want 
to fetch updated tags, just delete this file and the server will recreate it for you with 
fresh data the next time you hit the server in a browser.  Be warned - **this can take a few minutes**.
