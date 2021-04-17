from builtins import str
import os, shutil

from util import *
import util
from gamedatabase import *
from xml.etree.ElementTree import *
from rcbxmlreaderwriter import RcbXmlReaderWriter


class ConfigxmlUpdater(RcbXmlReaderWriter):
    tree = None

    def updateConfig(self, configFile):

        if not os.path.isfile(configFile):
            return False, util.localize(32003)

        tree = ElementTree().parse(configFile)
        if tree == None:
            Logutil.log('Could not read config.xml', util.LOG_LEVEL_ERROR)
            return False, util.localize(32004)

        self.tree = tree

        configVersion = tree.attrib.get('version')
        Logutil.log('Reading config version from config.xml: ' + str(configVersion), util.LOG_LEVEL_INFO)
        if configVersion == None:
            #set to previous version
            configVersion = '0.7.4'

        #nothing to do
        if (configVersion == util.CURRENT_CONFIG_VERSION):
            Logutil.log('Config file is up to date', util.LOG_LEVEL_INFO)
            return True, ''

        Logutil.log('Config file is out of date. Start update', util.LOG_LEVEL_INFO)

        #backup config.xml
        newFileName = configFile + '.backup ' + configVersion
        if not os.path.isfile(newFileName):
            try:
                shutil.copy(str(configFile), str(newFileName))
            except Exception as exc:
                return False, util.localize(32007) + ": " + str(exc)

        #write current version to config
        self.tree.attrib['version'] = util.CURRENT_CONFIG_VERSION

        if configVersion == '0.7.4':
            success, message = self.update_074_to_086()
            configVersion = '0.8.6'
            if not success:
                return False, message

        if configVersion == '0.8.6':
            success, message = self.update_086_to_0810()
            configVersion = '0.8.10'
            if not success:
                return False, message

        if configVersion == '0.8.10':
            success, message = self.update_0810_to_090()
            configVersion = '0.9.0'
            if not success:
                return False, message

        if configVersion == '0.9.0':
            success, message = self.update_090_to_095()
            configVersion = '0.9.5'
            if not success:
                return False, message

        if configVersion == '0.9.5':
            success, message = self.update_095_to_106()
            configVersion = '1.0.6'
            if not success:
                return False, message

        if configVersion == '1.0.6':
            success, message = self.update_106_to_208()
            configVersion = '2.0.8'
            if not success:
                return False, message

        if configVersion == '2.0.8':
            success, message = self.update_208_to_214()
            configVersion = '2.1.4'
            if not success:
                return False, message

        if configVersion == '2.1.4':
            success, message = self.update_214_to_220()
            configVersion = '2.2.0'
            if not success:
                return False, message

        #write file
        success, message = self.writeFile(configFile)

        return success, message

    def update_214_to_220(self):

        #remove Scrapers section
        self.removeElement(self.tree, 'Scrapers')

        #find highest file type id
        maxFileTypeId = 0
        createClearlogo = True
        fileTypesXml = self.tree.find('FileTypes')
        fileTypesXmlList = fileTypesXml.findall('FileType')
        for fileTypeXml in fileTypesXmlList:
            #check if filetype clearlogo already exists
            fileTypeName = fileTypeXml.attrib.get('name')
            if fileTypeName == 'clearlogo':
                createClearlogo = False
                break
            fileTypeId = int(fileTypeXml.attrib.get('id'))
            if fileTypeId > maxFileTypeId:
                maxFileTypeId = fileTypeId

        #add clearlogo with highest id +1
        if createClearlogo:
            clearlogoxml = SubElement(fileTypesXml, 'FileType', {'id': str(maxFileTypeId + 1), 'name': 'clearlogo'})
            SubElement(clearlogoxml, 'type').text = 'image'
            SubElement(clearlogoxml, 'parent').text = 'game'

        #remove all configured scrapers from rom collections and add thegamesdb as default scraper
        romCollectionsXml = self.tree.findall('RomCollections/RomCollection')
        for romCollectionXml in romCollectionsXml:
            self.removeElement(romCollectionXml, 'scraper')
            SubElement(romCollectionXml, 'scraper', {'name': 'thegamesdb.net', 'default': 'True'})

        #add fanart as fileTypeForMainViewBackground to MAME views
        imagePlacing = self.tree.find('ImagePlacing')
        fileTypeForList = imagePlacing.findall('fileTypeFor')
        for fileTypeFor in fileTypeForList:
            fileTypeForName = fileTypeFor.attrib.get('name')
            if fileTypeForName == 'gameinfomamemarquee' or fileTypeForName == 'gameinfomamecabinet':
                createFanart = True
                fileTypeForMainViewBackgroundList = fileTypeFor.findall('fileTypeForMainViewBackground')
                insertAtIndex = 0
                for fileTypeForMainViewBackground in fileTypeForMainViewBackgroundList:
                    if insertAtIndex == 0:
                        insertAtIndex = list(fileTypeFor).index(fileTypeForMainViewBackground)
                    if fileTypeForMainViewBackground.text == 'fanart':
                        createFanart = False
                        break
                if createFanart:
                    element = Element('fileTypeForMainViewBackground')
                    element.text = 'fanart'
                    fileTypeFor.insert(insertAtIndex, element)

        return True, ''

    def update_208_to_214(self):

        #remove archive.vg and maws.mameworld scraper from each rom collection
        romCollectionsXml = self.tree.findall('RomCollections/RomCollection')
        for romCollectionXml in romCollectionsXml:
            #self.removeElementByAttributeValue(romCollectionXml, 'scraper', 'name', 'archive.vg')
            self.removeElement(romCollectionXml, "scraper[@name='archive.vg']")
            self.removeElement(romCollectionXml, "scraper[@name='maws.mameworld.info']")

        scraperSitesXml = self.tree.find('Scrapers')
        self.removeElement(scraperSitesXml, "Site[@name='archive.vg']")
        self.removeElement(scraperSitesXml, "Site[@name='maws.mameworld.info']")

        return True, ''

    def update_106_to_208(self):
        #update mobygames scraper
        scraperSitesXml = self.tree.findall('Scrapers/Site')
        for scraperSiteXml in scraperSitesXml:
            siteName = scraperSiteXml.attrib.get('name')
            if siteName == 'mobygames.com':
                #delete all existing scraper elements
                scraperElements = scraperSiteXml.findall('Scraper')
                for scraperElement in scraperElements:
                    self.removeElement(scraperSiteXml, 'Scraper')

                #add new scraper elements
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.01 - mobygames - gamesearch.xml',
                                            'source': 'http://www.mobygames.com/search/quick?game=%GAME%&amp;p=%PLATFORM%',
                                            'returnUrl': 'true'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.02 - mobygames - details.xml',
                                            'source': '1'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.03 - mobygames - coverlink front.xml',
                                            'source': '1',
                                            'sourceAppend': 'cover-art',
                                            'returnUrl': 'true'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.04 - mobygames - coverdetail front.xml',
                                            'source': '2'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.05 - mobygames - coverlink back.xml',
                                            'source': '1',
                                            'sourceAppend': 'cover-art',
                                            'returnUrl': 'true'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.06 - mobygames - coverdetail back.xml',
                                            'source': '3'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.07 - mobygames - coverlink media.xml',
                                            'source': '1',
                                            'sourceAppend': 'cover-art',
                                            'returnUrl': 'true'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.08 - mobygames - coverdetail media.xml',
                                            'source': '4'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.09 - mobygames - screenshotlink.xml',
                                            'source': '1',
                                            'sourceAppend': 'screenshots',
                                            'returnUrl': 'true'
                                        })
                SubElement(scraperSiteXml, 'Scraper',
                                        {
                                            'parseInstruction': '04.10 - mobygames - screenshot detail.xml',
                                            'source': '5'
                                        })

                break

        return True, ''

    def update_095_to_106(self):
        #update archive.vg scraper to API v2.0
        scraperSitesXml = self.tree.findall('Scrapers/Site')
        for scraperSiteXml in scraperSitesXml:
            siteName = scraperSiteXml.attrib.get('name')
            if siteName == 'archive.vg':
                scraperXml = scraperSiteXml.find('Scraper')
                scraperXml.attrib['source'] = "http://api.archive.vg/2.0/Archive.search/%ARCHIVEAPIKEY%/%GAME%"
                break

        return True, ''

    def update_090_to_095(self):
        #add archive scraper
        scraperSitesXml = self.tree.findall('Scrapers/Site')
        for scraperSiteXml in scraperSitesXml:
            siteName = scraperSiteXml.attrib.get('name')
            if siteName == 'archive.vg':
                return True, ''

        scrapersXml = self.tree.find('Scrapers')
        scraperSiteXml = SubElement(scrapersXml, 'Site',
                                    {
                                        'name': 'archive.vg',
                                        'descFilePerGame': 'True',
                                        'searchGameByCRC': 'False'
                                    })
        SubElement(scraperSiteXml, 'Scraper',
                                {
                                    'parseInstruction': '05.01 - archive - search.xml',
                                    'source': 'http://api.archive.vg/1.0/Archive.search/%ARCHIVEAPIKEY%/%GAME%',
                                    'encoding': 'iso-8859-1',
                                    'returnUrl': 'true'
                                })
        SubElement(scraperSiteXml, 'Scraper',
                                {
                                    'parseInstruction': '05.02 - archive - detail.xml',
                                    'source': '1',
                                    'encoding': 'iso-8859-1'
                                })

        return True, ''

    def update_0810_to_090(self):
        #change imagePlacing elements
        romCollectionsXml = self.tree.findall('RomCollections/RomCollection')
        for romCollectionXml in romCollectionsXml:
            #read value from old element
            imagePlacingValue = self.readTextElement(romCollectionXml, 'imagePlacing')
            #write with new name
            SubElement(romCollectionXml, 'imagePlacingMain').text = imagePlacingValue
            SubElement(romCollectionXml, 'imagePlacingInfo').text = imagePlacingValue

            #remove old element
            self.removeElement(romCollectionXml, 'imagePlacing')

        return True, ''

    def update_086_to_0810(self):
        #reflect changes to thegamesdb.net
        scraperSitesXml = self.tree.findall('Scrapers/Site')
        for scraperSiteXml in scraperSitesXml:
            siteName = scraperSiteXml.attrib.get('name')
            if siteName == 'thegamesdb.net':
                scraperXml = scraperSiteXml.find('Scraper')
                scraperXml.attrib['source'] = "http://thegamesdb.net/api/GetGame.php?name=%GAME%&platform=%PLATFORM%"
                break

        return True, ''

    def update_074_to_086(self):

        #update scrapers
        scraperSitesXml = self.tree.findall('Scrapers/Site')
        for scraperSiteXml in scraperSitesXml:
            siteName = scraperSiteXml.attrib.get('name')

            #handle online scrapers
            if siteName == util.localize(32154):
                scraperSiteXml.attrib['descFilePerGame'] = 'True'
                scraperSiteXml.attrib['searchGameByCRC'] = 'False'
            elif siteName == 'thegamesdb.net':
                scraperSiteXml.attrib['descFilePerGame'] = 'True'
                scraperSiteXml.attrib['searchGameByCRC'] = 'False'
            elif siteName == 'giantbomb.com':
                scraperSiteXml.attrib['descFilePerGame'] = 'True'
                scraperSiteXml.attrib['searchGameByCRC'] = 'False'
            elif siteName == 'mobygames.com':
                scraperSiteXml.attrib['descFilePerGame'] = 'True'
                scraperSiteXml.attrib['searchGameByCRC'] = 'False'

            #handle offline scrapers
            else:
                #search for rom collection that uses current scraper
                romCollectionsXml = self.tree.findall('RomCollections/RomCollection')
                for romCollectionXml in romCollectionsXml:
                    scraperXml = romCollectionXml.find('scraper')
                    scraperName = scraperXml.attrib.get('name')

                    if scraperName != siteName:
                        continue

                    descFilePerGame = self.readTextElement(romCollectionXml, 'descFilePerGame')
                    if descFilePerGame != '':
                        scraperSiteXml.attrib['descFilePerGame'] = descFilePerGame

                    searchGameByCRC = self.readTextElement(romCollectionXml, 'searchGameByCRC')
                    if searchGameByCRC != '':
                        scraperSiteXml.attrib['searchGameByCRC'] = searchGameByCRC

                    useFoldernameAsCRC = self.readTextElement(romCollectionXml, 'useFoldernameAsCRC')
                    if useFoldernameAsCRC != '':
                        scraperSiteXml.attrib['useFoldernameAsCRC'] = useFoldernameAsCRC

                    useFilenameAsCRC = self.readTextElement(romCollectionXml, 'useFilenameAsCRC')
                    if useFilenameAsCRC != '':
                        scraperSiteXml.attrib['useFilenameAsCRC'] = useFilenameAsCRC

            #remove obsolete entries from rom collections
            romCollectionsXml = self.tree.findall('RomCollections/RomCollection')
            for romCollectionXml in romCollectionsXml:
                self.removeElement(romCollectionXml, 'descFilePerGame')
                self.removeElement(romCollectionXml, 'searchGameByCRC')
                self.removeElement(romCollectionXml, 'useFoldernameAsCRC')
                self.removeElement(romCollectionXml, 'useFilenameAsCRC')
                self.removeElement(romCollectionXml, 'searchGameByCRCIgnoreRomName')

        return True, ''

    #TODO use same as in config
    def readTextElement(self, parent, elementName):
        element = parent.find(elementName)
        if element != None and element.text != None:
            Logutil.log('%s: %s' % (elementName, element.text), util.LOG_LEVEL_INFO)
            return element.text
        else:
            return ''

    def removeElement(self, parent, elementName):
        element = parent.find(elementName)
        if element != None:
            parent.remove(element)

    #TODO use configxmlwriter
    def writeFile(self, configFile):
        #write file
        try:
            self.indentXml(self.tree)
            treeToWrite = ElementTree(self.tree)
            treeToWrite.write(configFile)

            return True, ""

        except Exception as exc:
            print("Error: Cannot write config.xml: " + str(exc))
            return False, util.localize(32008) + ": " + str(exc)
