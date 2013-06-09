import os
import signal
import jamendo
import cardservice
import web
import cherrypy

class JamendoActionsPage: #hard coded with the actions supported by the web player
  def __init__(self, context):
    self.context = context
    self._actions = [
      ["mpd.stop", "Stop"], ["mpd.pause", "Pause"],
      ["mpd.next", "Next"], ["mpd.previous", "Previous"]
    ]
  @cherrypy.expose
  def index(self):
    return self.context.render("actions.html","Actions", actions=self._actions)
  
def start():
  current_dir = os.path.dirname(os.path.abspath(__file__))
  port = int(os.environ.get('PORT', '5000'))
  clientid = os.environ.get('JAMENDO_CLIENTID', 'UNDEFINED')

  rootdir = os.path.dirname(os.path.abspath(__file__))
  database = cardservice.CardDatabase(cardservice.mongo_database())
  cs = cardservice.CardsService(database)
  jamapi = jamendo.JamendoApi(clientid)
  pages = [
    ("Jamendo Search", lambda c: jamendo.SearchPage(c, jamapi)),
    ("Jamendo Radio", lambda c: jamendo.RadioPage(c, jamapi)),
    ("Jamendo Likes", lambda c: jamendo.LikesPage(c, jamapi, "")),
    ("Actions", lambda c: JamendoActionsPage(c)),
  ]
  w = web.Web(current_dir, False, port, ["soundmanager2-nodebug-jsmin.js", "web-functions.js"], pages)
  w.root.cardservice = cs

  def signal_handler(signal, frame):
    w.stop()	
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  w.run()

#better updates to 'Ready' for reader status
#heroku deployment
#write home page
#improve usage text


