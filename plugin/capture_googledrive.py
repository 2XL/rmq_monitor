from capture import Capture


class GoogleDrive(Capture):

    def __init__(self):

        super(self.__class__, self).__init__()
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files (x86)/Google/Drive/googledrivesync.exe",
            self.proc_name = "googledrivesync.exe"
        else:
            self.pc_cmd = ""
            self.proc_name = ""


    def hello(self):
        print "{} say hello".format(self.whoami)

    def start(self, src, tgt):
        print "{} say publish".format(self.whoami)

    def stop(self, remote, local):
        print "{} say download".format(self.whoami)