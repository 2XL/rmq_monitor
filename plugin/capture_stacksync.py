from capture import Capture


class StackSync(Capture):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.whoami = (self).__class__.__name__
        print self.whoami

        if self.platform_is_windows:
            self.pc_cmd = "/Users/vagrant/AppData/Roaming/StackSync_client/Stacksync.jar",
            self.proc_name = "javaw.exe"
        else:
            self.pc_cmd = "/usr/bin/stacksync"
            self.proc_name = "java"




    def hello(self):
        print "{} say hello".format(self.whoami)

    def start(self, src, tgt):
        print "{} say publish".format(self.whoami)

    def stop(self, remote, local):
        print "{} say download".format(self.whoami)


