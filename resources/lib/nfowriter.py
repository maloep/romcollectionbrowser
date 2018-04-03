
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

from config import *
import dialogprogress
from gamedatabase import *
from rcbxmlreaderwriter import RcbXmlReaderWriter
from util import *
import util
import xbmcvfs


class NfoWriter(RcbXmlReaderWriter):

	Settings = util.getSettings()

	def __init__(self):
		pass


	def exportLibrary(self, gdb, romCollections):
		Logutil.log("Begin exportLibrary", util.LOG_LEVEL_INFO)

		progressDialog = dialogprogress.ProgressDialogGUI()
		progressDialog.writeMsg(util.localize(32169), "", "")
		continueExport = True
		rccount = 1

		for romCollection in romCollections.values():

			progDialogRCHeader = util.localize(32170) + " (%i / %i): %s" % (rccount, len(romCollections), romCollection.name)
			rccount = rccount + 1

			Logutil.log("export Rom Collection: " + romCollection.name, util.LOG_LEVEL_INFO)
			gameCount = 1

			#get all games for this Rom Collection
			games = Game(gdb).getGamesByFilter(romCollection.id, 0, 0, 0, False, '0 = 0')
			progressDialog.itemCount = len(games) + 1

			for game in games:

				continueExport = progressDialog.writeMsg(progDialogRCHeader, util.localize(32171) + ": " + str(game.name), "", gameCount)
				if(not continueExport):
					Logutil.log('Game export canceled by user', util.LOG_LEVEL_INFO)
					break

				gameCount = gameCount + 1

				gamenameFromFile = romCollection.getGamenameFromFilename(game.firstRom)
				artworkfiles = {}
				artworkurls = []

				genreList = []
				if game.genre:
					for genre in game.genre.split(', '):
						if genre != 'None':
							genreList.append(genre)

				self.createNfoFromDesc(game.name,
									   game.plot,
									   romCollection.name,
									   game.publisher,
									   game.developer,
									   game.year,
									   game.maxplayers,
									   game.rating,
									   game.votes,
									   game.url,
									   game.region,
									   game.media,
									   game.perspective,
									   game.controllerType,
									   game.originalTitle,
									   game.alternateTitle,
									   game.version,
									   genreList,
									   game.isFavorite,
									   game.playcount,
									   game.firstRom,
									   gamenameFromFile,
									   artworkfiles,
									   artworkurls)

		progressDialog.writeMsg("", "", "", -1)
		del progressDialog


	def createNfoFromDesc(self, title, plot, platform, publisher, developer, year, maxPlayer, rating, votes,
						  detailUrl, region, media, perspective, controller, originalTitle, alternateTitle, version, genreList, isFavorite, launchCount, romFile, gameNameFromFile, artworkfiles, artworkurls):

		Logutil.log("Begin createNfoFromDesc", util.LOG_LEVEL_INFO)

		nfoFile = self.getNfoFilePath(platform, romFile, gameNameFromFile)
		if nfoFile == '':
			log.debug(u"Not writing NFO file for {0}".format(gameNameFromFile))
			return

		root = ET.Element('game')
		#reference to eventually existing nfo
		existing_nfo = None

		#Read info from existing nfo file. New info and existing info will be merged
		if xbmcvfs.exists(nfoFile):
			fh = xbmcvfs.File(nfoFile)
			existing_nfo = ET.fromstring(fh.read())
			fh.close()

		for elem in ['title', 'originalTitle', 'alternateTitle', 'platform', 'plot', 'publisher', 'developer', 'year',
					 'detailUrl', 'maxPlayer', 'region', 'media', 'perspective', 'controller', 'version', 'rating',
					 'votes', 'isFavorite', 'launchCount']:
			elemText = locals()[elem]
			#if new info is empty, check if the existing file has it
			if existing_nfo and not elemText:
				try:
					elemText = existing_nfo.find(elem).text
				except:
					pass
			ET.SubElement(root, elem).text = elemText

		#if no genre was given, use genres from existing file
		if existing_nfo and len(genreList) == 0:
			for genre in existing_nfo.findall("genre"):
				genreList.append(genre.text)

		for genre in genreList:
			ET.SubElement(root, 'genre').text = genre

		for artworktype in artworkfiles.keys():

			local = ''
			online = ''
			try:
				local = artworkfiles[artworktype][0]
				online = artworkurls[artworktype.name]
			except:
				pass

			try:
				SubElement(root, 'thumb', {'type' : artworktype.name, 'local' : local}).text = online
			except Exception, (exc):
				Logutil.log('Error writing artwork url: ' + str(exc), util.LOG_LEVEL_WARNING)
				pass

		self.writeNfoElementToFile(root, platform, romFile, gameNameFromFile, nfoFile)


	def writeNfoElementToFile(self, root, platform, romFile, gameNameFromFile, nfoFile):
		# write file
		try:
			self.indentXml(root)
			tree = ElementTree(root)

			log.info(u"Writing NFO file {0}".format(nfoFile))
			localFile = util.joinPath(util.getTempDir(), os.path.basename(nfoFile))
			tree.write(localFile, encoding="UTF-8", xml_declaration=True)
			xbmcvfs.copy(localFile, nfoFile)
			xbmcvfs.delete(localFile)

		except Exception as exc:
			log.warn(u"Error: Cannot write game nfo for {0}: {1}".format(gameNameFromFile, exc))

	def getNfoFilePath(self, romCollectionName, romFile, gameNameFromFile):
		nfoFile = ''

		nfoFolder = self.Settings.getSetting(util.SETTING_RCB_NFOFOLDER)

		if nfoFolder != '' and nfoFolder != None:
			# Add the trailing slash that xbmcvfs.exists expects
			nfoFolder = os.path.join(os.path.dirname(nfoFolder), '')
			if not xbmcvfs.exists(nfoFolder):
				Logutil.log("Path to nfoFolder does not exist: " + nfoFolder, util.LOG_LEVEL_WARNING)
			else:
				nfoFolder = os.path.join(nfoFolder, romCollectionName)
				if(not os.path.exists(nfoFolder)):
					os.mkdir(nfoFolder)

				nfoFile = os.path.join(nfoFolder, gameNameFromFile + '.nfo')

		if(nfoFile == ''):
			romDir = os.path.dirname(romFile)
			Logutil.log('Romdir: ' + romDir, util.LOG_LEVEL_INFO)
			nfoFile = os.path.join(romDir, gameNameFromFile + '.nfo')

		log.debug(u"%s returns %s for %s (%s) on platform %s" %(__name__, nfoFile, gameNameFromFile, romFile, romCollectionName))

		return nfoFile


	def getGamePropertyFromCache(self, gameRow, dict, key, index):

		result = ""
		try:
			itemRow = dict[gameRow[key]]
			result = itemRow[index]
		except:
			pass

		return result


	def getGameProperty(self, property):

		try:
			result = str(property)
		except:
			result = ""

		return result

