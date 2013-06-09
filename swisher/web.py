
import cherrypy
import json
from mako.template import Template
from mako.lookup import TemplateLookup
from cherrypy.lib.static import serve_file
import os.path
import thread
import time
import Queue
import json

class RootPage:
  def __init__(self, dir, context):
      self.dir = dir
      self._context = context

  @cherrypy.expose
  def index(self):
      return self._context.render("index.html","Home")

  def add_page(self, name, page):
      setattr(self, name, page)

  @cherrypy.expose
  def assets(self, name):
      return serve_file(os.path.abspath(self.dir + "/assets/" + name))

class CardsPage:
  def __init__(self, context, card_store):
    self.context = context
    self.card_store = card_store
  @cherrypy.expose
  def index(self):
    return self.context.render("cards.html", "Cards",
        cards=self.cards_with_name())
  def cards_with_name(self):
    for number, action in self.card_store.cards():
      name = "Unknown"
      yield (number, action[0], action[1], name)

class ActionPage:
  def __init__(self, actions, card_manager):
    self._actions = actions
    self._card_manager = card_manager
  @cherrypy.expose
  def invoke(self, prefix=None, value=None):
    self._actions.invoke(prefix, value)
  @cherrypy.expose
  def record(self, prefix=None, value=None, name=None):
    self._card_manager.record(prefix, value, name)
  @cherrypy.expose
  def cancelrecord(self):
    self._card_manager.cancel_record()

class LongPollStatus:
    def __init__(self, notifier):
        self.notifier = notifier

    @cherrypy.expose
    def status(self, **current):
        changed_status = self.notifier.next_status(current)
        return json.dumps(changed_status)

class WebContext:
    def __init__(self, template, scripts):
        self._template = template
        self._scripts = scripts
        self._pages = [ "Home" ]
    def render(self, template_name, title, **others):
        t = self.get_template(template_name)
        return t.render(title=title, tabs=self.tabs(), scripts=self._scripts, **others)
    def get_template(self, name):
        return self._template.get_template(name)
    def add_page(self, name):
        self._pages.append(name)
    def tabs(self):
        return self._pages

class Web:
  def __init__(self, dir, logfile, port, scripts, pages):
    self.dir= dir
    self.logfile = logfile
    self.port = port
    self.context = WebContext(TemplateLookup(directories=[dir+'/templates']), scripts)
    self.root = RootPage(dir, self.context)
    for name, page in pages:
        self.context.add_page(name)
        self.root.add_page(name.replace(" ", ""), page(self.context))

  def start(self):
    thread.start_new_thread(self.run, ())
  def run(self):
    cherrypy.quickstart(self.root, config={
        'global': {
          'environment': 'production',
          'log.screen': not self.logfile,
          'log.access_file': False,
          'log.error_file': self.logfile,
          'server.socket_host': "0.0.0.0",
          'server.socket_port': self.port,
          'server.thread_pool': 10
        }
    })
  def stop(self):
    cherrypy.engine.exit()
