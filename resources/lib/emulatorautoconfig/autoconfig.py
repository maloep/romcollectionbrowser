
import os, sys
import xml.etree.ElementTree as ET
from rcbxmlreaderwriter import RcbXmlReaderWriter

class OperatingSystem(object):
    def __init__(self):
        self.name = ''
        self.versions = []
        self.platforms = []

    def __repr__(self):
        return "<OperatingSystem: %s>" % self.__dict__

class DetectionMethod(object):
    def __init__(self):
        self.name = ''
        self.command = ''
        self.packagename = ''
        self.folders = []

    def __repr__(self):
        return "<DetectionMethod: %s>" % self.__dict__


class Platform(object):
    def __init__(self):
        self.name = ''
        self.aliases = []
        self.emulators = []

    def __repr__(self):
        return "<Platform: %s>" % self.__dict__

class Emulator(object):
    def __init__(self):
        self.name = ''
        self.os = ''
        self.platform = ''
        self.isInstalled = False
        self.installdir = ''
        self.emuCmd = ''
        self.emuParams = ''
        self.detectionMethods = []

    def __repr__(self):
        return "<Emulator: %s>" % self.__dict__


class EmulatorAutoconfig(RcbXmlReaderWriter):
    def __init__(self, configFile):
        self.configFile = configFile
        self.tree = None
        self.operatingSystems = []
    
    def initXml(self):
        try:
            tree = ET.ElementTree().parse(self.configFile)
        except ET.ParseError as err:
            print 'EmulatorAutoconfig ERROR: Could not read emu_autoconfig.xml'
            return None
        
        return tree

    def readXml(self):
        self.tree = self.initXml()
        if self.tree is None:
            return
        
        self.operatingSystems = self.readOperatingSystems(self.tree)
        
    def readOperatingSystems(self, tree):
        operatingSystems = []

        osRows = self.tree.findall('os')
        for osRow in osRows:
            operatingSystem = OperatingSystem()
            operatingSystem.name = osRow.attrib.get('name')
            if(osRow.attrib.get('version')):
                operatingSystem.versions = [version.strip() for version in osRow.attrib.get('version').split(',')]
            operatingSystem.platforms = self.readPlatforms(osRow)
            operatingSystems.append(operatingSystem)
            
        return operatingSystems

    def readPlatforms(self, osRow):
        platformRows = osRow.findall('platform')
        if platformRows is None:
            print 'EmulatorAutoconfig ERROR: Could not find node os/platform in emu_autoconfig.xml'
            return []
            
        platforms = []
            
        for platformRow in platformRows:
            platform = Platform()
            platform.name = platformRow.attrib.get('name')
            aliases = []
            aliasRows = platformRow.findall('alias')
            if aliasRows is not None:
                for aliasRow in aliasRows:
                    aliases.append(aliasRow.text)
            platform.aliases = aliases
            platform.emulators = self.readEmulators(platformRow, osRow)
            platforms.append(platform)
            
        return platforms

    def readEmulators(self, platformRow, osRow):
        
        emulatorRows = platformRow.findall('emulator')
        if emulatorRows is None:
            print 'EmulatorAutoconfig ERROR: Could not find node os/platform/emulator in emu_autoconfig.xml'
            return []
        
        emulators = []
        
        for emulatorRow in emulatorRows:
            emulator = Emulator()
            emulator.name = emulatorRow.attrib.get('name')
            emulator.os = osRow.attrib.get('name')
            emulator.platform = platformRow.attrib.get('name')
            emulator.emuCmd = self.readTextElement(emulatorRow, 'configuration/emulatorCommand')
            emulator.emuParams = self.readTextElement(emulatorRow, 'configuration/emulatorParams')
            emulator.detectionMethods = self.readDetectionMethods(emulatorRow, osRow)
            
            emulators.append(emulator)
            
        return emulators

    def readDetectionMethods(self, emulatorRow, osRow):
        
        detectionMethodRows = emulatorRow.findall('detectionMethod')
        if detectionMethodRows is None:
            print 'EmulatorAutoconfig WARNING: Could not find node os/platform/emulator/detectionMethod in emu_autoconfig.xml'
            return []
        
        globalDMRows = osRow.findall('detectionMethods/detectionMethod')
        if globalDMRows is None:
            globalDMRows = []
        
        detectionMethods = []
        
        for detectionMethodRow in detectionMethodRows:
            detectionMethod = DetectionMethod()
            detectionMethod.name = detectionMethodRow.attrib.get('name')
            
            if detectionMethod.name == 'packagename':
                for globalDMRow in globalDMRows:
                    if globalDMRow.attrib.get('name') == 'packagename':
                        detectionMethod.command = self.readTextElement(globalDMRow, 'command')
                        
                detectionMethod.packagename = self.readTextElement(detectionMethodRow, 'packagename')
            elif detectionMethod.name == 'commonFolders':
                folderRows = detectionMethodRow.findall('folder')
                for folderRow in folderRows:                    
                    detectionMethod.folders.append(folderRow.text)
            
            detectionMethods.append(detectionMethod)
            
        return detectionMethods

    def findEmulators(self, operatingSystemName, osVersionInfo, platformName, checkInstalledState=False):
        """
        Parse the emu_autoconfig.xml file for a specified OS and platform
        Args:
            operatingSystemName: The OS to find. This is currently limited to Android, OSX, Windows or Linux.
            osVersionInfo: specific version of the OS. For example "Windows 10", "LibreELEC", ...   
            platformName: The emulator platform
            checkInstalledState: Whether to check if the found emulator is installed

        Returns: a list of matching Emulator objects, or an empty list if there was an error.

        """
        print 'EmulatorAutoconfig: findEmulators(). os = %s, osVersionInfo = %s, platform = %s, checkInstalled = %s' % (operatingSystemName,
                                                                                                    osVersionInfo,
                                                                                                    platformName,
                                                                                                    str(checkInstalledState))
        
        # Read autoconfig.xml file
        if self.tree == None or len(self.operatingSystems) == 0:
            self.readXml()

        osFound = self.findOsByNameAndVersion(operatingSystemName, osVersionInfo)

        if osFound is None:
            print 'EmulatorAutoconfig ERROR: Could not find os %s in emu_autoconfig.xml' % operatingSystemName
            return []
            
        platformFound = None
        for platform in osFound.platforms:
            if platform.name == platformName:
                platformFound = platform
            else:
                if platform.aliases:
                    for alias in platform.aliases:
                        if(alias == platformName):
                            platformFound = platform 
            
        if platformFound is None:
            print 'EmulatorAutoconfig ERROR: Could not find platform %s for os %s in emu_autoconfig.xml' % (platformName,
                                                                                                            operatingSystemName)
            return []
        
        if checkInstalledState:
            for emulator in platformFound.emulators:
                emulator.isInstalled = self.isInstalled(emulator)
        
        return platformFound.emulators
    
    
    def findOsByNameAndVersion(self, operatingSystemName, osVersionInfo):
        
        osFound = None
        
        for operatingSystem in self.operatingSystems:
            if operatingSystem.name == operatingSystemName:
                if(len(operatingSystem.versions) == 0):
                    osFound = operatingSystem
                #version specific os will override general os entry
                if(next((version for version in operatingSystem.versions if version in osVersionInfo),None)):
                    return operatingSystem
                    
        return osFound
    

    def isInstalled(self, emulator):
        print 'EmulatorAutoconfig: isInstalled(). emulator = %s' % emulator.name
        
        for detectionMethod in emulator.detectionMethods:
            print 'EmulatorAutoconfig: detectionMethod.name = ' + detectionMethod.name
            if detectionMethod.name == 'packagename':
                try:
                    packages = os.popen(detectionMethod.command).readlines()
                except OSError as exc:
                    print 'EmulatorAutoconfig ERROR: error while reading list of packages: %s' % str(exc)
                    # Try with the next detectionMethod
                    continue

                print 'EmulatorAutoconfig: packages = ' + str(packages)
                for package in packages:
                    print 'EmulatorAutoconfig: package = ' + package
                    print 'EmulatorAutoconfig: detectionMethod.packagename = ' + detectionMethod.packagename
                    if package.strip() == detectionMethod.packagename.strip():
                        print 'EmulatorAutoconfig: emulator is installed!'
                        return True

            elif detectionMethod.name == 'registry':
                print 'Emulator installation status via registry has not been implemented'
                pass

            elif detectionMethod.name == 'commonFolders':
                for folder in detectionMethod.folders:
                    #resolve windows environment variables like %APPDATA%
                    newFolder = ''
                    parts = folder.split('%')
                    for part in parts:
                        partEnv = os.getenv(part)
                        if(partEnv):
                            newFolder = newFolder +partEnv
                        else:
                            newFolder = newFolder +part
                    
                    if(os.path.exists(newFolder)):
                        emulator.installdir = newFolder
                        return True
            else:
                print 'Unhandled detection method: {0}'.format(detectionMethod.name)

        return False
    
    def readTextElement(self, parent, elementName):
        element = parent.find(elementName)
        if element != None and element.text != None:
            return element.text
        else:
            return ''
