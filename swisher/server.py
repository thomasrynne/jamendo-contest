
import notifier
import web
import cardreader
import cardmanager
import cards
import mpdsource
import mpdplayer
import actions
import shell
import cherrypy
import logging
import radiosource
import printer
import jamendo

class Server:
    def __init__(self, resources_path, cardsfile, log, grab_device, mpdhost, mpdport, http_port, jamendo_username):
        self.notifier = notifier.Notifier()
        self.card_store = cards.CardStore(cardsfile, True)
        self.actions = actions.Actions()
        self.card_manager = cardmanager.CardManager(self.card_store, self.actions, self.notifier.notify)
        self.card_reader = cardreader.CardReader(
            grab_device,
            self.card_manager.on_card,
            self.card_manager.update_devices_count
        )
        self.mpdplayer = mpdplayer.MpdPlayer(mpdhost, mpdport, self.actions, self.notifier.notify)
        self.mpdsource = mpdsource.MpdSource(self.actions, self.mpdplayer.client)
        radios = radiosource.RadioSource(self.actions, self.mpdplayer)
        self.jamendo = jamendo.Jamendo(self.mpdplayer, self.actions, jamendo_username)
        self.shell = shell.Shell(self.actions)

        pages = [
            ("Cards", lambda c: web.CardsPage(c, self.card_store, self.actions)),
            ("Mpd", lambda c: mpdsource.SearchPage(c, self.mpdsource)),
            ("Radio", lambda c: radiosource.RadioPage(c, radios)),
            ("Actions", lambda c: actions.ActionsPage(c, self.actions)),
            ("CardPrinter", lambda c: printer.CardPrinterPage(c))
        ]
        if jamendo_username:
            pages = pages + [
                ("Jamendo Search", lambda c: jamendo.SearchPage(c, self.jamendo)),
                ("Jamendo Radio", lambda c: jamendo.RadioPage(c, self.jamendo)),
                ("Jamendo Likes", lambda c: jamendo.LikesPage(c, self.jamendo)),
            ]
        self.web = web.Web(resources_path, log, http_port,
          self.actions, self.card_store, self.card_manager, self.notifier, pages)
    def start(self):
        self.mpdplayer.start()
        self.card_reader.start()
        self.web.start()
    def stop(self):
        cherrypy.log("Stopping swisher", severity=logging.INFO)
        self.notifier.stop()
        self.web.stop()
        self.card_reader.stop()
        self.mpdplayer.stop()

