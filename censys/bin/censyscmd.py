import base64
import json
import logging
import os
import sys
import urllib2

# https://docs.splunk.com/Documentation/Splunk/7.3.1/Search/Writeasearchcommand
# https://blog.angelalonso.es/2016/03/hunting-exploit-kits-in-enterprise.html
import splunk.Intersplunk
import splunk.entity as entity

PORTS = ("protocols", )

BANNERS = ('110.pop3.starttls.banner',
           '143.imap.starttls.banner',
           '16992.http.get.headers.server',
           '21.ftp.banner.banner',
           '22.ssh.v2.banner.raw',
           '23.telnet.banner.banner',
           '2323.telnet.banner.banner',
           '25.smtp.starttls.banner',
           '3306.mysql.banner.server_version',
           '443.https.get.headers.server',
           '445.smb.banner.smb_version.version_string',
           '465.smtp.tls.banner',
           '5432.postgres.banner.supported_versions',
           '587.smtp.starttls.banner',
           '6443.kubernetes.banner.metadata.description',
           '7547.cwmp.get.headers.server',
           '80.http.get.headers.server',
           '8888.http.get.headers.server',
           '993.imaps.tls.banner',
           '995.pop3s.tls.banner'
           )

DESCRIPTION = ("metadata.description", )

TITLES = ('443.https.get.title',
          '80.http.get.title',
          '8080.http.get.title',
          '8888.http.get.title')

TLS_NAMES = ('110.pop3.starttls.tls.certificate.parsed.names',
             '143.imap.starttls.tls.certificate.parsed.names',
             '1433.mssql.banner.tls.certificate.parsed.names',
             '25.smtp.starttls.tls.certificate.parsed.names',
             '443.https.tls.certificate.parsed.names',
             '587.smtp.starttls.tls.certificate.parsed.names',
             '993.imaps.tls.tls.certificate.parsed.names',
             '995.pop3s.tls.tls.certificate.parsed.names')

FIELDS = {'ports': PORTS,
          'banners': BANNERS,
          'description': DESCRIPTION,
          'titles': TITLES,
          'tls_names': TLS_NAMES}

logger = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/censys_enterprise.log', maxBytes=25000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
myapp='censys'
config = {'api_id': '', 'api_secret': ''}

events, _, settings = splunk.Intersplunk.getOrganizedResults()
sessionKey = str(settings.get('sessionKey'))

if len(sessionKey) == 0:
   sys.stderr.write("Did not receive a session key from splunkd. " +
                    "Please enable passAuth in commands.conf for this " +
                    "script\n")
   exit(2)
try:
    entities = entity.getEntities(['admin', 'passwords'], namespace=myapp,
                                  owner='nobody', sessionKey=sessionKey)
except Exception, e:
    logger.fatal("getEntities: Could not get {0} credentials from splunk. Error: {1}".format(myapp, e))
    splunk.Intersplunk.outputResults([
        splunk.Intersplunk.generateErrorResults(
        "getEntities: Could not get {0} credentials from splunk. Error: {1}".format(myapp, e))])
    sys.exit(1)

try:
    for k,entity in entities.items():
        if entity.get('realm', False):
           config['api_id'] = entity['username']
           config['api_secret'] = entity['clear_password']
except Exception, e:
    logger.fatal("entities.items(): Could not get {0} credentials from splunk. Error: {1}".format(myapp, e))
    splunk.Intersplunk.outputResults([        
        splunk.Intersplunk.generateErrorResults(
        "entities.items(): Could not get {0} credentials from splunk. Error: {1}".format(myapp, e))])
    sys.exit(1)

auth64 = base64.b64encode('{0}:{1}'.format(config['api_id'], config['api_secret']))

keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

try:
    field = sys.argv[1]
    output = sys.argv[2]
except IndexError:
    splunk.Intersplunk.outputResults([splunk.Intersplunk.generateErrorResults('Usage: censys inputfield {0}'.format(', '.join(FIELDS.keys())))])
    sys.exit(0)

if not FIELDS.has_key(output):
    splunk.Intersplunk.outputResults([splunk.Intersplunk.generateErrorResults('Invalid output field, valid options are: {0}'.format(', '.join(FIELDS.keys())))])
    sys.exit(0)

try:
    cache = {}
    for event in events:
        try:
            ip = event[field]
        except KeyError:
            continue

        try:
            resp = cache[ip]
        except KeyError:
            data = {"query": "ip:{0}".format(ip),
                    "page": 1,
                    "flatten": True,
                    "fields": FIELDS.get(output)}
            request = urllib2.Request('https://censys.io/api/v1/search/ipv4', json.dumps(data))
            request.add_header("Authorization", "Basic %s" % auth64)
            req = urllib2.urlopen(request)
            resp = json.loads(req.read())
            req.close()
            cache[ip] = resp
        for r in resp.get('results', []):
            for k,v in r.items():
                event[k] = v
except:
    import traceback
    stack =  traceback.format_exc()
    events = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

splunk.Intersplunk.outputResults(events)