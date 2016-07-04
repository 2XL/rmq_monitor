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

    personal_cloud = "googledrive"
    # la plataforma se comprueba por script no por parametro

    def test_hello(self):
        monitor = Monitor(self.personal_cloud)
        result = monitor.hello()
        self.assertEqual(result, 0)



    def test_start(self):
        # initialize the personal_cloud client and check if the process exists
        monitor.start()