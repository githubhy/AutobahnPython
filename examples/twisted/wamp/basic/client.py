###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


if __name__ == '__main__':

   import sys, argparse

   from twisted.python import log
   from twisted.internet.endpoints import clientFromString


   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("-c", "--component", type = str,
                       help = "Start WAMP-WebSocket client with this application component, e.g. 'timeservice.TimeServiceFrontend'")

   parser.add_argument("--websocket", type = str, default = "tcp:127.0.0.1:8080",
                       help = 'WebSocket client Twisted endpoint descriptor, e.g. "tcp:127.0.0.1:8080" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--wsurl", type = str, default = "ws://127.0.0.1:8080/ws",
                       help = 'WebSocket URL (must suit the endpoint), e.g. "ws://127.0.0.1:8080/ws".')

   args = parser.parse_args()


   ## start Twisted logging to stdout
   ##
   if args.debug:
      log.startLogging(sys.stdout)


   ## we use an Autobahn utility to import the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   if args.debug:
      print("Running on reactor {}".format(reactor))


   ## create a WAMP application session factory
   ##
   from autobahn.twisted.wamp import ApplicationSessionFactory
   session_factory = ApplicationSessionFactory()


   ## dynamically load the application component ..
   ##
   import importlib
   c = args.component.split('.')
   mod, klass = '.'.join(c[:-1]), c[-1]
   app = importlib.import_module(mod)

   ## .. and set the session class on the factory
   ##
   session_factory.session = getattr(app, klass)


   ## create a WAMP-over-WebSocket transport client factory
   ##
   from autobahn.twisted.websocket import WampWebSocketClientFactory
   transport_factory = WampWebSocketClientFactory(session_factory, args.wsurl, debug = args.debug)
   transport_factory.setProtocolOptions(failByDrop = False)


   ## start a WebSocket client from an endpoint
   ##
   client = clientFromString(reactor, args.websocket)
   client.connect(transport_factory)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
