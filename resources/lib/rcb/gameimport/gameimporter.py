
import os, sys, re
import getpass, string, glob
import codecs
import time

import xbmcvfs, xbmcgui
import fnmatch

import filewalker, dbupdater, nfowriter
import resources.lib.pyscraper.pyscraper
import resources.lib.rcb.gameimport.nfowriter
from resources.lib.rcb.utils import util, romfileutil, helper

from resources.lib.rcb.utils.util import *
from resources.lib.rcb.configuration.config import *
from resources.lib.rcb.datamodel.gamedatabase import *
from resources.lib.pyscraper.descriptionparserfactory import *
from resources.lib.pyscraper.pyscraper import *
from resources.lib.rcb.gameimport.nfowriter import *
from resources.lib.rcb.gameimport import multigamescraper


class GameImporter:
	
	def __init__(self):
		Logutil.log("init GameImporter", util.LOG_LEVEL_INFO)
		pass
		
	
	def importGames(self, gdb, gui, updateOption, inConfig, romCollections, settings, isRescrape):
		self.gdb = gdb
		self.Settings = settings
			
		#self.scrapeResultsFile = self.openFile(os.path.join(util.getAddonDataPath(), 'scrapeResults.txt'))
		self.missingDescFile = self.openFile(os.path.join(util.getAddonDataPath(), 'scrapeResult_missingDesc.txt'))
		self.missingArtworkFile = self.openFile(os.path.join(util.getAddonDataPath(), 'scrapeResult_missingArtwork.txt'))
		self.possibleMismatchFile = self.openFile(os.path.join(util.getAddonDataPath(), 'scrapeResult_possibleMismatches.txt'))		
		
		Logutil.log("Start Update DB", util.LOG_LEVEL_INFO)
		
		Logutil.log("Iterating Rom Collections", util.LOG_LEVEL_INFO)
		rccount = 1
		
		#get fuzzyFactor before scraping
		matchingRatioIndex = self.Settings.getSetting(util.SETTING_RCB_FUZZYFACTOR)
		if (matchingRatioIndex == ''):
			matchingRatioIndex = 2
		Logutil.log("matchingRatioIndex: " + str(matchingRatioIndex), util.LOG_LEVEL_INFO)
		
		fuzzyFactor = util.FUZZY_FACTOR_ENUM[int(matchingRatioIndex)]
		Logutil.log("fuzzyFactor: " + str(fuzzyFactor), util.LOG_LEVEL_INFO)
		
		#always do full reimports when in rescrape-mode 
		enableFullReimport = isRescrape or self.Settings.getSetting(util.SETTING_RCB_ENABLEFULLREIMPORT).upper() == 'TRUE'
		Logutil.log("enableFullReimport: " + str(enableFullReimport), util.LOG_LEVEL_INFO)
		
		continueUpdate = True
		#Added variable to allow user to continue on errors
		ignoreErrors = False
		
		for romCollection in romCollections.values():
			
			#timestamp1 = time.clock()
			
			#check if import was canceled
			if(not continueUpdate):
				Logutil.log('Game import canceled', util.LOG_LEVEL_INFO)
				break
							
			#prepare Header for ProgressDialog
			progDialogHeader = util.localize(40022) + " (%i / %i): %s" % (rccount, len(romCollections), romCollection.name)
			rccount = rccount + 1
			
			Logutil.log("current Rom Collection: " + romCollection.name, util.LOG_LEVEL_INFO)
			
			#self.scrapeResultsFile.write('~~~~~~~~~~~~~~~~~~~~~~~~\n' +romCollection.name +'\n' +'~~~~~~~~~~~~~~~~~~~~~~~~\n')
			self.missingDescFile.write('~~~~~~~~~~~~~~~~~~~~~~~~\n' + romCollection.name + '\n' + '~~~~~~~~~~~~~~~~~~~~~~~~\n')
			self.missingArtworkFile.write('~~~~~~~~~~~~~~~~~~~~~~~~\n' + romCollection.name + '\n' + '~~~~~~~~~~~~~~~~~~~~~~~~\n')
			self.possibleMismatchFile.write('~~~~~~~~~~~~~~~~~~~~~~~~\n' + romCollection.name + '\n' + '~~~~~~~~~~~~~~~~~~~~~~~~\n')
			self.possibleMismatchFile.write('gamename, filename\n')

			#Read settings for current Rom Collection
			Logutil.log("ignoreOnScan: " + str(romCollection.ignoreOnScan), util.LOG_LEVEL_INFO)
			if(romCollection.ignoreOnScan):
				Logutil.log("current Rom Collection will be ignored.", util.LOG_LEVEL_INFO)
				#self.scrapeResultsFile.write('Rom Collection will be ignored.\n')
				continue

			Logutil.log("update is allowed for current rom collection: " + str(romCollection.allowUpdate), util.LOG_LEVEL_INFO)
			Logutil.log("max folder depth: " + str(romCollection.maxFolderDepth), util.LOG_LEVEL_INFO)
			
			firstScraper = romCollection.scraperSites[0]
			
			#check if we are in local artwork mode
			if(len(romCollection.scraperSites) == 1 and firstScraper.name == util.localize(40053)):
				Logutil.log("Forcing enableFullReimport because we are in local artwork mode", util.LOG_LEVEL_INFO)
				enableFullReimport = True
			
			files = filewalker.getRomFilesByRomCollection(self.gdb, romCollection, enableFullReimport)
			
			#itemCount is used for percentage in ProgressDialogGUI
			gui.itemCount = len(files) + 1
			
			#check if first scraper is a multigame scraper
			if(not firstScraper.descFilePerGame):
				
				#build file hash tables	(key = gamename or crc, value = romfiles)			
				Logutil.log("Start building file dict", util.LOG_LEVEL_INFO)
				fileDict = multigamescraper.buildFileDict(gui, progDialogHeader, files, romCollection, firstScraper)
									
				try:
					fileCount = 0
					gamenameFromDesc = ''
					
					#TODO move to to check preconditions
					#first scraper must be the one for multiple games					
					if(len(firstScraper.scrapers) == 0):
						Logutil.log('Configuration error: Configured scraper site does not contain any scrapers', util.LOG_LEVEL_ERROR)
						continue
											
					scraper = firstScraper.scrapers[0]
					Logutil.log("start parsing with multi game scraper: " + str(firstScraper.name), util.LOG_LEVEL_INFO)
					Logutil.log("using parser file: " + scraper.parseInstruction, util.LOG_LEVEL_INFO)
					Logutil.log("using game description: " + scraper.source, util.LOG_LEVEL_INFO)
											
					parser = DescriptionParserFactory.getParser(str(scraper.parseInstruction)) 										
					
					#parse description
					for result in parser.scanDescription(scraper.source, str(scraper.parseInstruction), scraper.encoding):
						
						try:
							gamenameFromDesc = result['Game'][0]
							
							#find parsed game in Rom Collection
							filenamelist = multigamescraper.matchDescriptionWithRomfiles(firstScraper, result, fileDict, gamenameFromDesc)
		
							artScrapers = {}
		
							if(filenamelist != None and len(filenamelist) > 0):
												
								gamenameFromFile = romfileutil.getGamenameFromFilename(filenamelist[0], romCollection)
								foldername = romfileutil.getFoldernameFromRomFilename(filenamelist[0])
								
								fileCount = fileCount + 1
								
								continueUpdate = gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + str(gamenameFromDesc), "", fileCount)
								if(not continueUpdate):				
									Logutil.log('Game import canceled by user', util.LOG_LEVEL_INFO)
									break
								
								Logutil.log('Start scraping info for game: ' + str(gamenameFromFile), LOG_LEVEL_INFO)
															
								#check if this file already exists in DB
								continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filenamelist[0], enableFullReimport, False)
								if(not continueUpdate):
									continue
								
								#use additional scrapers
								if(len(romCollection.scraperSites) > 1):
									result, artScrapers = self.useSingleScrapers(result, romCollection, 1, gamenameFromFile, foldername, filenamelist[0], fuzzyFactor, updateOption, gui, progDialogHeader, fileCount)
								
							else:
								Logutil.log("game " + gamenameFromDesc + " was found in parsed results but not in your rom collection.", util.LOG_LEVEL_WARNING)
								continue						
							
							dialogDict = {'dialogHeaderKey':progDialogHeader, 'gameNameKey':gamenameFromFile, 'scraperSiteKey':artScrapers, 'fileCountKey':fileCount}
							
							if(result == None):
								try:
									self.missingDescFile.write('%s\n' % gamenameFromFile)
								except:
									self.missingDescFile.write('%s\n' % gamenameFromFile.encode('utf-8'))
								
								ignoreGameWithoutDesc = self.Settings.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTDESC).upper() == 'TRUE'
								if(ignoreGameWithoutDesc):
									Logutil.log('No description found for game "%s". Game will not be imported.' % gamenameFromFile, util.LOG_LEVEL_WARNING)
									break
								else:
									gamename = gamenameFromFile
							else:
								gamename = dbupdater.resolveParseResult(result, 'Game')
								if(gamename != gamenameFromFile):
									try:
										self.possibleMismatchFile.write('%s, %s\n' % (gamename, gamenameFromFile))
									except:
										self.possibleMismatchFile.write('%s, %s\n' % (gamename.encode('utf-8'), gamenameFromFile.encode('utf-8')))
								if(gamename == ""):
									gamename = gamenameFromFile
									
							#TODO pub dev and other artwork
							publisher = ''
							developer = ''
							artWorkFound, artworkfiles, artworkurls = self.getArtworkForGame(romCollection, gamename, gamenameFromFile, result, gui, dialogDict, foldername, publisher, developer, False)
			
							if(not artWorkFound):
								ignoreGamesWithoutArtwork = settings.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTARTWORK).upper() == 'TRUE'
								if(ignoreGamesWithoutArtwork):								
									Logutil.log('No artwork found for game "%s". Game will not be imported.' %gamenameFromFile, util.LOG_LEVEL_WARNING)
									try:
										self.missingArtworkFile.write('--> No artwork found for game "%s". Game will not be imported.\n' %gamename)
									except:
										self.missingArtworkFile.write('--> No artwork found for game "%s". Game will not be imported.\n' %gamename.encode('utf-8'))
									return None, True
							
							gameId, continueUpdate = dbupdater.insertGameFromDesc(self.gdb, result, gamename, gamenameFromFile, romCollection, filenamelist, foldername, isUpdate, gameId, gui, False, self.Settings, artworkfiles, artworkurls, dialogDict)
							if(not continueUpdate):
								break
							
							#remove found files from file list
							if(gameId != None):
								for filename in filenamelist:
									files.remove(filename)
									
							#stop import if no files are left
							if(len(files) == 0):
								Logutil.log("All games are imported", util.LOG_LEVEL_INFO)
								break
						
						except Exception, (exc):
							Logutil.log("an error occured while adding game " + gamenameFromDesc, util.LOG_LEVEL_WARNING)
							Logutil.log("Error: " + str(exc), util.LOG_LEVEL_WARNING)
							continue
						
					#all files still available files-list, are missing entries
					for filename in files:
						gamenameFromFile = romfileutil.getGamenameFromFilename(filename, romCollection)
						try:
							self.missingDescFile.write('%s\n' % gamenameFromFile)
						except:
							self.missingDescFile.write('%s\n' % gamenameFromFile.encode('utf-8'))
							
				except Exception, (exc):
					Logutil.log("an error occured while adding game " + gamenameFromDesc, util.LOG_LEVEL_WARNING)
					Logutil.log("Error: " + str(exc), util.LOG_LEVEL_WARNING)
					try:
						self.missingDescFile.write('%s\n' % gamenameFromDesc)
					except:
						self.missingDescFile.write('%s\n' % gamenameFromDesc.encode('utf-8'))
					continue
			else:
				fileCount = 0
				successfulFiles = 0
				lastgamename = ''
				lastGameId = None
				
				for filename in files:
					
					#try:
					gamenameFromFile = ''
					gamenameFromFile = romfileutil.getGamenameFromFilename(filename, romCollection)
					
					#check if we are handling one of the additional disks of a multi rom game
					#XBOX Hack: rom files will always be named default.xbe: always detected as multi rom without this hack
					isMultiRomGame = (gamenameFromFile == lastgamename and lastgamename.lower() != 'default')
					lastgamename = gamenameFromFile
					
					if(isMultiRomGame):
						if(lastGameId == None):
							Logutil.log('Game detected as multi rom game, but lastGameId is None.', util.LOG_LEVEL_ERROR)
							continue
						#TODO: store additional rom files?
						"""
						fileType = FileType()
						fileType.id = 0
						fileType.name = "rcb_rom"
						fileType.parent = "game"
						dbupdater.insertFile(self.gdb, filename, lastGameId, fileType, None, None, None)
						"""
						continue
					
					Logutil.log('Start scraping info for game: ' + gamenameFromFile, LOG_LEVEL_INFO)						
					
					fileCount = fileCount + 1
					continueUpdate = gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, "", fileCount)
					if(not continueUpdate):				
						Logutil.log('Game import canceled by user', util.LOG_LEVEL_INFO)
						break
					
					#check if we are in local artwork mode
					isLocalArtwork = (firstScraper.name == util.localize(40053))
					
					#check if this file already exists in DB
					continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filename, enableFullReimport, isLocalArtwork)
					if(not continueUpdate):
						continue										
					
					results = {}
					foldername = romfileutil.getFoldernameFromRomFilename(filename)
					filecrc = ''
											
					artScrapers = {}
					firstRomFile = os.path.basename(filename)
					#TODO handle local artwork scraper (including developer, publisher, ...)
					if(not isLocalArtwork):
						game, continueUpdate = self.useSingleScrapersHeimdall(inConfig, romCollection, gamenameFromFile, firstRomFile, foldername, updateOption, gui, progDialogHeader, fileCount)
						#results, artScrapers = self.useSingleScrapers(results, romCollection, 0, gamenameFromFile, foldername, filename, fuzzyFactor, updateOption, gui, progDialogHeader, fileCount)
					
					if(not continueUpdate):
						Logutil.log('Error during scrape game. Game import will be stopped.', util.LOG_LEVEL_WARNING)
						break
					
					#Variables to process Art Download Info
					#dialogDict = {'dialogHeaderKey':progDialogHeader, 'gameNameKey':gamenameFromFile, 'scraperSiteKey':artScrapers, 'fileCountKey':fileCount}					
										
					if(game == None):
						if(not isLocalArtwork):
							try:
								self.missingDescFile.write('%s\n' % gamenameFromFile)
							except:
								self.missingDescFile.write('%s\n' % gamenameFromFile.encode('utf-8'))
						
						ignoreGameWithoutDesc = self.Settings.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTDESC).upper() == 'TRUE'
						if(ignoreGameWithoutDesc):
							Logutil.log('No description found for game "%s". Game will not be imported.' % gamenameFromFile, util.LOG_LEVEL_WARNING)
							continue
					else:
						if(game.name != gamenameFromFile):
							try:
								self.possibleMismatchFile.write('%s, %s\n' % (game.name, gamenameFromFile))
							except:
								self.possibleMismatchFile.write('%s, %s\n' % (game.name.encode('utf-8'), gamenameFromFile.encode('utf-8')))
						
					if(len(game.releases[0].mediaFiles) == 0):
						ignoreGamesWithoutArtwork = settings.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTARTWORK).upper() == 'TRUE'
						if(ignoreGamesWithoutArtwork):								
							Logutil.log('No artwork found for game "%s". Game will not be imported.' %gamenameFromFile, util.LOG_LEVEL_WARNING)
							try:
								self.missingArtworkFile.write('--> No artwork found for game "%s". Game will not be imported.\n' %gamename)
							except:
								self.missingArtworkFile.write('--> No artwork found for game "%s". Game will not be imported.\n' %gamename.encode('utf-8'))
							continue
								
					game.insert(self.gdb, False)
					self.gdb.commit()									
					#lastGameId, continueUpdate = dbupdater.insertGameFromDesc(self.gdb, game, gamenameFromFile, gameId, romCollection, filenamelist, foldername, isUpdate, gui, isLocalArtwork, self.Settings, artworkfiles, artworkurls)
					lastGameId = game.id
					
					"""
					if (not continueUpdate):
						break
					"""
					
					if (lastGameId != None):
						successfulFiles = successfulFiles + 1

					#check if all first 10 games have errors - Modified to allow user to continue on errors
					if (fileCount >= 10 and successfulFiles == 0 and ignoreErrors == False):
						options = []
						options.append(util.localize(40024))
						options.append(util.localize(40025))
						options.append(util.localize(40026))
						answer = xbmcgui.Dialog().select(util.localize(40027), options)
						if(answer == 1):
							ignoreErrors = True
						elif(answer == 2):
							xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(40028), util.localize(40029))
							continueUpdate = False
							break
						
					"""
					except Exception, (exc):
						Logutil.log("an error occured while adding game " + gamenameFromFile, util.LOG_LEVEL_WARNING)
						Logutil.log("Error: " + str(exc), util.LOG_LEVEL_WARNING)
						try:
							self.missingDescFile.write('%s\n' % gamenameFromFile)
						except:
							self.missingDescFile.write('%s\n' % gamenameFromFile.encode('utf-8'))
						continue
					"""
					
			#timestamp2 = time.clock()
			#diff = (timestamp2 - timestamp1) * 1000		
			#print "load %i games in %d ms" % (self.getListSize(), diff)
					
		gui.writeMsg("Done.", "", "", gui.itemCount)
		self.exit()
		return True, ''
	
	
	def checkRomfileAlreadyExists(self, filename, enableFullReimport, isLocalArtwork):
		
		isUpdate = False
		gameId = None
		
		romFile = File.getFileByNameAndType(self.gdb, filename, 0)
		if(romFile.id != None):
			isUpdate = True
			gameId = romFile.parentId
			Logutil.log('File "%s" already exists in database.' % filename, util.LOG_LEVEL_INFO)
			Logutil.log('Always rescan imported games = ' + str(enableFullReimport), util.LOG_LEVEL_INFO)
			Logutil.log('scraper == "local artwork": ' + str(isLocalArtwork), util.LOG_LEVEL_INFO)
			if(enableFullReimport == False and not isLocalArtwork):
				Logutil.log('Won\'t scrape this game again. Set "Always rescan imported games" to True to force scraping.', util.LOG_LEVEL_INFO)
				return False, isUpdate, gameId
		else:
			if(isLocalArtwork):
				Logutil.log('scraper == "local artwork": ' + str(isLocalArtwork), util.LOG_LEVEL_INFO)
				Logutil.log('Can\'t use "local artwork" scraper if game is not already imported. Use another scraper first.', util.LOG_LEVEL_INFO)
				return False, isUpdate, gameId
		
		return True, isUpdate, gameId
		
		
	def useSingleScrapersHeimdall(self, config, romCollection, gamenameFromFile, firstRomFile, foldername, updateOption, gui, progDialogHeader, fileCount):
		import gamescraper
		game = gamescraper.scrapeGame(gamenameFromFile, firstRomFile, config, romCollection, self.Settings, foldername, updateOption, gui, progDialogHeader, fileCount)
		return game
	

	def useSingleScrapers(self, result, romCollection, startIndex, gamenameFromFile, foldername, firstRomfile, fuzzyFactor, updateOption, gui, progDialogHeader, fileCount):
		
		filecrc = ''
		artScrapers = {}
				
		for i in range(startIndex, len(romCollection.scraperSites)):
			scraperSite = romCollection.scraperSites[i]
			
			gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, scraperSite.name + " - " + util.localize(40031), fileCount)
			Logutil.log('using scraper: ' + scraperSite.name, util.LOG_LEVEL_INFO)
			
			if(scraperSite.searchGameByCRC and filecrc == ''):
				filecrc = romfileutil.getFileCRC(firstRomfile)
			
			urlsFromPreviousScrapers = []
			doContinue = False
			for scraper in scraperSite.scrapers:
				pyScraper = PyScraper()
				result, urlsFromPreviousScrapers, doContinue = pyScraper.scrapeResults(result, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc, firstRomfile, fuzzyFactor, updateOption, romCollection, self.Settings)
			if(doContinue):
				continue
									
			#Find Filetypes and Scrapers for Art Download
			if(len(result) > 0):
				for path in romCollection.mediaPaths:
					thumbKey = 'Filetype' + path.fileType.name 
					if(len(dbupdater.resolveParseResult(result, thumbKey)) > 0):
						if((thumbKey in artScrapers) == 0):
							artScrapers[thumbKey] = scraperSite.name
						
		return result, artScrapers


	def openFile(self, filename):
		try:			
			filehandle = open(filename, 'w')		
		except Exception, (exc):			
			Logutil.log('Cannot write to file "%s". Error: "%s"' % (filename, str(exc)), util.LOG_LEVEL_WARNING)
			return None
		
		return filehandle
		

	def exit(self):
		
		try:
			self.missingArtworkFile.close()
			self.missingDescFile.close()
			self.possibleMismatchFile.close()
		except:
			pass
		
		Logutil.log("Update finished", util.LOG_LEVEL_INFO)
