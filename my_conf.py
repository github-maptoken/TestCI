#!/usr/bin/env python3

import os
import sys
import time
import datetime
import locale
import subprocess
import configparser
import unittest
import logging


##logging.basicConfig(level=logging.DEBUG, filename=logFile)
logger = logging.getLogger(__name__)


# Derived class Configparser so that "stdout=termPrint" and
#   "stderr=sysPrint" are configurable. Also, specialty methods.
class MyConf(configparser.ConfigParser):
    def __init__(self, termPrint, sysPrint, confFile=None, parent=None):
        super().__init__(parent)
        self.writeChat = termPrint
        self.writeCon = sysPrint
        if confFile:
            try:
                self.read(confFile)
            except Exception as eeh:
                logger.warning(f"Class of exception is : {type(eeh).__name__}")
                logger.warning(f"failed opening {confFile} for reading: {eeh}")
                logger.debug("Continuing on")
                self.writeCon("Error Initializing config. Moving on")

    def printConfig(self) -> None:
        if len(self.sections()) < 1:
            logger.warning("No config file read yet")
            self.writeChat("Config is empty")
            return
        self.writeChat("Print config")
        for sectNow in self.sections():
            self.writeChat(f"[{sectNow}]")
            for keyNow in self[sectNow]:
                self.writeChat(f" {keyNow} = {sectNow}[{keyNow}]")

    def mergeConfig(self, confFile) -> None:
        try:
            self.read(confFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed opening {confFile} for reading: {eeh}")
            logger.debug("Continuing on")
            self.writeCon("Error merging config {confFile}. Moving on")

    def readConfig(self, confFile) -> None:
        if len(self.sections()) > 0:
            logger.warning("Re-reading config file")
            self.clear()    ## NOTE: special section DEFAULTSECT not removed
        try:
            self.read(confFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed opening {confFile} for reading: {eeh}")
            logger.debug("Continuing on")
            self.writeCon("Error reading config {confFile}. Moving on")

    def setSectionValue(self, useSection, useKey, useValue) -> None:
        if useSection not in self.sections():
            self[useSection] = {}
        self[useSection][useKey] = useValue

    def getSectionValue(self, useSection, useKey, useDefault) -> str:
        if useSection not in self.sections():
            return useDefault
        if self[useSection][useKey]:
            return self[useSection][useKey]
        else:
            return useDefault

    def delSectionValue(self, useSection, useKey) -> None:
        try:
            self.remove_option(useSection,useKey)
        except configparser.NoSectionError:
            logger.warning(f"Removing key {useKey} from none existant section {useSection}")
            return
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed deleting key {useKey} in config section {useSection} : {eeh}")
            self.writeCon("Error deleting key {useKey} in section {useSection}. Moving on")

    def delSection(self, useSection) -> None:
        try:
            self.remove_section(useSection)
        except configparser.NoSectionError:
            logger.warning(f"Removing non-existant section {useSection} from config")
            return
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed deleting key {useKey} in config section {useSection} : {eeh}")
            self.writeCon("Error deleting no-existant section {useSection}. Moving on")

    def get_config_section(self, useSection) -> dict:
        # Assuming a section called 'Settings' exists in the config file
        if useSection in self.sections():
            return dict(self[useSection])
        return {}

    def printSection(self, useSection) -> None:
        if useSection not in self.sections():
            logger.warning("No section {useSection} in config")
            return
        self.writeChat(f"Print section {useSection}")
        if useSection in self.sections():
            for keyNow in self[useSection]:
                self.writeChat(f" {keyNow} = {self[useSection][keyNow]}")

    def saveConfig(self, useFile) -> bool:
        try:
            with open(useFile, 'w') as config_file:
                self.write(config_file)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed opening {useFile} for writing: {eeh}")
            logger.debug("Continuing on")
            self.writeConf(f"Failed writing config to {useFile}")
            return False
        return True


class test_MyConf(unittest.TestCase):
    ## class variable
    ##defaultTestFile = "generated.conf"
    dateOnly = datetime.date.today()
    timeOnly = time.strftime("%H_%M_%S")
    defaultTestFile = "testconf.conf" + str(dateOnly) + "-" + timeOnly + ".log"

    @classmethod
    def setUpClass(cls) -> None:
        print('\n=== setUp Unit Tests ===')
        ##sys.stdout.flush()
        locale.setlocale(locale.LC_ALL, '')

    @classmethod
    def tearDownClass(cls) -> None:
        print('\n=== tearDown Unit Tests ===')
        ##sys.stdout.flush()

    @classmethod
    def genTestConfig(cls, testFile=None) -> bool:
        if testFile:
            saveAsFile = testFile
        else:
            saveAsFile = cls.defaultTestFile
        confDat = configparser.ConfigParser()
        confDat['MAIN'] = {'coreTopic': 'HouseIoT',
                           'devName': 'myDev'
                           }
        confDat['SERVER_TOPICS'] = {}
        confDat['DEVICE_TOPICS'] = {}
        serverStuff = confDat['SERVER_TOPICS']
        serverStuff['Receiver'] = '/rcvsrv'
        serverStuff['Quit'] = '/quitsrv'
        myStuff = confDat['DEVICE_TOPICS']
        myStuff['Receiver'] = '/rcviot'
        myStuff['Quit'] = '/quitiot'
        try:
            with open(saveAsFile, 'w') as confFile:
                confDat.write(confFile)
            logger.debug(f"Generated test config {saveAsFile}")
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed generic test config {saveAsFile} for writing: {eeh}")
            # self.fail(f"Failed to generate a test config file")
            return False
        return True


    def setUp(self) -> None:
        print('\n== setUp Test Case ==')
        ##sys.stdout.flush()
        testFile = self.defaultTestFile
        if len(sys.argv) > 1:
            testFile = sys.argv[1]
        self.assertTrue(self.genTestConfig())
        self.myConf = MyConf(termPrint=print, sysPrint=logger.debug, confFile=testFile)
        #self.myConf = MyConf(termPrint=logger.info, sysPrint=logger.debug, confFile=testFile)
        ##self.myConf.printConfig()

    def tearDown(self) -> None:
        print('\n== tearDown Test Case ==')
        ##sys.stdout.flush()
        try:
            os.remove(self.defaultTestFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            self.fail("tearDown failure")
            return

    def test_ReadConfig(self) -> None:
        self.myConf.printConfig()

    def test_PrintSection(self) -> None:
        self.myConf.printSection('SERVER_TOPICS')

    def test_SaveConfig(self) -> None:
        copyTestFile = "copy-" + self.defaultTestFile
        self.assertTrue(self.myConf.saveConfig(copyTestFile))
        try:
            os.remove(copyTestFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed removing copy of test config {self.testFile}: {eeh}")
            self.fail("save config failure")




if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    logger.debug("Running unit testing...")
    unittest.main()
