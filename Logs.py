import datetime
import random

class Log:
    def __init__(self, fileName):
        self.fileName = fileName
        fileNameDate = self.fileName[0:10]
        hour = self.fileName[11:13]
        mins = self.fileName[14:16]

        fileNameForm = "Logs/" + fileNameDate + "-" + hour + mins + ".txt"

        self.f = open(fileNameForm, 'x')
        startString = "Log file started: " + self.fileName
        self.f.write(startString + "\n")

    def sendError(self, error):
        timeNow = datetime.datetime.now()
        self.f.write(str(timeNow)[0:19] + " ERROR:  " + str(error) + "\n")

    def sendNotice(self, notice):
        timeNow = datetime.datetime.now()
        self.f.write(str(timeNow)[0:19] + " NOTICE:  " + str(notice) + "\n")