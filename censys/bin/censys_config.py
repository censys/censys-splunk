import splunk.admin as admin
import splunk.entity as en

STRING_ARGS = ('api_id', 'api_secret', 'beta_api_key')
ALL_ARGS = STRING_ARGS

class ConfigApp(admin.MConfigHandler):
    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ALL_ARGS:
                self.supportedArgs.addOptArg(arg)
  
    def handleList(self, confInfo):
        confDict = self.readConf("appsetup")
        if None != confDict:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if key in STRING_ARGS and val in (None, ''):
                        val = ''
                    confInfo[stanza].append(key, val)
  
  
    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs
        self.writeConf('appsetup', 'setupentity', self.callerArgs.data)

admin.init(ConfigApp, admin.CONTEXT_NONE)
    