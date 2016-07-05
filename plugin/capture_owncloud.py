from capture import Capture


class OwnCloud(Capture):

    def __init__(self):

        super(self.__class__, self).__init__()
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files (x86)/ownCloud/owncloud.exe",
            self.proc_name = "owncloud.exe"
            self.sync_folder = ""
        else:
            self.pc_cmd = "/vagrant/owncloudsync.sh"
            self.proc_name = "owncloudsync"
            self.sync_folder = "owncloud_folder"




    def hello(self):
        print "{} say hello".format(self.whoami)

    def start(self, src, tgt):
        print "{} say publish".format(self.whoami)

    def stop(self, remote, local):
        print "{} say download".format(self.whoami)