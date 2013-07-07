
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.datamodel.gamedatabase import *
from resources.lib.rcb.gameimport import nfowriter
from resources.lib.rcb.configuration.config import *


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
        
    #read current properties for local artwork scraper
    if(not isLocalArtwork):
        publisherId = insertForeignKeyItem(gdb, gamedescription, 'Publisher', Publisher(gdb))
        developerId = insertForeignKeyItem(gdb, gamedescription, 'Developer', Developer(gdb))
    else:
        gameRow = Game(gdb).getObjectById(gameId)
        if(gameRow != None):
            publisherId = gameRow[GAME_publisherId]
            publisherRow = Publisher(gdb).getObjectById(gameId)
            if(publisherRow != None):
                publisher = publisherRow[util.ROW_NAME]              
            developerId = gameRow[GAME_developerId]
            developerRow = Developer(gdb).getObjectById(gameId)
            if(developerRow != None):
                developer = developerRow[util.ROW_NAME]
    
    region = resolveParseResult(gamedescription, 'Region')        
    media = resolveParseResult(gamedescription, 'Media')
    controller = resolveParseResult(gamedescription, 'Controller')
    players = resolveParseResult(gamedescription, 'Players')        
    rating = resolveParseResult(gamedescription, 'Rating')
    votes = resolveParseResult(gamedescription, 'Votes')
    url = resolveParseResult(gamedescription, 'URL')
    perspective = resolveParseResult(gamedescription, 'Perspective')
    originalTitle = resolveParseResult(gamedescription, 'OriginalTitle')
    alternateTitle = resolveParseResult(gamedescription, 'AlternateTitle')
    translatedBy = resolveParseResult(gamedescription, 'TranslatedBy')
    version = resolveParseResult(gamedescription, 'Version')                                
    plot = resolveParseResult(gamedescription, 'Description')
    isFavorite = resolveParseResult(gamedescription, 'IsFavorite')
    if(isFavorite == ''):
        isFavorite = '0'
    launchCount = resolveParseResult(gamedescription, 'LaunchCount')
    if(launchCount == ''):
        launchCount = '0'
    
    #create Nfo file with game properties
    createNfoFile = settings.getSetting(util.SETTING_RCB_CREATENFOFILE).upper() == 'TRUE'    
    if(createNfoFile and gamedescription != None):
        genreList = []
        try:
            genreList = gamedescription['Genre']
        except:
            pass
                    
        nfowriter.NfoWriter().createNfoFromDesc(gamename, plot, romCollection.name, publisher, developer, year, 
            players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, version, genreList, isFavorite, launchCount, romFiles[0], gamenameFromFile, artworkfiles, artworkurls)
                    
    if(not isLocalArtwork):
        gameId = insertGame(gdb, settings, gamename, plot, romCollection.id, publisherId, developerId, reviewerId, yearId, 
            players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId, romCollection.allowUpdate, )
    
        if(gameId == None):
            return None, True
                    
        for genreId in genreIds:
            genreGame = GenreGame(gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
            if(genreGame == None):
                GenreGame(gdb).insert((genreId, gameId))
            
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

    
    
def insertGame(gdb, settings, gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, 
            players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId, allowUpdate):        
    
    try:
        if(not isUpdate):
            Logutil.log("Game does not exist in database. Insert game: " +gameName, util.LOG_LEVEL_INFO)
            Game(gdb).insert((gameName, description, None, None, romCollectionId, publisherId, developerId, reviewerId, yearId, 
                players, rating, votes, url, region, media, perspective, controller, int(isFavorite), int(launchCount), originalTitle, alternateTitle, translatedBy, version))
            return gdb.cursor.lastrowid
        else:    
            if(allowUpdate):
                
                #check if we are allowed to update with null values
                allowOverwriteWithNullvalues = settings.getSetting(util.SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES).upper() == 'TRUE'
                Logutil.log("allowOverwriteWithNullvalues: " +str(allowOverwriteWithNullvalues), util.LOG_LEVEL_INFO)
                
                gameRow = None
                Logutil.log("Game does exist in database. Update game: " +gameName, util.LOG_LEVEL_INFO)
                Game(gdb).update(('name', 'description', 'romCollectionId', 'publisherId', 'developerId', 'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
                    'url', 'region', 'media', 'perspective', 'controllerType', 'originalTitle', 'alternateTitle', 'translatedBy', 'version', 'isFavorite', 'launchCount'),
                    (gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, players, rating, votes, url, region, media, perspective, controller,
                    originalTitle, alternateTitle, translatedBy, version, int(isFavorite), int(launchCount)),
                    gameId, allowOverwriteWithNullvalues)
            else:
                Logutil.log("Game does exist in database but update is not allowed for current rom collection. game: " +gameName, util.LOG_LEVEL_INFO)
            
            return gameId
    except Exception, (exc):
        Logutil.log("An error occured while adding game '%s'. Error: %s" %(gameName, str(exc)), util.LOG_LEVEL_INFO)
        return None
        
    

def insertForeignKeyItem(gdb, result, itemName, gdbObject):
    
    item = resolveParseResult(result, itemName)
                    
    if(item != "" and item != None):
        itemRow = gdbObject.getOneByName(item)
        if(itemRow == None):    
            try:
                Logutil.log(itemName +" does not exist in database. Insert: " +item, util.LOG_LEVEL_INFO)
            except:
                pass
            gdbObject.insert((item,))
            itemId = gdb.cursor.lastrowid
        else:
            itemId = itemRow[0]
    else:
        itemId = None
        
    return itemId
    

def insertForeignKeyItemList(gdb, result, itemName, gdbObject):
    idList = []                
            
    try:
        itemList = result[itemName]
        Logutil.log("Result " +itemName +" = " +str(itemList), util.LOG_LEVEL_INFO)
    except:
        Logutil.log("Error while resolving item: " +itemName, util.LOG_LEVEL_WARNING)
        return idList                
    
    for item in itemList:
        item = stripHTMLTags(item)
        
        itemRow = gdbObject.getOneByName(item)
        if(itemRow == None):
            try:
                Logutil.log(itemName +" does not exist in database. Insert: " +item, util.LOG_LEVEL_INFO)
            except:
                pass
            gdbObject.insert((item,))
            idList.append(gdb.cursor.lastrowid)
        else:
            idList.append(itemRow[0])
            
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
        
    fileRow = File(gdb).getFileByNameAndTypeAndParent(fileName, fileType.id, parentId)
    if(fileRow == None):
        Logutil.log("File does not exist in database. Insert file: " + fileName, util.LOG_LEVEL_INFO)
        File(gdb).insert((str(fileName), fileType.id, parentId))
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