import unittest
import Logs
import PressureController
import os
import shutil
import datetime
import time


class TestLogs(unittest.TestCase):

    def setUp(self):
        self.startTime = str(datetime.datetime.now())
        self.test_logs = Logs.Log(self.startTime)
        fileNameDate = self.startTime[0:10]
        hour = self.startTime[11:13]
        mins = self.startTime[14:16]
        secs = self.startTime[17:19]
        self.fileNameForm = "Logs/" + fileNameDate + "-" + hour + mins + secs + ".txt"

    def test_send_error(self):
        self.assertEqual(self.test_logs.sendError("Test Error"),
                         'Test Error', "Should return test error")

    def test_send_notice(self):
        self.assertEqual(self.test_logs.sendNotice("Test Notice"),
                         'Test Notice', "Should return test notice")

    def tearDown(self):
        self.test_logs.closeFile()
        os.remove(str(self.fileNameForm))


if __name__ == "__main__":
    unittest.main()
