"""
Copyright (c) 2016-2018 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import sleekxmpp

class XmppClient(sleekxmpp.ClientXMPP):

    def __init__(self, bot_client, jid, password):
        self._bot_client = bot_client
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handlers()

    def add_event_handlers(self):
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def is_valid_message(self, msg):
        if 'type' in msg:
            return bool(msg['type'] in ('chat', 'normal'))
        return False

    def get_question(self, msg):
        if 'body' in msg:
            return msg['body']
        return None

    def get_userid(self, msg):
        if 'from' in msg:
            return msg['from']
        return None

    def send_response(self, msg, response):
        if response is not None:
            msg.reply(response).send()

    def message(self, msg):
        if self.is_valid_message(msg) is True:

            question = self.get_question(msg)
            if question is None:
                if logging.getLogger().isEnabledFor(logging.ERROR):
                    logging.debug("Missing 'question' from XMPP message")
                return

            userid = self.get_userid(msg)
            if userid is None:
                if logging.getLogger().isEnabledFor(logging.ERROR):
                    logging.debug("Missing 'userid' from XMPP message")
                return

            response = self._bot_client.ask_question(userid, question)

            self.send_response(msg, response)

        else:
            if logging.getLogger().isEnabledFor(logging.ERROR):
                logging.debug("Invalid XMPP message")
            self.send_response(msg, "Sorry, no idea!")

    def register_xep_plugins(self, configuration):
        if configuration.xep_0030 is True:
            self.register_plugin('xep_0030')

        if configuration.xep_0004 is True:
            self.register_plugin('xep_0004')

        if configuration.xep_0060 is True:
            self.register_plugin('xep_0060')

        if configuration.xep_0199 is True:
            self.register_plugin('xep_0199')