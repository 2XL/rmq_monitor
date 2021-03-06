from capture import Capture


class Box(Capture):

    def __init__(self, hostname):

        super(self.__class__, self).__init__(hostname)
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "",
            self.proc_name = ""
            self.sync_folder = ""
            self.sync_folder_cleanup = ""
        else:
            self.pc_cmd = ""
            self.proc_name = ""
            self.sync_folder = ""
            self.sync_folder_cleanup = ""

    def hello(self):
        print "{} say hello".format(self.whoami)

    # def start(self):
    #     print "{} say start".format(self.whoami)
    #     # self.sync_client = None
    #     # self.monitor = None
    #
    # def stop(self):
    #     print "{} say stop".format(self.whoami)
    #     # self.sync_client = None
    #     # self.monitor = None
