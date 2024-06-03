#!/usr/bin/env python3

import os
import sys
import locale
import subprocess
import configparser
import unittest
import logging


##logging.basicConfig(level=logging.DEBUG, filename=logFile)
logger = logging.getLogger(__name__)


class MyConf():
    def __init__(self, termPrint, sysPrint, confFile=None, parent=None):
        self.writeChat = termPrint
        self.writeCon = sysPrint
        self.confDat = {}
        if confFile:
            self.readConfig(confFile)

    def printConfig(self):
        if not self.confDat:
            logger.warning("No config file read yet")
            return
        print("Print config")
        for sectNow in self.confDat.sections():
            print(f"[{sectNow}]")
            for keyNow in self.confDat[sectNow]:
                print(f" {keyNow} = {self.confDat[sectNow][keyNow]}")

    def readConfig(self, confFile):
        if self.confDat:
            logger.warning("Re-reading config file")
        self.confDat = configparser.ConfigParser()
        try:
            self.confDat.read(confFile)
            ## self.printConfig()   ## Uncomment for testing
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed opening {confFile} for reading: {eeh}")
            logger.debug("Continuing on")
            return

    def set_section_value(self, useSection, useKey, useValue):
        if useSection not in confDat:
            self.confDat[useSection] = {}
        self.confDat[useSection][useKey] = useValue

    def get_section_value(self, useSection, useKey, useDefault):
        if useSection not in self.confDat:
            return useDefault
        if self.confDat[useSection][useKey]:
            return self.confDat[useSection][useKey]
        else:
            return useDefault

    def get_config_section(self, useSection):
        # Assuming a section called 'Settings' exists in the config file
        if useSection in self.confDat:
            return dict(self.confDat[useSection])
        return {}

    def printSection(self, useSection):
        if not self.confDat:
            logger.warning("No config file read yet")
            return
        print(f"Print section {useSection}")
        if useSection in self.confDat:
            for keyNow in self.confDat[useSection]:
                print(f" {keyNow} = {self.confDat[useSection][keyNow]}")


    def save_config(self, useFile):
        with open(useFile, 'w') as config_file:
            self.confDat.write(config_file)
        return None


class test_MyConf(unittest.TestCase):
    ## class variable
    defaultTestFile = "generated.conf"

    @classmethod
    def setUpClass(cls):
        print('\n=== setUp Unit Tests ===')
        sys.stdout.flush()
        locale.setlocale(locale.LC_ALL, '')

    @classmethod
    def tearDownClass(cls):
        print('\n=== tearDown Unit Tests ===')
        sys.stdout.flush()

    @classmethod
    def genTestConfig(cls, testFile=None):
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
            self.fail(f"Failed to generate a test config file")
            return


    def setUp(self):
        print('\n== setUp Test Case ==')
        sys.stdout.flush()
        self.testFile = self.defaultTestFile
        if len(sys.argv) > 1:
            self.testFile = sys.argv[1]
        self.genTestConfig()
        self.myConf = MyConf(termPrint=logger.info, sysPrint=logger.debug, confFile=self.testFile)
        ##self.myConf.printConfig()

    def tearDown(self):
        print('\n== tearDown Test Case ==')
        sys.stdout.flush()
        logger.debug(f"Removing conf {self.testFile}")
        if self.testFile == self.defaultTestFile:
            try:
                os.remove(self.testFile)
            except Exception as eeh:
                logger.warning(f"Class of exception is : {type(eeh).__name__}")
                logger.warning(f"failed removing test config {self.testFile}: {eeh}")
                self.fail("tearDown failure")
                return
        else:
            logger.warning(f"Not removing non-default config file file {self.testFile}")

    def test_ReadConfig(self):
        logger.debug(f"Reading conf {self.testFile}")
        self.myConf.printConfig()

    def test_PrintSection(self):
        logger.debug(f"Reading conf {self.testFile}")
        self.myConf.printSection('SERVER_TOPICS')

    ## FIXME: Actually add tests to exercize the rest of MyConf


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    logger.debug("Running unit testing...")
    unittest.main()
