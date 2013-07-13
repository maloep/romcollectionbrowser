
from resources.lib.rcb.utils import util
from resources.lib.rcb.datamodel.game import Game
from resources.lib.rcb.datamodel.year import Year
from resources.lib.rcb.datamodel.genre import Genre
from resources.lib.rcb.datamodel.publisher import Publisher
from resources.lib.rcb.datamodel.developer import Developer
from resources.lib.rcb.datamodel.file import File


from resources.lib.rcb.utils.util import *
from resources.lib.rcb.datamodel.gamedatabase import *
from resources.lib.rcb.gameimport import nfowriter
from resources.lib.rcb.configuration.config import *


"""
def insertGameFromDesc(gdb, gamedescription, gamename, gamenameFromFile, romCollection, romFiles, foldername, isUpdate, gameId, gui, isLocalArtwork, settings, artworkfiles, artworkurls, dialogDict=''):
    Logutil.log("insertGameFromDesc", util.LOG_LEVEL_INFO)
    
    if(gamedescription == None):
        gamedescription = {}
    
    publisher = resolveParseResult(gamedescription, 'Publisher')
    developer = resolveParseResult(gamedescription, 'Developer')
    year = resolveParseResult(gamedescription, 'ReleaseYear')
    
    yearId = insertForeignKeyItem(gdb, gamedescription, 'ReleaseYear', Year(gdb))
    genreIds = insertForeignKeyItemList(gdb, gamedescription, 'Genre', Genre(gdb))
    reviewerId = insertForeignKeyItem(gdb, gamedescription, 'Reviewer', Reviewer(gdb))
        
    publisherId = -1
    developerId = -1
        
    game = Game(gdb)
    #read current properties for local artwork scraper
    if(not isLocalArtwork):
        game.publisherId = insertForeignKeyItem(gdb, gamedescription, 'Publisher', Publisher(gdb))
        game.developerId = insertForeignKeyItem(gdb, gamedescription, 'Developer', Developer(gdb))
    else:
        game = Game(gdb).getObjectById(gameId)
        if(game != None):
            publisherId = game.publisherId
            publisher = Publisher(gdb).getObjectById(gameId)
            if(publisher != None):
                publisher = publisher.name
            developerId = game.developerId
            developer = Developer(gdb).getObjectById(gameId)
            if(developer != None):
                developer = developer.name
    
    game.name = gamename
    game.romCollectionId = romCollection.id
    game.yearId = yearId
    game.reviewerId = reviewerId
    game.region = resolveParseResult(gamedescription, 'Region')        
    game.media = resolveParseResult(gamedescription, 'Media')
    game.controllerType = resolveParseResult(gamedescription, 'Controller')
    game.maxPlayers = resolveParseResult(gamedescription, 'Players')        
    game.rating = resolveParseResult(gamedescription, 'Rating')
    game.numVotes = resolveParseResult(gamedescription, 'Votes')
    game.url = resolveParseResult(gamedescription, 'URL')
    game.perspective = resolveParseResult(gamedescription, 'Perspective')
    game.originalTitle = resolveParseResult(gamedescription, 'OriginalTitle')
    game.alternateTitle = resolveParseResult(gamedescription, 'AlternateTitle')
    game.translatedBy = resolveParseResult(gamedescription, 'TranslatedBy')
    game.version = resolveParseResult(gamedescription, 'Version')                                
    game.description = resolveParseResult(gamedescription, 'Description')
    game.isFavorite = resolveParseResult(gamedescription, 'IsFavorite')
    if(game.isFavorite == ''):
        game.isFavorite = '0'
    game.launchCount = resolveParseResult(gamedescription, 'LaunchCount')
    if(game.launchCount == ''):
        game.launchCount = '0'
    
    #create Nfo file with game properties
    createNfoFile = settings.getSetting(util.SETTING_RCB_CREATENFOFILE).upper() == 'TRUE'    
    if(createNfoFile and gamedescription != None):
        genreList = []
        try:
            genreList = gamedescription['Genre']
        except:
            pass
                    
        nfowriter.NfoWriter().createNfoFromDesc(gamename, game.description, romCollection.name, publisher, developer, year, 
            game.maxPlayers, game.rating, game.numVotes, game.url, game.region, game.media, game.perspective, game.controllerType, game.originalTitle, game.alternateTitle, game.version, genreList, game.isFavorite, game.launchCount, romFiles[0], gamenameFromFile, artworkfiles, artworkurls)
                    
    if(not isLocalArtwork):
        gameId = insertGame(gdb, settings, game, isUpdate, romCollection.allowUpdate)
    
        if(gameId == None):
            return None, True
                    
        for genreId in genreIds:
            genreGame = GenreGame(gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
            if(genreGame == None):
                genreGame = GenreGame(gdb)
                genreGame.genreId = genreId
                genreGame.gameId = gameId 
                genreGame.insert(genreGame)
            
        for romFile in romFiles:
            fileType = FileType()
            fileType.id = 0
            fileType.name = "rcb_rom"
            fileType.parent = "game"
            insertFile(gdb, romFile, gameId, fileType, None, None, None)                
    
    Logutil.log("Importing files: " +str(artworkfiles), util.LOG_LEVEL_INFO)        
    for fileType in artworkfiles.keys():
        for fileName in artworkfiles[fileType]:
            insertFile(gdb, fileName, gameId, fileType, romCollection.id, publisherId, developerId)        
            
    gdb.commit()
    return gameId, True
"""


def insertGameFromDesc(gdb, gameFromScraper, gamenameFromFile, gameId, romCollection, romFiles, foldername, isUpdate, gui, isLocalArtwork, settings, artworkfiles, artworkurls):
    Logutil.log("insertGameFromDesc", util.LOG_LEVEL_INFO)

    
    yearId = insertForeignKeyItem(gdb, gameFromScraper.yearFromScraper, Year(gdb))
    genreIds = insertForeignKeyItemList(gdb, gameFromScraper.genreFromScraper, Genre(gdb))
    reviewerId = insertForeignKeyItem(gdb, gameFromScraper.reviewerFromScraper, Reviewer(gdb))
    publisherId = insertForeignKeyItem(gdb, gameFromScraper.publisherFromScraper, Publisher(gdb))
    developerId = insertForeignKeyItem(gdb, gameFromScraper.developerFromScraper, Developer(gdb))    
                
    if(isUpdate):
        game = Game(gdb).getObjectById(gameId)
    else:
        game = Game(gdb)    
    
    game.name = gameFromScraper.name
    game.romCollectionId = romCollection.id
    game.yearId = yearId
    game.publisherId = publisherId
    game.developerId = developerId
    game.reviewerId = reviewerId
    game.region = gameFromScraper.region       
    game.media = gameFromScraper.media
    game.controllerType = gameFromScraper.controllerType
    game.maxPlayers = gameFromScraper.maxPlayers
    game.rating = gameFromScraper.rating
    game.numVotes = gameFromScraper.numVotes
    game.url = gameFromScraper.url
    game.perspective = gameFromScraper.perspective
    game.originalTitle = gameFromScraper.originalTitle
    game.alternateTitle = gameFromScraper.alternateTitle
    game.translatedBy = gameFromScraper.translatedBy
    game.version = gameFromScraper.version
    game.description = gameFromScraper.description
    game.isFavorite = gameFromScraper.isFavorite
    if(game.isFavorite == ''):
        game.isFavorite = '0'
    game.launchCount = gameFromScraper.launchCount
    if(game.launchCount == ''):
        game.launchCount = '0'
    
    #create Nfo file with game properties
    createNfoFile = settings.getSetting(util.SETTING_RCB_CREATENFOFILE).upper() == 'TRUE'    
    if(createNfoFile):
        genreList = []
        try:
            genreList = game.genreFromScraper
        except:
            pass
                    
        nfowriter.NfoWriter().createNfoFromDesc(game.name, game.description, romCollection.name, game.publisherFromScraper, game.developerFromScraper, game.yearFromScraper, 
            game.maxPlayers, game.rating, game.numVotes, game.url, game.region, game.media, game.perspective, game.controllerType, game.originalTitle, game.alternateTitle, game.version, genreList, game.isFavorite, game.launchCount, romFiles[0], gamenameFromFile, artworkfiles, artworkurls)
                    
    if(not isLocalArtwork):
        gameId = insertGame(gdb, settings, game, isUpdate, romCollection.allowUpdate)
    
        if(gameId == None):
            return None, True
                    
        for genreId in genreIds:
            genreGame = GenreGame(gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
            if(genreGame == None):
                genreGame = GenreGame(gdb)
                genreGame.genreId = genreId
                genreGame.gameId = gameId 
                genreGame.insert(genreGame)
            
        for romFile in romFiles:
            fileType = FileType()
            fileType.id = 0
            fileType.name = "rcb_rom"
            fileType.parent = "game"
            insertFile(gdb, romFile, gameId, fileType, None, None, None)                
    
    Logutil.log("Importing files: " +str(artworkfiles), util.LOG_LEVEL_INFO)        
    for fileType in artworkfiles.keys():
        for fileName in artworkfiles[fileType]:
            insertFile(gdb, fileName, gameId, fileType, romCollection.id, publisherId, developerId)        
            
    gdb.commit()
    return gameId, True

    
    
def insertGame(gdb, settings, game, isUpdate, allowUpdate):        
    
    try:
        if(not isUpdate):
            Logutil.log("Game does not exist in database. Insert game: " +game.name, util.LOG_LEVEL_INFO)
            game.insert(game)
            return gdb.cursor.lastrowid
        else:    
            if(allowUpdate):
                
                #check if we are allowed to update with null values
                allowOverwriteWithNullvalues = settings.getSetting(util.SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES).upper() == 'TRUE'
                Logutil.log("allowOverwriteWithNullvalues: " +str(allowOverwriteWithNullvalues), util.LOG_LEVEL_INFO)
                                
                Logutil.log("Game does exist in database. Update game: " +game.name, util.LOG_LEVEL_INFO)
                game.updateAllColumns(game, allowOverwriteWithNullvalues)
            else:
                Logutil.log("Game does exist in database but update is not allowed for current rom collection. game: " +game.name, util.LOG_LEVEL_INFO)
            
            return game.id
    except Exception, (exc):
        Logutil.log("An error occured while adding game '%s'. Error: %s" %(game.name, str(exc)), util.LOG_LEVEL_INFO)
        return None
        
    

def insertForeignKeyItem(gdb, item, gdbObject):
                    
    if(item != "" and item != None):
        obj = gdbObject.getOneByName(item)
        if(obj == None):    
            try:
                Logutil.log("%s does not exist in database. Will insert now." %item, util.LOG_LEVEL_INFO)
            except:
                pass
            gdbObject.name = item
            gdbObject.insert(gdbObject)
            itemId = gdb.cursor.lastrowid
        else:
            itemId = obj.id
    else:
        itemId = None
        
    return itemId
    

def insertForeignKeyItemList(gdb, itemList, gdbObject):
    
    idList = []
    
    for item in itemList:
        item = stripHTMLTags(item)
        
        obj = gdbObject.getOneByName(item)
        if(obj == None):
            try:
                Logutil.log("%s does not exist in database. Will insert now." %item, util.LOG_LEVEL_INFO)
            except:
                pass
            gdbObject.name = item
            gdbObject.insert(gdbObject)
            idList.append(gdb.cursor.lastrowid)
        else:
            idList.append(obj.id)
            
    return idList


def insertFile(gdb, fileName, gameId, fileType, romCollectionId, publisherId, developerId):
    Logutil.log("Begin Insert file: " + fileName, util.LOG_LEVEL_DEBUG)                                        
    
    parentId = None
    
    #TODO console and romcollection could be done only once per RomCollection            
    #fileTypeRow[3] = parent
    if(fileType.parent == 'game'):
        Logutil.log("Insert file with parent game", util.LOG_LEVEL_INFO)
        parentId = gameId
    elif(fileType.parent == 'romcollection'):
        Logutil.log("Insert file with parent romcollection.", util.LOG_LEVEL_INFO)
        parentId = romCollectionId        
    elif(fileType.parent == 'publisher'):
        Logutil.log("Insert file with parent publisher", util.LOG_LEVEL_INFO)
        parentId = publisherId
    elif(fileType.parent == 'developer'):
        Logutil.log("Insert file with parent developer", util.LOG_LEVEL_INFO)
        parentId = developerId
                
    Logutil.log("Insert file with parentid: " + str(parentId), util.LOG_LEVEL_INFO)
        
    file = File(gdb).getFileByNameAndTypeAndParent(fileName, fileType.id, parentId)
    if(file == None):
        Logutil.log("File does not exist in database. Insert file: " + fileName, util.LOG_LEVEL_INFO)
        file = File(gdb)
        file.name = fileName
        file.fileTypeId = fileType.id
        file.parentId = parentId
        file.insert(file)
    else:
        Logutil.log("File already exists in database: " + fileName, util.LOG_LEVEL_INFO)


def resolveParseResult(result, itemName):
        
    resultValue = ""
    
    try:            
        resultValue = result[itemName][0]
        
        if(itemName == 'ReleaseYear' and resultValue != None):
            if(type(resultValue) is time.struct_time):
                resultValue = str(resultValue[0])
            elif(len(resultValue) > 4):
                resultValueOrig = resultValue
                resultValue = resultValue[0:4]
                try:
                    #year must be numeric
                    int(resultValue)
                except:
                    resultValue = resultValueOrig[len(resultValueOrig) -4:]
                    try:
                        int(resultValue)
                    except:
                        resultValue = ''
                        
        #replace and remove HTML tags
        resultValue = stripHTMLTags(resultValue)
        resultValue = resultValue.strip()
                                
    except Exception, (exc):
        Logutil.log("Error while resolving item: " +itemName +" : " +str(exc), util.LOG_LEVEL_WARNING)
                    
    try:
        Logutil.log("Result " +itemName +" = " +resultValue, util.LOG_LEVEL_DEBUG)
    except:
        pass
            
    return resultValue


def stripHTMLTags(inputString):
            
    inputString = util.html_unescape(inputString)
    
    #remove html tags and double spaces
    intag = [False]
    lastSpace = [False]
    def chk(c):
        if intag[0]:
            intag[0] = (c != '>')
            lastSpace[0] = (c == ' ')
            return False
        elif c == '<':
            intag[0] = True
            lastSpace[0] = (c == ' ')
            return False
        if(c == ' ' and lastSpace[0]):
            lastSpace[0] = (c == ' ')
            return False
        lastSpace[0] = (c == ' ')
        return True
    
    return ''.join(c for c in inputString if chk(c))