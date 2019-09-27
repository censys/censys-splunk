from base64 import decodestring
import ConfigParser
import json
import logging
import optparse
import os
import ssl
import sys
import time
import logging
import urllib2

import splunk.entity as entity

class EventLog(object):
    """A generic class to talk to the Censys Enterprise Platform logbook API"""
    def __init__(self, key):
        super(EventLog, self).__init__()
        self.key = key
        self.appserver_dir = '{0}/../appserver'.format(os.path.dirname(os.path.abspath(__file__)))
        try:
            self.latest = int(open('{0}/static/latest_id'.format(self.appserver_dir), 'r').read())
        except IOError:
            self.latest = -1
        self.includedLogTypes = ('CERT',
                                'HOST',
                                'HOST_CERT',
                                'HOST_CVE',
                                'HOST_PORT',
                                'HOST_SERVICE',
                                'HOST_SOFTWARE',
                                'DOMAIN',
                                'DOMAIN_EXPIRATION_DATE',
                                'DOMAIN_MAIL_EXCHANGE_SERVER',
                                'DOMAIN_NAME_SERVER',
                                'DOMAIN_REGISTRAR')
        self.body = {'data': {'general': {'includedLogTypes': self.includedLogTypes }}}
        self.logger = logging.getLogger('censys_enterprise')
        self.logger.setLevel(logging.DEBUG)
        # handler = logging.StreamHandler()
        file_handler = logging.handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/censys_enterprise.log', maxBytes=25000000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.fetch_more = True

    def main(self):
        events = self.get_events()
        events.update(json.loads(decodestring(events['nextWindowCursor'])))
        self.print_events(events)
        cursor = events['nextWindowCursor']
        while self.fetch_more:
            events = self.get_events(cursor)
            if len(events.get('results', [])) < 1 or not self.fetch_more:
                break
            else:
                self.print_events(events)
                cursor = events['nextWindowCursor']
        self.save_latest()

    def get_events(self, cursor=None):
        self.logger.debug("get_events() - {}".format(cursor or self.body))
        baseurl = 'https://app.censys.io/n/api/protected/beta/getLogbookData?betaApiKey={0}'
        req = urllib2.Request(baseurl.format(self.key))
        req.add_header('Content-Type', 'application/json')
        try:
            gcontext = ssl._create_unverified_context()
            if cursor:
                data = {"data": cursor}
            else:
                data = self.body
            resp = urllib2.urlopen(req, json.dumps(data), context=gcontext)
            logs = json.loads(resp.read())
        except urllib2.URLError, e:
            self.logger.warning('Error seen: {0}'.format(e))
            logs = {'rows': []}
        return logs

    def print_events(self, logs):
        silence = False
        for row in logs['results'][::-1]:
            row['timestamp'] = time.ctime(row.pop('logTime')/1000)
            if row['id'] <= self.latest:
                if not silence:
                    self.logger.debug("setting fetch_more to false")
                    silence = True
                self.fetch_more = False
                continue
            # don't emit null values
            # http://www.georgestarcher.com/splunk-null-thinking/
            # 1. Consumes license for the string of the field name in all the events. This can be real bad at volume.
            # 2. It throws off all the Splunk auto statistics for field vs event coverage.
            # 3. Makes it hard to do certain search techniques.
            row = {k: v for k, v in row.items() if v is not None}
            print(json.dumps(row))
            self.latest = max(self.latest, row['id'])

    def save_latest(self):
        with open('{0}/static/latest_id'.format(self.appserver_dir), 'w') as f:
            f.write(str(self.latest))

if __name__ == '__main__':
    myapp = 'censys_enterprise_logs'
    parser = optparse.OptionParser(usage="%prog [<config file path>]")
    (options, args) = parser.parse_args(sys.argv[1:])

    cp = ConfigParser.ConfigParser()
    if len(sys.argv) == 1:
        config_path = os.path.abspath(__file__)
        config_path = os.path.dirname(config_path)
        config_path = os.path.join(config_path, "splunk_conf/censys.conf")
    else:
        config_path = sys.argv[1]
    cp.read(config_path)
    config = dict(cp.items('censys'))
    beta_api_key = config['beta_api_key']

    """
    sessionKey = sys.stdin.readline().strip()

    if len(sessionKey) == 0:
       sys.stderr.write("Did not receive a session key from splunkd. " +
                        "Please enable passAuth in inputs.conf for this " +
                        "script\n")
       exit(2)
    try:
        entities = entity.getEntities(['admin', 'passwords'], namespace=myapp,
                                      owner='nobody', sessionKey=sessionKey)
    except Exception, e:
        raise Exception("Could not get %s credentials from splunk. Error: %s"
                        % (myapp, str(e)))
    try:
        beta_api_key = entities.items()[0]['beta_api_key']
    except IndexError:
        raise Exception('Not enough items')
    except KeyError:
        raise Exception('No beta_api_key found')
    """
    evlog = EventLog(beta_api_key)
    evlog.main()