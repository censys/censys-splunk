from __future__ import print_function
import json
import logging, logging.handlers
import optparse
import os
import random
import re
import ssl
import sys
import time
import six.moves.urllib.request, six.moves.urllib.error, six.moves.urllib.parse
 
import splunklib.client as client


class EventLog(object):
    """A generic class to talk to the Censys Enterprise Platform logbook API"""

    def __init__(self, key):
        super(EventLog, self).__init__()
        time.sleep(random.randint(0, 45))
        self.key = key
        self.appserver_dir = "{0}/../appserver".format(
            os.path.dirname(os.path.abspath(__file__))
        )
        try:
            self.latest = int(
                open("{0}/static/latest_id".format(self.appserver_dir), "r").read()
            )
        except IOError:
            self.latest = -1
        self.body = {}
        self.logger = logging.getLogger("censys_enterprise")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(
            os.environ["SPLUNK_HOME"] + "/var/log/splunk/censys_enterprise.log",
            maxBytes=25000000,
            backupCount=5,
        )
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.fetch_more = True

    def main(self):
        events = self.get_events()
        self.print_events(events)
        cursor = events["nextWindowCursor"]
        while self.fetch_more:
            events = self.get_events(cursor)
            if len(events.get("results", [])) < 1 or not self.fetch_more:
                break
            else:
                self.print_events(events)
                cursor = events["nextWindowCursor"]
        self.save_latest()

    def get_events(self, cursor=None):
        self.logger.debug("get_events() - {}".format(cursor or self.body))
        baseurl = "https://app.censys.io/api/beta/logbook/getLogbookData"
        req = six.moves.urllib.request.Request(baseurl, cursor or json.dumps(self.body))
        req.add_header("Content-Type", "application/json")
        req.add_header("accept", "application/json")
        req.add_header("Censys-Beta-Api-Key", self.key)
        req.add_header('User-Agent', 'Censys-TA for Splunk 1.0.x')
        try:
            gcontext = ssl._create_unverified_context()
            if cursor:
                data = {"nextWindowCursor": cursor}
            else:
                data = self.body
            resp = six.moves.urllib.request.urlopen(req, json.dumps(data), context=gcontext).read()
            logs = json.loads(resp)
        except six.moves.urllib.error.URLError as e:
            self.logger.warning("Error seen: {0}".format(e))
            self.fetch_more = False
            logs = {"results": [], "nextWindowCursor": "e30="}
        return logs

    def print_events(self, logs):
        def convert(name):
            # camelCase to snake_case
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        silence = False
        for row in logs["results"][::-1]:
            if row["id"] <= self.latest:
                if not silence:
                    self.logger.debug("setting fetch_more to false")
                    silence = True
                self.fetch_more = False
                continue
            # convert to snake_case
            # also - don't emit null values
            # http://www.georgestarcher.com/splunk-null-thinking/
            # 1. Consumes license for the string of the field name in all the events. 
            #    This can be real bad at volume.
            # 2. It throws off all the Splunk auto statistics for field vs event coverage.
            # 3. Makes it hard to do certain search techniques.
            row = dict([(convert(k), v) for k, v in list(row.items()) if v is not None])
            print(json.dumps(row))
            self.latest = max(self.latest, row["id"])

    def save_latest(self):
        with open("{0}/static/latest_id".format(self.appserver_dir), "w") as f:
            f.write(str(self.latest))


if __name__ == "__main__":
    myapp = "censys"
    parser = optparse.OptionParser(usage="%prog [<config file path>]")
    (options, args) = parser.parse_args(sys.argv[1:])

    sessionKey = sys.stdin.readline().strip()

    def get_password(session_key, username):
        args = {"token": session_key}
        service = client.connect(**args)

        # Retrieve the password from the storage/passwords endpoint
        for storage_password in service.storage_passwords:
            if storage_password.username == username:
                return storage_password.content.clear_password

    beta_api_key = get_password(sessionKey, "censys_saas")

    evlog = EventLog(beta_api_key)
    evlog.main()
