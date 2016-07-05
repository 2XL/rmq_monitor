import os
import subprocess
import time
import psutil


class Capture(object):

    def __init__(self):
        print "Constructor: "
        if os.name == "nt":
            self.platform_is_windows = True
        else:
            self.platform_is_windows = False

        self.is_capturing = False
        self.is_client_running = False
        self.proc_name = None
        self.pc_cmd = None

    def _test(self):

        metric_reader = None
        # metric values generator

        operations = 0
        while self.is_client_running:
            # while the client is running
            operations += 1
            self.is_client_running = self.emit(self.sync_proc_pid)
            # this forwards the captured metric to the rabbit server
            time.sleep(1)  # metric each second

        print "QUIT emit metrics"

    def _pc_client(self):

        print "start running [{}] {}".format(self.proc_name, self.pc_cmd)
        try_start = 10
        while self.is_client_running is False:
            self.sync_proc = subprocess.Popen(self.str_cmd, shell=True)
            try_start -= 1
            if try_start == 0:
                print "Unable to start {}".format(self.personal_cloud)
                break
            time.sleep(3)
            try:
                #  pid lookup
                is_running = False
                client_pid = None
                for proc in psutil.process_iter():
                    if proc.name() == self.proc_name:
                        is_running = True
                        client_pid = proc.pid
                        break
                if is_running:
                    self.is_client_running = True
                    self.sync_proc_pid = client_pid
            except Exception as ex:
                print ex.message
                print "Couldn't load sync client"


    def emit(self, process_id=None):
        print "Retrive generic psutil stats by process_id"
        # retrieve stats by process id
        return self.is_client_running  # if client is running

