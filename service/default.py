# Copyright (C) 2011 Malte Loepmann (maloep@googlemail.com)
#
# This program is free software; you can redistribute it and/or modify it under the terms 
# of the GNU General Public License as published by the Free Software Foundation; 
# either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; 
# if not, see <http://www.gnu.org/licenses/>.

import os

print 'RCB Service: Initialize'

import xbmcaddon

#get path to RCB
rcbAddon = xbmcaddon.Addon(id='script.games.rom.collection.browser')
rcbAddonPath = rcbAddon.getAddonInfo('path')

print 'RCB Service: Path to RCB = ' +str(rcbAddonPath)

#check scrape on XBMC startup setting
serviceAddon = xbmcaddon.Addon(id='service.rom.collection.browser')
scrapeOnStart = serviceAddon.getSetting('rcb_scrapOnStartUP')
print 'RCB Service: scrapeOnStart = ' +str(scrapeOnStart)

if(scrapeOnStart.lower() == 'true'):
	print 'RCB Service: Starting DB Update'
	#launch dbUpdate
	path = os.path.join(rcbAddonPath, 'dbUpLauncher.py')
	xbmc.executescript("%s" %path)
	
print 'RCB Service: Done.'