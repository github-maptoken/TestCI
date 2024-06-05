#!/usr/bin/env python3
"""
  Wrapper for ConfigParser to deal with '.ini' style config file
  Config is used to primarily put literal values into a
  single place for ease of modifications.
"""

import os
# import sys
import time
import datetime

from typing import Callable, Optional, Any
import locale
import configparser
import unittest
import logging

USE_ENCODING = "utf-8"

# logging.basicConfig(level=logging.DEBUG, filename=logFile)
logger = logging.getLogger(__name__)


class MyConf(configparser.ConfigParser):
    """ Derived class Configparser for custom config file processing. Also,
        so that 'stdout/stderr' are configurable, and specialty methods.
    """
    def __init__(self,
                 termout: Callable[[str],None],
                 sysout: Callable[[str],None],
                 conf_file: Optional[str] = None,
                 parent: Any = None) -> None:
        """ termout => stdout, sysout => stderr. Needed for UI purposes """
        super().__init__(parent)
        self.write_chat = termout
        self.write_con = sysout
        if conf_file:
            try:
                self.read(conf_file)
            except Exception as eeh:
                self.write_con(f"Class of exception is : {type(eeh).__name__}")
                self.write_con(f"failed opening {conf_file} for reading: {eeh}")
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

    def readConfig(self, conf_file: str, merge_in_flag: bool = False) -> None:
        """ load configuration file """
        if not merge_in_flag:
            if len(self.sections()) > 0:
                self.write_con("Re-reading config file")
                self.clear()    # NOTE: special builtin section DEFAULTSECT not removed
        if conf_file is None:
            self.write_con("No filename given to read configuration")
            return
        try:
            self.read(conf_file)
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed opening {conf_file} for reading: {eeh}")
            if not merge_in_flag:
                self.write_con(f"Error merging config {conf_file}. Moving on")
            else:
                self.write_con(f"Error loading config {conf_file}. Moving on")

    def setSectionValue(self, sect_name: str, key_name: str, use_value: str) -> None:
        """ create or set a value of a key in a section """
        if sect_name not in self.sections():
            self[sect_name] = {}
        self[sect_name][key_name] = use_value

    def getSectionValue(self, sect_name: str, key_name: str, use_default: str) -> str:
        """ get value of a key in a section """
        if sect_name not in self.sections():
            return use_default
        if self[sect_name][key_name]:
            return self[sect_name][key_name]
        return use_default

    def delKey(self, sect_name: str, key_name: str) -> None:
        """ remove key in a section """
        try:
            self.remove_option(sect_name, key_name)
        except configparser.NoSectionError:
            self.write_con(f"Removing key {key_name} from none existant section {sect_name}")
            return
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed deleting key {key_name} in config section {sect_name} : {eeh}")
            self.write_con(f"Error deleting key {key_name} in section {sect_name}. Moving on")

    def delSection(self, sect_name: str) -> None:
        """ remove section in config """
        try:
            self.remove_section(sect_name)
        except configparser.NoSectionError:
            self.write_con(f"Removing non-existant section {sect_name} from config")
            return
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed deleting config section {sect_name} : {eeh}")
            self.write_con(f"Error deleting no-existant section {sect_name}. Moving on")

    def addSection(self, sect_name: str) -> None:
        """ add section in config if missing """
        if self.haveSection(sect_name):
            return
        try:
            self.add_section(sect_name)
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed adding config section {sect_name} : {eeh}")
            self.write_con(f"Error adding config section {sect_name}. Moving on")

    def getSection(self, sect_name: str) -> dict[str,str]:
        """ return section in config, empty dictionary if missing """
        if sect_name in self.sections():
            return dict(self[sect_name])
        return {}

    def haveSection(self, sect_name: str) -> bool:
        """ Check existance of a section in config """
        return sect_name in self.sections()

    def haveKey(self, sect_name: str, key_name: str) -> bool:
        """ Check existance of a key in a section of config """
        if sect_name not in self.sections():
            return False
        return key_name in self[sect_name]

    def printSection(self, sect_name: str) -> None:
        """ Print to terminal section of config """
        if sect_name not in self.sections():
            self.write_con(f"No section {sect_name} in config")
            return
        self.write_chat(f"Print section {sect_name}")
        if sect_name in self.sections():
            for kx in self[sect_name]:
                self.write_chat(f" {kx} = {self[sect_name][kx]}")

    def saveConfig(self, use_filename: str) -> bool:
        """ Save config to file. Returns bool used mostly for testing """
        try:
            with open(use_filename, mode='w', encoding=USE_ENCODING) as conf_file:
                self.write(conf_file)
        except Exception as eeh:
            self.write_con(f"Class of exception is : {type(eeh).__name__}")
            self.write_con(f"failed opening {use_filename} for writing: {eeh}")
            self.write_con(f"Failed writing config to {use_filename}")
            return False
        return True


class Test_MyConf(unittest.TestCase):
    """ unittest class for testing MyConf class """
    # class variables
    dateOnly: Any = datetime.date.today()
    timeOnly: Any = time.strftime("%H_%M_%S")
    default_test_conf = "testconf-" + str(dateOnly) + "-" + timeOnly + ".conf"

    @classmethod
    def setUpClass(cls) -> None:
        """ Setup done before any test case """
        print('\n=== setUp Unit Testing ===')
        # sys.stdout.flush()
        locale.setlocale(locale.LC_ALL, '')
        # Generate a sample config file
        cls.genTestConfig(cls.default_test_conf)

    @classmethod
    def tearDownClass(cls) -> None:
        """ Teardown done after all test cases """
        print('\n=== tearDown Unit Testing ===')
        # sys.stdout.flush()
        try:
            os.remove(cls.default_test_conf)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            return

    @classmethod
    def genTestConfig(cls, test_filename: Optional[str] = None) -> bool:
        """ Generate an example config for testing purposes """
        if test_filename:
            save_filename = test_filename
        else:
            save_filename = cls.default_test_conf
        confDat = configparser.ConfigParser()
        confDat['MAIN'] = {'coreTopic': 'HouseIoT',
                           'devName': 'myDev'
                           }
        confDat['SERVER_TOPICS'] = {}
        confDat['DEVICE_TOPICS'] = {}
        server_section = confDat['SERVER_TOPICS']
        server_section['Receiver'] = '/rcvsrv'
        server_section['Quit'] = '/quitsrv'
        dev_section = confDat['DEVICE_TOPICS']
        dev_section['Receiver'] = '/rcviot'
        dev_section['Quit'] = '/quitiot'
        try:
            with open(save_filename, mode='w', encoding=USE_ENCODING) as conf_file:
                confDat.write(conf_file)
            logger.debug(f"Generated test config {save_filename}")
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed generic test config {save_filename} for writing : {eeh}")
            # self.fail(f"Failed to generate a test config file")
            return False
        return True

    def setUp(self) -> None:
        """ test case setup """
        # print('\n== setUp Test Case ==')
        # sys.stdout.flush()
        try:
            self.myConf = MyConf(termout=print, sysout=print, conf_file=self.default_test_conf)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            self.fail("Failed to setup test case")

    def tearDown(self) -> None:
        """ test case teardown """
        # print('\n== tearDown Test Case ==')
        # sys.stdout.flush()
        # pass

    def test_ReadConfig(self) -> None:
        """ test case read config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        try:
            self.myConf = MyConf(termout=print, sysout=print)   # redo myConf because setUp()
            self.myConf.readConfig(conf_file=self.default_test_conf, merge_in_flag=False)
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
            self.fail("Failed to print section of config file")

    def test_SaveConfig(self) -> None:
        """ test case save config file """
        print(f"\n==> RUNTEST {self.id()} <==")
        copy_conf_file = "copy-" + self.default_test_conf
        self.assertTrue(self.myConf.saveConfig(copy_conf_file))
        try:
            os.remove(copy_conf_file)
        except Exception as eeh:
            logger.warning(f"Class of exception is : {type(eeh).__name__}")
            logger.warning(f"failed removing copy of test config {copy_conf_file}: {eeh}")
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
    # logging.basicConfig(level=logging.DEBUG)
    logger.debug("Running unit testing...")
    unittest.main()
