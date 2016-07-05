from capture import Capture


class Dropbox(Capture):

    def __init__(self):

        super(self.__class__, self).__init__()
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files (x86)/Dropbox/Client/Dropbox.exe",
            self.proc_name = "Dropbox.exe"
            self.sync_folder = "/Users/vagrant/Dropbox"
        else:
            self.pc_cmd = "sudo -H -u vagrant bash -c '/usr/local/bin/dropbox start'"
            self.proc_name = "dropbox"
            self.sync_folder = "Dropbox"


    def hello(self):
        print "{} say hello".format(self.whoami)

    def start(self):
        print "{} say start".format(self.whoami)

    def stop(self):
        print "{} say stop".format(self.whoami)