import cherrypy
import os
import json
import pymongo
import datetime

class CardDatabase(object):
    def __init__(self, database):
        self._db = database
        self._cards = self._db.cards
    def read(self, cardnumber):
        result = []
        for entry in self._cards.find({"cardnumber":cardnumber}, sort=[("datetime",pymongo. DESCENDING)]):
            result.append(entry['value'])
        return result
    def store(self, cardnumber, meta, value):
        self._cards.insert({
          'cardnumber': cardnumber,
          'datetime': datetime.datetime.utcnow(),
          'meta': meta,
          'value': value
        })
    def listall(self):
        return self._cards.find()

class CardsService(object):
    def __init__(self, database):
        self._database = database

    def store(self, cardnumber="", value=""):
        jsonvalue = json.loads(value)
        meta = {
          "ipaddress": cherrypy.request.headers["Remote-Addr"]
        }
        self._database.store(cardnumber, meta, jsonvalue)
        cherrypy.response.headers['Content-Type']= 'text/plain'
        return "OK"
    store.exposed = True

    def read(self, cardnumber):
        entries = self._database.read(cardnumber)
        if not entries:
            cherrypy.response.status = 404
            cherrypy.response.headers['Content-Type']= 'text/plain'
            return cardnumber + " not found" 
        else:
            cherrypy.response.headers['Content-Type']= 'application/json'
            return json.dumps(entries)
    read.exposed = True

    def listall(self):
        for card in self._database.listall():
            yield str(card)
    listall.exposed = True

def mongo_database():
    mongohq_url = os.environ.get('MONGOHQ_URL')
    if mongohq_url:
        database_name = mongohq_url[mongohq_url.rfind("/")+1:]
        connection = pymongo.Connection(mongohq_url)
        return connection[database_name]
    else:
        return pymongo.Connection().swisher

