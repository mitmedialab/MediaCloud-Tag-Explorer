MediaCloud Tag Explorer
=======================

Small server to let users explore tags in the MediaCloud system.  Originally 
created as an example of how to use the [MediaCloud API client](https://github.com/c4fcm/MediaCloud-API-Client/) in a web app.

Installation
------------

Make sure you havy Python 2.7 (and the pip package manager).

First [download the latest egg of the python api client module](https://github.com/c4fcm/MediaCloud-API-Client/tree/master/dist) and install it like this:

```
easy_install [the egg file]
```

Then install the dependencies:

```
pip install flask
pip install requests
```

Then Copy the `mc-client.config.template` to `mc-client.config` and edit it, putting in the 
API username and password, and database connection settings too.

Use
---

Run this command and then visit `localhost:5000` with a web browser

```
python server.py
```
