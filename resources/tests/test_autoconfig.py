"""
Unit tests for autoconfig.py, auto-detecting installed emulators and command-line options

To invoke, from the top-level directory, run:
python -m unittest discover -v resources/tests/ "test_autoconfig.py"
or as part of a full test suite:
python -m unittest discover -v resources/tests/

This has been verified on Mac; other envs will need to be tested manually

"""

from builtins import str
import unittest
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'emulatorautoconfig'))
from autoconfig import EmulatorAutoconfig


class TestAutoConfig(unittest.TestCase):

    autoconfig = None

    @classmethod
    def setUpClass(cls):
        # Create directory paths
        try:
            os.makedirs(os.path.join(os.path.dirname(__file__), 'testdata', 'appdirparent', 'appdirnested'))
        except Exception as err:
            print (str(err))
            pass

        # Create applications in parent directory
        for f in ['TestApp1', 'TestApp2', 'TestApp3']:
            fname = os.path.join(os.path.dirname(__file__), 'testdata', 'appdirparent', f)
            print (u'Creating dummy application {0}'.format(fname))
            with open(fname, 'a'):
                os.utime(fname, None)

        # Create applications in child directory
        for f in ['NestedTestApp1', 'NestedTestApp2', 'NestedTestApp3']:
            fname = os.path.join(os.path.dirname(__file__), 'testdata', 'appdirparent', 'appdirnested', f)
            print (u'Creating dummy nested application {0}'.format(fname))
            with open(fname, 'a'):
                os.utime(fname, None)

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary applications and paths from the testdata directory
        import shutil
        try:
            shutil.rmtree(os.path.join(os.path.dirname(__file__), 'testdata', 'appdirparent'))
        except Exception as err:
            print (str(err))
            pass

    def setUp(self):
        # Set a default config XML file
        self.autoconfigxmlfile = os.path.join(os.path.dirname(__file__), 'testdata', 'test_emu_autoconfig.xml')

    def tearDown(self):
        pass

    def test_FindSingleEmulatorOnMac(self):
        autoconfig = EmulatorAutoconfig(self.autoconfigxmlfile)
        emulators = autoconfig.findEmulators('OSX', 'SNES', False)
        ems_found = len(emulators)
        self.assertTrue(ems_found == 1, u'Found {0} SNES emulators, expecting 1'.format(ems_found))

    def test_FindMultipleEmulatorOnMac(self):
        autoconfig = EmulatorAutoconfig(self.autoconfigxmlfile)
        emulators = autoconfig.findEmulators('OSX', 'Atari 2600', False)
        ems_found = len(emulators)
        self.assertTrue(ems_found == 2, u'Found {0} Atari 2600 emulators, expecting 2'.format(ems_found))

    def test_UnableToFindNonDefinedEmulatorOnMac(self):
        autoconfig = EmulatorAutoconfig(self.autoconfigxmlfile)
        emulators = autoconfig.findEmulators('OSX', 'UnknownPlatform', False)
        ems_found = len(emulators)
        self.assertTrue(ems_found == 0, u'Found {0} "UnknownPlatform" emulators, expecting 0'.format(ems_found))

    def test_EmulatorCommandAndParams(self):
        autoconfig = EmulatorAutoconfig(self.autoconfigxmlfile)
        emulators = autoconfig.findEmulators('OSX', 'SNES', False)
        print(emulators[0].emuCmd)

        self.assertEqual(emulators[0].emuCmd, u'/Applications/RetroArch.app/Contents/MacOS/RetroArch',
                         u'Emulator command doesn\'t equal expected value')
        self.assertEqual(emulators[0].emuParams,
                         u'-v -L /Applications/RetroArch.app/Contents/Resources/cores/snes9x_libretro.dylib "%rom%"',
                         u'Emulator params doesn\'t equal expected value')

    def test_OperatingSystems(self):
        autoconfig = EmulatorAutoconfig(self.autoconfigxmlfile)
        autoconfig.readXml()
        oses = autoconfig.operatingSystems
        self.assertTrue(len(oses) == 4, u'Found {0} operating systems, expecting 4'.format(len(oses)))

    def test_UnableToFindIncorrectOS(self):
        autoconfig = EmulatorAutoconfig(self.autoconfigxmlfile)
        emulators = autoconfig.findEmulators('UnknownOS', 'SNES', False)
        self.assertTrue(len(emulators) == 0, u'Found {0} "UnknownOS" emulators, expecting 0'.format(len(emulators)))

    def test_NoOSElementsFound(self):
        autoconfigxmlfile = os.path.join(os.path.dirname(__file__), 'testdata', 'test_emu_autoconfig_empty.xml')
        autoconfig = EmulatorAutoconfig(autoconfigxmlfile)
        autoconfig.readXml()
        oses = autoconfig.operatingSystems

        self.assertTrue(len(oses) == 0, u'Found {0} operating systems, expecting 0'.format(len(oses)))

    @unittest.skip("Not yet implemented")
    def test_EmulatorInstalled(self):
        """ Need to implement a node under the XML to represent one of our created directories
        """
        pass

    @unittest.skip("Not yet implemented")
    def test_ApplicationInNestedFolder(self):
        """ Skip until we implemented
        """
        pass

    @unittest.skip("Not yet implemented")
    def test_WindowsCommonDirectory(self):
        """ Skip until we implemented
        """
        pass


if __name__ == "__main__":
    unittest.main()
