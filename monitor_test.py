#!/usr/bin/python
import unittest
import os
from monitor import Monitor
from hashlib import md5
import sys

# execute single test
# nosetests publisher_test.py -- single test
# nosetests /path/to/folder -- suit of test


class MonitorTest(unittest.TestCase):

    personal_cloud = "dropbox"
    # la plataforma se comprueba por script no por parametro

    def test_hello(self):
        monitor = Monitor(self.personal_cloud)
        result = monitor.hello()  # hello es un hello world
        self.assertEqual(result, 0)

    def test_start_personal_cloud(self):
        # initialize the personal_cloud client and check if the process exists
        monitor = Monitor(self.personal_cloud)
        monitor.start()


    def test_stop_personal_cloud(self):

        monitor = Monitor(self.personal_cloud)
        monitor.stop()


