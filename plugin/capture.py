import os
import subprocess
import time
import psutil
import glob
import shutil
import signal
import urlparse
import pika
import calendar
import math
import json
from threading import Thread


class Capture(object):

    def __init__(self, hostname):

        print "Constructor: "
        self.hostname = hostname

        if os.name == "nt":
            self.platform_is_windows = True
            self.rmq_path = '/Users/vagrant/vagrant/rabbitmq'
        else:
            self.platform_is_windows = False
            self.rmq_path = "rabbitmq"

        self.rmq_path_url = None

        with open(self.rmq_path, 'r') as read_file:
            self.rmq_path_url = read_file.read().splitlines()[0]

        self.metric_prev = None
        self.traffic_monitor = None
        self.metric_network_counter = None
        self.metric_network_netiface = None
        iface_candidate = ['enp4s0f2', 'eth0']
        for iface in iface_candidate:
            if iface in psutil.net_io_counters(pernic=True):
                self.metric_network_counter = psutil.net_io_counters(pernic=True)[iface]
                self.metric_network_netiface = iface
                break
            else:
                continue

        # if none has been selected then, none network iface metric will be reported
        self.rmq_url = urlparse.urlparse(self.rmq_path_url)

        self.rmq_connection = None

        try:
            self.rmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rmq_url.hostname,
                    heartbeat_interval=5,
                    virtual_host=self.rmq_url.path[1:],
                    credentials=pika.PlainCredentials(self.rmq_url.username, self.rmq_url.password)
                )
            )
        except Exception as ex:
            print ex.message
            exit(0)
            # failed to create rabbit connection
        self.rmq_channel = self.rmq_connection.channel()
        self.rmq_channel.exchange_declare(exchange='metrics', type='fanout')

        self.is_monitor_capturing = False               # is_monitor_capturing
        self.is_sync_client_running = False             # is_sync_client_running

        self.sync_client = None
        self.sync_client_proc = None
        self.sync_client_proc_pid = None

        self.stereotype_recipe = None

        self.monitor = None

        self.proc_name = None
        self.pc_cmd = None


    '''
    Retrieve the psutil metrics
    '''
    def notify_status(self):
        print "curr state metrics"
        # retrieve the current state metrics from the personal client capturer
        # current metrics is a local variable
        metrics = {'cpu': 0,
                   'ram': 1,
                   'net': 2,
                   'bytes_sent': 1,
                   'bytes_recv': 1,
                   'packets_sent': 1,
                   'packets_recv': 1,
                   'errin': 0,
                   'errout': 0,
                   'dropin': 0,
                   'dropout': 0,
                   'disk': 0,
                   'files': 0,
                   'time': calendar.timegm(time.gmtime()) * 1000}

        try:
            if self.is_sync_client_running:  # the sync client is running
                self.sync_client_proc = psutil.Process(self.sync_client_proc_pid)
        except Exception as ex:
            print ex.message    # no sync client running
            return False
        # assign ram and cpu usage
        if self.sync_client_proc is not None:
            # we got a process and gota collect metrics
            cpu_usage = int(math.ceil(self.sync_client_proc.cpu_percent(0)))
            ram_usage = self.sync_client_proc.memory_info().rss
            metrics['cpu'] = cpu_usage
            metrics['ram'] = ram_usage

        # assign the network usage
        if self.metric_prev is not None:
            last_time = self.metric_prev['metric']['time']
            curr_net_counter = psutil.net_io_counters(pernic=True)[self.metric_network_netiface]
            curr_time = metrics['time']
            elapsed_time = (curr_time - last_time) / 1000  # seconds
            for key, value in curr_net_counter.__dict__.items():
                metrics[key] = (value - getattr(self.prev_net_counter, key)) / elapsed_time  # unit is seconds
            self.prev_net_counter = curr_net_counter

        # assign hard disk usage
        if self.platform_is_windows:
            drive_usage = "1234"
        else:
            drive_usage_cmd = ['/usr/bin/du', '-ks', '/home/vagrant/{}'.format(self.sync_folder)]
            drive_usage_output = subprocess.Popen(drive_usage_cmd, stdout=subprocess.PIPE)
            drive_usage = drive_usage_output.stdout.read()
        try:
            metrics['disk'] = int(drive_usage.split('\t')[0])  # kilo bytes cast string to int
        except Exception as ex:
            print "invalid literal for... memory unit"
            metrics['disk'] = 1

        # assign file counter
        if self.platform_is_windows:
            num_files = "123"
        else:
            find_cmd = '/usr/bin/find /home/vagrant/{} -type f'.format(self.sync_folder).split()
            proc_find = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
            wc_cmd = '/usr/bin/wc -l'.split()
            proc_wc = subprocess.Popen(wc_cmd, stdin=proc_find.stdout, stdout=subprocess.PIPE)
            num_files = proc_wc.communicate()[0]
        try:
            metrics['files'] = int(num_files.split('\t')[0])
        except Exception as ex:
            print ex.message
            print "invalid literal for... file counter"

        try:
            net_stats = self.traffic_monitor.notify_status()

            # py_sniffer not unlocalizable
            metrics['data_rate_size_up'] = net_stats['data_rate']['size_up']
            metrics['data_rate_size_down'] = net_stats['data_rate']['size_down']
            metrics['data_rate_pack_up'] = net_stats['data_rate']['pack_up']
            metrics['data_rate_pack_down'] = net_stats['data_rate']['pack_down']
            metrics['meta_rate_size_up'] = net_stats['meta_rate']['size_up']
            metrics['meta_rate_size_down'] = net_stats['meta_rate']['size_down']
            metrics['meta_rate_pack_up'] = net_stats['meta_rate']['pack_up']
            metrics['meta_rate_pack_down'] = net_stats['meta_rate']['pack_down']
        except Exception as ex:
            print ex.message

        tags = ''
        if tags == '':
            tags = {
                'profile': self.stereotype_recipe,
                'credentials': 'pc_credentials',
                'client': self.whoami,
            }

        data = {
            'metrics': metrics,
            'tags': tags
        }
        self.metric_prev = data  # update the last emited metric
        msg = json.dumps(data)
        print msg

        self.rmq_channel.basic_publish(
            exchange='metrics',
            routing_key=self.hostname,
            body=msg)

        return True
        # asssign data and metadata from pysniffer
        # net_stats = self.traffic_monitor.notify_stats()

    def _test(self):

        metric_reader = None
        # metric values generator

        operations = 0
        while self.is_sync_client_running:
            # while the client is running
            operations += 1
            self.is_sync_client_running = self.emit(self.sync_client_proc_pid)
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
                    self.sync_client_proc_pid = client_pid
            except Exception as ex:
                print ex.message
                print "Couldn't load sync client"

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

