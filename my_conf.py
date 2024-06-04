#!/usr/bin/env python3

##  Wrapper for ConfigParser to deal with '.ini' style config file
##  Config is used to primarily put literal values into a
##  single place for ease of modifications.

import os
##import sys
import time
import datetime
import locale
##import subprocess
import configparser
import unittest
import logging


##logging.basicConfig(level=logging.DEBUG, filename=logFile)
logger = logging.getLogger(__name__)


class MyConf(configparser.ConfigParser):
    """ Derived class Configparser for custom config file processing. Also,
        so that 'stdout/stderr' are configurable, and specialty methods.
    """
    def __init__(self, termPrint, sysPrint, confFile=None, parent=None):
        """ termPrint => stdout, sysPrint => stderr. Needed for UI purposes """
        super().__init__(parent)
        self.write_chat = termPrint
        self.write_con = sysPrint
        if confFile:
            try:
                self.read(confFile)
            except Exception as eeh:
                self.write_con(f"Class of exception is : {type(eeh).__name__}")
                self.write_con(f"failed opening {confFile} for reading: {eeh}")
                self.write_con("Error Initializing config. Moving on")

    def printConfig(self) -> None:
        """ print out configuration to terminal """
        if len(self.sections()) < 1:
            self.write_con("Config is empty")
            return
        self.write_chat("Print config")
        for sx in self.sections():
            self.write_chat(f"[{sx}]")
            for kx in self[sx]:
                self.write_chat(f" {kx} = {self[sx][kx]}")
        return

    def readConfig(self, confFile, mergeIn=False) -> None:
        """ load configuration file """
        if not mergeIn:
            if len(self.sections()) > 0:
                self.write_con("Re-reading config file")
                self.clear()    ## NOTE: special builtin section DEFAULTSECT not removed
        if confFile is None:
            self.write_con("No filename given to read configuration")
            return
        try:
            self.read(confFile)
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed opening {confFile} for reading: {eeh}")
            if not mergeIn:
                self.write_con(f"Error merging config {confFile}. Moving on")
            else:
                self.write_con(f"Error loading config {confFile}. Moving on")
        return

    def setSectionValue(self, useSection, useKey, useValue) -> None:
        """ create or set a value of a key in a section """
        if useSection not in self.sections():
            self[useSection] = {}
        self[useSection][useKey] = useValue
        return

    def getSectionValue(self, useSection, useKey, useDefault) -> str:
        """ get value of a key in a section """
        if useSection not in self.sections():
            return useDefault
        if self[useSection][useKey]:
            return self[useSection][useKey]
        else:
            return useDefault

    def delSectionKey(self, useSection, useKey) -> None:
        """ remove key in a section """
        try:
            self.remove_option(useSection,useKey)
        except configparser.NoSectionError:
            self.write_con(f"Removing key {useKey} from none existant section {useSection}")
            return
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed deleting key {useKey} in config section {useSection} : {eeh}")
            self.write_con(f"Error deleting key {useKey} in section {useSection}. Moving on")
        return

    def delSection(self, useSection) -> None:
        """ remove section in config """
        try:
            self.remove_section(useSection)
        except configparser.NoSectionError:
            self.write_con(f"Removing non-existant section {useSection} from config")
            return
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed deleting config section {useSection} : {eeh}")
            self.write_con(f"Error deleting no-existant section {useSection}. Moving on")
        return

    def addSection(self, useSection) -> None:
        """ add section in config if missing """
        if self.haveSection(useSection):
            return
        try:
            self.add_section(useSection)
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed adding config section {useSection} : {eeh}")
            self.write_con(f"Error adding config section {useSection}. Moving on")
        return

    def getSection(self, useSection) -> dict:
        """ return section in config, empty dictionary if missing """
        if useSection in self.sections():
            return dict(self[useSection])
        return {}

    def haveSection(self, useSection) -> bool:
        """ Check existance of a section in config """
        return useSection in self.sections()

    def haveKey(self, useSection, useKey) -> bool:
        """ Check existance of a key in a section of config """
        if useSection not in self.sections():
            return False
        return useKey in self[useSection]

    def printSection(self, useSection) -> None:
        """ Print to terminal section of config """
        if useSection not in self.sections():
            self.write_con(f"No section {useSection} in config")
            return
        self.write_chat(f"Print section {useSection}")
        if useSection in self.sections():
            for kx in self[useSection]:
                self.write_chat(f" {kx} = {self[useSection][kx]}")
        return

    def saveConfig(self, useFile) -> bool:
        """ Save config to file. Returns bool used mostly for testing """
        try:
            with open(useFile, 'w') as config_file:
                self.write(config_file)
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed opening {useFile} for writing: {eeh}")
            self.write_con(f"Failed writing config to {useFile}")
            return False
        return True


class test_MyConf(unittest.TestCase):
    """ unittest class for testing MyConf class """
    ## class variables
    dateOnly = datetime.date.today()
    timeOnly = time.strftime("%H_%M_%S")
    defaultTestFile = "testconf-" + str(dateOnly) + "-" + timeOnly + ".conf"

    @classmethod
    def setUpClass(cls) -> None:
        """ Setup done before any test case """
        print('\n=== setUp Unit Testing ===')
        ##sys.stdout.flush()
        locale.setlocale(locale.LC_ALL, '')
        # Generate a sample config file
        cls.genTestConfig(cls.defaultTestFile)

    @classmethod
    def tearDownClass(cls) -> None:
        """ Teardown done after all test cases """
        print('\n=== tearDown Unit Testing ===')
        ##sys.stdout.flush()
        try:
            os.remove(cls.defaultTestFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            unittest.fail("tearDown failure")
            return

    @classmethod
    def genTestConfig(cls, testFile=None) -> bool:
        """ Generate an example config for testing purposes """
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
            logger.warning(f"failed generic test config {saveAsFile} for writing : {eeh}")
            # self.fail(f"Failed to generate a test config file")
            return False
        return True

    def setUp(self) -> None:
        """ test case setup """
        ##print('\n== setUp Test Case ==')
        ##sys.stdout.flush()
        try:
            self.myConf = MyConf(termPrint=print, sysPrint=print, confFile=self.defaultTestFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            self.fail("Failed to setup test case")

    def tearDown(self) -> None:
        """ test case teardown """
        ##print('\n== tearDown Test Case ==')
        ##sys.stdout.flush()
        pass

    def test_ReadConfig(self) -> None:
        """ test case read config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.myConf = MyConf(termPrint=print, sysPrint=print)   ## redo myConf because setUp()
            self.myConf.readConfig(confFile=self.defaultTestFile,mergeIn=False)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            self.fail("Failed to read config file")

    def test_printConfig(self) -> None:
        """ test case print config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.myConf.printConfig()
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            self.fail("Failed to print config file")

    def test_PrintSection(self) -> None:
        """ test case print section of config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.myConf.printSection('SERVER_TOPICS')
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            self.fail(f"Failed to print section of config file")

    def test_SaveConfig(self) -> None:
        """ test case save config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        copyTestFile = "copy-" + self.defaultTestFile
        self.assertTrue(self.myConf.saveConfig(copyTestFile))
        try:
            os.remove(copyTestFile)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed removing copy of test config {self.testFile}: {eeh}")
            self.fail("save config failure")

    def test_setSectionValue(self) -> None:
        """ test case assign value to a key in a section of config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.myConf.setSectionValue("SERVER_TOPICS", "greeting", "Hello Dude!")
            self.myConf.printSection("SERVER_TOPICS")
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning("failed set setting section value")
            self.fail("save set section value failure")

    def test_haveKey(self) -> None:
        """ test case existance of key in a section of config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.assertFalse(self.myConf.haveKey("SERVER_TOPICS", "greeting"))
            self.myConf.setSectionValue("SERVER_TOPICS", "greeting", "Hello Dude!")
            self.assertTrue(self.myConf.haveKey("SERVER_TOPICS", "greeting"))
            self.myConf.printSection("SERVER_TOPICS")
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning("failed checking key existance")
            self.fail("key existance check failure")

    def test_haveSection(self) -> None:
        """ test case existance of section of config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.assertFalse(self.myConf.haveSection("GREETINGS"))
            self.myConf.addSection("GREETINGS")
            self.assertTrue(self.myConf.haveSection("GREETINGS"))
            self.myConf.printSection("GREETINGS")
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning("failed checking section existance")
            self.fail("section existance check failure")


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    logger.debug("Running unit testing...")
    unittest.main()
