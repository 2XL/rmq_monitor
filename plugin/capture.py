import os
import subprocess
import time
import psutil
import glob
import shutil
import signal
from threading import Thread

class Capture(object):

    def __init__(self):
        print "Constructor: "
        if os.name == "nt":
            self.platform_is_windows = True
        else:
            self.platform_is_windows = False

        self.is_monitor_capturing = False               # is_monitor_capturing
        self.is_sync_client_running = False             # is_sync_client_running

        self.sync_client = None
        self.monitor = None

        self.proc_name = None
        self.pc_cmd = None

    def _test(self):

        metric_reader = None
        # metric values generator

        operations = 0
        while self.is_sync_client_running:
            # while the client is running
            operations += 1
            self.is_sync_client_running = self.emit(self.sync_proc_pid)
            # this forwards the captured metric to the rabbit server
            time.sleep(1)  # metric each second

        print "QUIT emit metrics"

    def _pc_client(self):

        print "start running [{}] {}".format(self.proc_name, self.pc_cmd)
        try_start = 10
        while self.is_sync_client_running is False:
            self.sync_proc = subprocess.Popen(self.pc_cmd, shell=True)
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
                    self.is_sync_client_running = True
                    self.sync_proc_pid = client_pid
            except Exception as ex:
                print ex.message
                print "Couldn't load sync client"

    def emit(self, process_id=None):
        print "Retrive generic psutil stats by process_id"
        # retrieve stats by process id
        return self.is_sync_client_running  # if client is running

    def start(self, body):
        self.personal_cloud = body['msg']['test']['testClient']
        self.personal_cloud_ip = body['msg']['{}-ip'.format(self.personal_cloud.lower())]
        self.personal_cloud_port = body['msg']['{}-port'.format(self.personal_cloud.lower())]
        self.sync_client = Thread(target=self._pc_client)
        self.sync_client.start()
        self.monitor = Thread(target=self._test)
        self.monitor.start()
        self.is_monitor_capturing = True
        self.is_sync_client_running = True
        print "{} say start".format(self.whoami)
        # self.sync_client = None
        # self.monitor = None

    def stop(self, body):
        print "try stop..."
        self.personal_cloud = body['msg']['test']['testClient']
        self.personal_cloud_ip = body['msg']['{}-ip'.format(self.personal_cloud.lower())]
        self.personal_cloud_port = body['msg']['{}-port'.format(self.personal_cloud.lower())]

        self.remove_inner_path(self.sync_folder_cleanup)
        print "{} say stop".format(self.whoami)
        # self.sync_client = None
        # self.monitor = None
        # how to stop the process in windows ... todo lookup by psutil and clean up
        self.is_monitor_capturing = False
        self.is_sync_client_running = False
        self.monitor.join()
        self.sync_client.join()

        # how to stop process in linux

        if self.platform_is_windows:
            for proc in psutil.process_iter():
                if proc.name() == self.proc_name:
                    proc.kill()  # force quit like a boss
        else:
            pstring = self.proc_name
            for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
                fields = line.split()
                proc_pid = fields[0]
                os.kill(int(proc_pid), signal.SIGKILL)

    @staticmethod
    def remove_inner_path(path):
        files = glob.glob(path)
        try:
            for f in files:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)
        except Exception as ex:
            print ex.message

