import os

import util
from util import *
from config import *
from rcbxmlreaderwriter import RcbXmlReaderWriter
from xml.etree.ElementTree import *


class ConfigXmlWriter(RcbXmlReaderWriter):

    def __init__(self, createNew):

        Logutil.log('init ConfigXmlWriter', util.LOG_LEVEL_INFO)

        self.createNew = createNew

        if createNew:
            configFile = os.path.join(util.getAddonInstallPath(), 'resources', 'database', 'config_template.xml')
        else:
            configFile = util.getConfigXmlPath()

        if not os.path.isfile(configFile):
            Logutil.log('File config.xml does not exist. Place a valid config file here: ' + str(configFile),
                        util.LOG_LEVEL_ERROR)
        else:
            self.tree = ElementTree().parse(configFile)

    #Functions for generating XML objects from objects

    def getXmlAttributesForRomCollection(self, rc):
        return {'id': str(rc.id), 'name': rc.name}

    def getXmlElementsForRomCollection(self, rc):
        elements = []
        # String attributes
        for e in ['gameclient', 'emulatorCmd', 'emulatorParams', 'preCmd', 'postCmd',
                  'saveStatePath', 'saveStateParams']:
            try:
                el = Element(e, {})
                el.text = getattr(rc, e)
                elements.append(el)
            except AttributeError:
                # Skip any errors
                pass

        # Non-string attributes
        for e in ['useBuiltinEmulator', 'useEmuSolo', 'usePopen', 'ignoreOnScan', 'allowUpdate', 'autoplayVideoMain',
                  'autoplayVideoInfo', 'useFoldernameAsGamename', 'maxFolderDepth', 'doNotExtractZipFiles',
                  'makeLocalCopy', 'diskPrefix']:
            try:
                el = Element(e, {})
                el.text = str(getattr(rc, e))
                elements.append(el)
            except AttributeError:
                # Skip any errors
                pass

        for romPath in rc.romPaths:
            el = Element('romPath', {})
            el.text = romPath
            elements.append(el)

        return elements

    def getXmlAttributesForSite(self, site):
        attrs = {'name': site.name, 'path': site.path}
        return attrs

    def getXmlElementsForSite(self, site):
        """ Not needed """
        pass

    def writeRomCollections(self, romCollections, isEdit):

        Logutil.log('write Rom Collections', util.LOG_LEVEL_INFO)

        romCollectionsXml = self.tree.find('RomCollections')

        #HACK: remove all Rom Collections and create new
        if isEdit:
            for romCollectionXml in romCollectionsXml.findall('RomCollection'):
                romCollectionsXml.remove(romCollectionXml)

        for romCollection in romCollections.values():

            Logutil.log('write Rom Collection: ' + str(romCollection.name), util.LOG_LEVEL_INFO)

            romCollectionXml = SubElement(romCollectionsXml, 'RomCollection',
                                          self.getXmlAttributesForRomCollection(romCollection))

            for subel in self.getXmlElementsForRomCollection(romCollection):
                romCollectionXml.append(subel)

            for mediaPath in romCollection.mediaPaths:

                success, message = self.searchConfigObjects('FileTypes/FileType', mediaPath.fileType.name, 'FileType')
                if not success:
                    return False, message

                SubElement(romCollectionXml, 'mediaPath', {'type': mediaPath.fileType.name}).text = mediaPath.path

            #image placing
            if not self.createNew:
                #in case of an update we have to create new options
                if romCollection.name == 'MAME' and not self.createNew:
                    self.addFileTypesForMame()
                    self.addImagePlacingForMame()

            if romCollection.imagePlacingMain != None and romCollection.imagePlacingMain.name != '':
                success, message = self.searchConfigObjects('ImagePlacing/fileTypeFor',
                                                            romCollection.imagePlacingMain.name, 'ImagePlacing')
                if not success:
                    return False, message
                SubElement(romCollectionXml, 'imagePlacingMain').text = romCollection.imagePlacingMain.name
            else:
                SubElement(romCollectionXml, 'imagePlacingMain').text = 'gameinfobig'

            if romCollection.imagePlacingInfo != None and romCollection.imagePlacingInfo.name != '':
                success, message = self.searchConfigObjects('ImagePlacing/fileTypeFor',
                                                            romCollection.imagePlacingInfo.name, 'ImagePlacing')
                if not success:
                    return False, message
                SubElement(romCollectionXml, 'imagePlacingInfo').text = romCollection.imagePlacingInfo.name
            else:
                SubElement(romCollectionXml, 'imagePlacingInfo').text = 'gameinfosmall'

            if romCollection.scraperSites == None or len(romCollection.scraperSites) == 0:
                #use thegamesdb.net as default scraper in online scraping scenario
                SubElement(romCollectionXml, 'scraper', {'name': 'thegamesdb.net', 'default': 'True'})
            else:
                for scraperSite in romCollection.scraperSites:
                    if scraperSite == None:
                        continue
                    attributes = {'name': scraperSite.name}
                    if scraperSite.path:
                        attributes['path'] = scraperSite.path
                    if scraperSite.default:
                        attributes['default'] = str(scraperSite.default)

                    SubElement(romCollectionXml, 'scraper', attributes)

        success, message = self.writeFile()
        return success, message

    def writeMissingFilter(self, showHideOption, artworkOrGroup, artworkAndGroup, infoOrGroup, infoAndGroup):

        Logutil.log('write Missing Info Filter', util.LOG_LEVEL_INFO)

        missingFilterXml = self.tree.find('MissingFilter')

        #HACK: remove MissingFilter-element
        if missingFilterXml != None:
            self.tree.remove(missingFilterXml)

        missingFilterXml = SubElement(self.tree, 'MissingFilter')
        SubElement(missingFilterXml, 'showHideOption').text = showHideOption

        if len(artworkOrGroup) > 0 or len(artworkAndGroup) > 0:
            missingArtworkXml = SubElement(missingFilterXml, 'missingArtworkFilter')
            self.addMissingFilterItems(missingArtworkXml, artworkOrGroup, 'orGroup')
            self.addMissingFilterItems(missingArtworkXml, artworkAndGroup, 'andGroup')
        if len(infoOrGroup) > 0 or len(infoAndGroup) > 0:
            missingInfoXml = SubElement(missingFilterXml, 'missingInfoFilter')
            self.addMissingFilterItems(missingInfoXml, infoOrGroup, 'orGroup')
            self.addMissingFilterItems(missingInfoXml, infoAndGroup, 'andGroup')

        success, message = self.writeFile()
        return success, message

    def addMissingFilterItems(self, missingXml, group, groupName):
        if len(group) > 0:
            groupXml = SubElement(missingXml, groupName)
            for item in group:
                SubElement(groupXml, 'item').text = item

    def searchConfigObjects(self, xPath, nameToCompare, objectType):
        objects = self.tree.findall(xPath)
        objectFound = False
        for obj in objects:
            objectName = obj.attrib.get('name')
            if objectName == nameToCompare:
                objectFound = True
                break

        if not objectFound:
            return False, util.localize(32009) % (objectType, nameToCompare)

        return True, ''

    def removeRomCollection(self, RCName):

        Logutil.log('removeRomCollection', util.LOG_LEVEL_INFO)

        configFile = util.getConfigXmlPath()
        self.tree = ElementTree().parse(configFile)
        romCollectionsXml = self.tree.find('RomCollections')
        for romCollectionXml in romCollectionsXml.findall('RomCollection'):
            name = romCollectionXml.attrib.get('name')
            if name == RCName:
                romCollectionsXml.remove(romCollectionXml)

        success, message = self.writeFile()
        return success, message

    def addFileTypesForMame(self):
        Logutil.log('addFileTypesForMame', util.LOG_LEVEL_INFO)

        fileTypesXml = self.tree.find('FileTypes')

        #check if the MAME FileTypes already exist
        cabinetExists = False
        marqueeExists = False
        actionExists = False
        titleExists = False
        highestId = 0
        fileTypeXml = fileTypesXml.findall('FileType')
        for fileType in fileTypeXml:
            name = fileType.attrib.get('name')
            if name == 'cabinet':
                cabinetExists = True
            elif name == 'marquee':
                marqueeExists = True
            elif name == 'action':
                actionExists = True
            elif name == 'title':
                titleExists = True

            ftid = fileType.attrib.get('id')
            if int(ftid) > highestId:
                highestId = int(ftid)

        if not cabinetExists:
            self.createFileType(fileTypesXml, str(highestId + 1), 'cabinet', 'image', 'game')
        if not marqueeExists:
            self.createFileType(fileTypesXml, str(highestId + 2), 'marquee', 'image', 'game')
        if not actionExists:
            self.createFileType(fileTypesXml, str(highestId + 3), 'action', 'image', 'game')
        if not titleExists:
            self.createFileType(fileTypesXml, str(highestId + 4), 'title', 'image', 'game')

    def createFileType(self, fileTypesXml, ftid, name, filetype, parent):
        fileType = SubElement(fileTypesXml, 'FileType', {'id': str(ftid), 'name': name})
        SubElement(fileType, 'type').text = filetype
        SubElement(fileType, 'parent').text = parent

    def addImagePlacingForMame(self):
        Logutil.log('addImagePlacingForMame', util.LOG_LEVEL_INFO)

        imagePlacingXml = self.tree.find('ImagePlacing')

        #check if the MAME ImagePlacing options already exist
        cabinetExists = False
        marqueeExists = False
        fileTypeForXml = imagePlacingXml.findall('fileTypeFor')
        for fileTypeFor in fileTypeForXml:
            name = fileTypeFor.attrib.get('name')
            if name == 'gameinfomamecabinet':
                cabinetExists = True
            elif name == 'gameinfomamemarquee':
                marqueeExists = True

        if not cabinetExists:
            fileTypeFor = SubElement(imagePlacingXml, 'fileTypeFor', {'name': 'gameinfomamecabinet'})
            for imgtype in ['cabinet', 'boxfront', 'title']:
                SubElement(fileTypeFor, 'fileTypeForGameList').text = imgtype
                SubElement(fileTypeFor, 'fileTypeForGameListSelected').text = imgtype

            for imgtype in ['boxfront', 'title', 'action']:
                SubElement(fileTypeFor, 'fileTypeForMainViewBackground').text = imgtype

            SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoUpperLeft').text = 'title'
            SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoUpperRight').text = 'action'
            SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoLower').text = 'marquee'

        if not marqueeExists:
            fileTypeFor = SubElement(imagePlacingXml, 'fileTypeFor', {'name': 'gameinfomamemarquee'})
            for imgtype in ['marquee', 'boxfront', 'title']:
                SubElement(fileTypeFor, 'fileTypeForGameList').text = imgtype
                SubElement(fileTypeFor, 'fileTypeForGameListSelected').text = imgtype

            for imgtype in ['boxfront', 'title', 'action']:
                SubElement(fileTypeFor, 'fileTypeForMainViewBackground').text = imgtype

            SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoLeft').text = 'cabinet'
            SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoUpperRight').text = 'action'
            SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoLowerRight').text = 'title'

    # FIXME TODO This function is only called within this class - raise exception rather than return tuple
    def writeFile(self):
        Logutil.log('writeFile', util.LOG_LEVEL_INFO)
        #write file
        try:
            configFile = util.getConfigXmlPath()

            self.indentXml(self.tree)
            treeToWrite = ElementTree(self.tree)
            treeToWrite.write(configFile)

            return True, ""

        except Exception, (exc):
            print("Error: Cannot write config.xml: " + str(exc))
            return False, util.localize(32008) + ": " + str(exc)
