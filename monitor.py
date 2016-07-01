import traceback
from plugin.capture_box import Box as box
from plugin.capture_dropbox import Dropbox as dropbox
from plugin.capture_googledrive import GoogleDrive as googledrive
from plugin.capture_owncloud import OwnCloud as ownloud
from plugin.capture_stacksync import StackSync as stacksync


class Monitor(object):

    def __init__(self, personal_cloud):
        print "constructor"

        self.action = None
        if personal_cloud is None:
            raise NotImplemented
        else:
            self.action = eval("{}".format(personal_cloud))()

    def hello(self):
        #try:
        self.action.hello()
        return 0
        #    return 0  # successfully logged to personal cloud service
        # except Exception as ex:
        #     print ex.message
        #     print traceback.print_tb(None)
        #     return 1
