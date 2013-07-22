
import difflib

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.configuration import config

import xbmcgui


def matchResult(resultNames, gamenameFromFile, settings, updateOption):
        
    #get fuzzyFactor before scraping
    matchingRatioIndex = settings.getSetting(util.SETTING_RCB_FUZZYFACTOR)
    if (matchingRatioIndex == ''):
        matchingRatioIndex = 2
    Logutil.log("matchingRatioIndex: " + str(matchingRatioIndex), util.LOG_LEVEL_INFO)
    
    fuzzyFactor = util.FUZZY_FACTOR_ENUM[int(matchingRatioIndex)]
    Logutil.log("fuzzyFactor: " + str(fuzzyFactor), util.LOG_LEVEL_INFO)
        
    digits = ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    romes = ['X', 'IX', 'VIII', 'VII', 'VI', 'V', 'IV', 'III', 'II', 'I']
    
    
    if (resultNames != None and len(resultNames) >= 1):
        Logutil.log('Searching for game: ' +gamenameFromFile, util.LOG_LEVEL_INFO)
        Logutil.log('%s results found. Try to find best match.' %str(len(resultNames)), util.LOG_LEVEL_INFO)                        
        
        result, highestRatio = matchGamename(resultNames, gamenameFromFile, digits, romes, False)
        
        if(highestRatio != 1.0):
            
            #stop searching in accurate mode
            if(updateOption == util.SCRAPING_OPTION_AUTO_ACCURATE):
                Logutil.log('Ratio != 1.0 and scraping option is set to "Accurate". Result will be skipped', LOG_LEVEL_WARNING)
                return None
        
            #Ask for correct result in Interactive mode
            if(updateOption == util.SCRAPING_OPTION_INTERACTIVE):
                options = []
                options.append('Skip Game')
                options.extend(resultNames)
                    
                resultIndex = xbmcgui.Dialog().select('Search for: ' +gamenameFromFile, options)
                if(resultIndex == 0):
                    Logutil.log('No result chosen by user', util.LOG_LEVEL_INFO)
                    return None
                #-1 because of "Skip Game" entry
                resultIndex = resultIndex - 1
                selectedGame = resultNames[resultIndex]
                Logutil.log('Result chosen by user: ' +str(selectedGame), util.LOG_LEVEL_INFO)
                return resultNames[resultIndex]
            
            #check seq no in guess names mode
            seqNoIsEqual = checkSequelNoIsEqual(gamenameFromFile, result)
            if (not seqNoIsEqual):                                        
                highestRatio = 0.0
        
        if(highestRatio < fuzzyFactor):
            Logutil.log('No result found with a ratio better than %s. Try again with subtitle search.' %(str(fuzzyFactor),), LOG_LEVEL_WARNING)                
            result, highestRatio = matchGamename(resultNames, gamenameFromFile, digits, romes, True)
            #check for sequel numbers because it could be misinteroreted as subtitle
            seqNoIsEqual = checkSequelNoIsEqual(gamenameFromFile, result)
            if (not seqNoIsEqual):                    
                return None
                    
        if(highestRatio < fuzzyFactor):
            Logutil.log('No result found with a ratio better than %s. Result will be skipped.' %(str(fuzzyFactor),), LOG_LEVEL_WARNING)
            return None
                                
        Logutil.log('Using result %s' %result, util.LOG_LEVEL_INFO)
        return result
    else:
        Logutil.log('No results found with current scraper', util.LOG_LEVEL_INFO)
        return None


def matchGamename(resultNames, gamenameFromFile, digits, romes, checkSubtitle):
    
    highestRatio = 0.0
    bestIndex = 0        
    
    for i in range(0, len(resultNames)):
        resultName = resultNames[i]
        try:
            #keep it for later reference
            origSearchKey = resultName
            gamenameToCheck = gamenameFromFile
            
            Logutil.log('Comparing %s with %s' %(gamenameToCheck, resultName), util.LOG_LEVEL_INFO)
            if(compareNames(gamenameToCheck, resultName, checkSubtitle)):
                #perfect match
                return resultName, 1.0
                    
            #try again with normalized names        
            gamenameToCheck = normalizeName(gamenameToCheck)
            resultName = normalizeName(resultName)
            Logutil.log('Try normalized names. Comparing %s with %s' %(gamenameToCheck, resultName), util.LOG_LEVEL_INFO)
            if(compareNames(gamenameToCheck, resultName, checkSubtitle)):
                #perfect match
                return resultNames[i], 1.0
                        
            #try again with replaced sequel numbers        
            sequelGamename = gamenameToCheck
            sequelSearchKey = resultName
            for j in range(0, len(digits)):
                sequelGamename = sequelGamename.replace(digits[j], romes[j])
                sequelSearchKey = sequelSearchKey.replace(digits[j], romes[j])
            
            Logutil.log('Try with replaced sequel numbers. Comparing %s with %s' %(sequelGamename, sequelSearchKey), util.LOG_LEVEL_INFO)
            if(compareNames(sequelGamename, sequelSearchKey, checkSubtitle)):
                #perfect match
                return resultNames[i], 1.0
            
            #remove last char for sequel number 1 from gamename
            if(gamenameFromFile.endswith(' 1') or gamenameFromFile.endswith(' I')):
                gamenameRemovedSequel = sequelGamename[:len(sequelGamename)-1]
                Logutil.log('Try with removed sequel numbers. Comparing %s with %s' %(gamenameRemovedSequel, sequelSearchKey), util.LOG_LEVEL_INFO)
                if(compareNames(gamenameRemovedSequel, sequelSearchKey, checkSubtitle)):
                    #perfect match                                            
                    return resultNames[i], 1.0
            
            #remove last char for sequel number 1 from result (check with gamenameFromFile because we need the ' ' again)
            if(origSearchKey.endswith(' 1') or origSearchKey.endswith(' I')):
                searchKeyRemovedSequels = sequelSearchKey[:len(sequelSearchKey)-1]
                Logutil.log('Try with removed sequel numbers. Comparing %s with %s' %(sequelGamename, searchKeyRemovedSequels), util.LOG_LEVEL_INFO)
                if(compareNames(sequelGamename, searchKeyRemovedSequels, checkSubtitle)):
                    #perfect match                                            
                    return resultNames[i], 1.0
            
            
            ratio = difflib.SequenceMatcher(None, sequelGamename.upper(), sequelSearchKey.upper()).ratio()
            Logutil.log('No result found. Try to find game by ratio. Comparing %s with %s, ratio: %s' %(sequelGamename, sequelSearchKey, str(ratio)), util.LOG_LEVEL_INFO)                        
            
            if(ratio > highestRatio):
                highestRatio = ratio
                bestIndex = i
                
        except Exception, (exc):
            Logutil.log("An error occured while matching the best result: " +str(exc), util.LOG_LEVEL_WARNING)
    
    return resultNames[bestIndex], highestRatio


def compareNames(gamename, searchkey, checkSubtitle):
    if(checkSubtitle):
        if(searchkey.find(gamename) > -1):
            Logutil.log('%s is a subtitle of %s. Using result %s' %(gamename, searchkey, searchkey), util.LOG_LEVEL_INFO)
            return True
    else:
        if(gamename == searchkey):
            Logutil.log('Perfect match. Using result %s' %searchkey, util.LOG_LEVEL_INFO)
            return True
    
    return False
    
    
def normalizeName(name):

    removeChars = [', A', 'THE', ' ', '&', '-', '_', ':', '!', "'", '"', '.', ',', '#']         
    
    name = util.html_unescape(name)
    name = name.upper()
    
    for char in removeChars:
        name = name.replace(char, '')
    
    return name
    
    
def checkSequelNoIsEqual(gamenameFromFile, searchKey):
    
    Logutil.log('Check sequel numbers for "%s" and "%s".' %(gamenameFromFile, searchKey), util.LOG_LEVEL_INFO)                
    
    #first check equality of last number (also works for year sequels like Fifa 98)
    numbers = re.findall(r"\d+", gamenameFromFile)
    if(len(numbers) > 0):
        numberGamename = numbers[len(numbers)-1]
    else:
        numberGamename = '1'
    
    numbers = re.findall(r"\d+", searchKey)
    if(len(numbers) > 0):
        numberSearchkey = numbers[len(numbers)-1]
    else:
        numberSearchkey = '2'
    
    if(numberGamename == numberSearchkey):
        return True
    
    digits = [' 10', ' 9', ' 8', ' 7', ' 6', ' 5', ' 4', ' 3', ' 2', ' 1']
    romes = [' X', ' IX', ' VIII', ' VII', ' VI', ' V', ' IV', ' III', ' II', ' I']
    
    indexGamename = getSequelNoIndex(gamenameFromFile, digits, romes)        
    indexSearchKey = getSequelNoIndex(searchKey, digits, romes)        
        
    if(indexGamename == -1 and indexSearchKey == -1):
        Logutil.log('"%s" and "%s" both don\'t contain a sequel number. Skip checking sequel number match.' %(gamenameFromFile, searchKey), util.LOG_LEVEL_INFO)
        return True
    
    if((indexGamename == -1 or indexSearchKey == -1) and (indexGamename == 9 or indexSearchKey == 9)):
        Logutil.log('"%s" and "%s" seem to be sequel number 1. Skip checking sequel number match.' %(gamenameFromFile, searchKey), util.LOG_LEVEL_INFO)
        return True
    
    if(indexGamename != indexSearchKey):
        Logutil.log('Sequel number index for "%s" : "%s"' %(gamenameFromFile, str(indexGamename)), util.LOG_LEVEL_INFO)
        Logutil.log('Sequel number index for "%s" : "%s"' %(searchKey, str(indexSearchKey)), util.LOG_LEVEL_INFO)
        Logutil.log('Sequel numbers don\'t match. Result will be skipped.', util.LOG_LEVEL_INFO)
        return False
    
    return True
        
    
def getSequelNoIndex(gamename, digits, romes):        
    indexGamename = -1
    
    for i in range(0, len(digits)):    
        if(gamename.find(digits[i]) != -1):
            indexGamename = i
            break
        if(gamename.find(romes[i]) != -1):
            indexGamename = i
            break
            
    return indexGamename