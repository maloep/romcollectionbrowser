# coding=utf-8
import sys
import os
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import xbmcaddon
from nfowriter import NfoWriter
from nfo_scraper import NFO_Scraper
from gamedatabase import GameDataBase, GameView
from config import Config, RomCollection


class Test_NFOWriter(unittest.TestCase):

    def test_getNfoFilePath(self):

        xbmcaddon._settings['rcb_nfoFolder'] = ''

        writer = NfoWriter()
        filename = writer.getNfoFilePath("Amiga", "./testdata/roms/Amiga/Airborne Ranger.adf", "Airborne Ranger")

        filename = filename.replace("\\", "/")

        self.assertEquals("./testdata/roms/Amiga/Airborne Ranger.nfo", filename)


    def test_getNfoFilePath_path_in_settings(self):

        xbmcaddon._settings['rcb_nfoFolder'] = './testdata/nfo/'

        writer = NfoWriter()
        filename = writer.getNfoFilePath("Amiga", "./testdata/roms/Amiga/Airborne Ranger.adf", "Airborne Ranger")

        filename = filename.replace("\\", "/")

        self.assertEquals("./testdata/nfo/Amiga/Airborne Ranger.nfo", filename)


    def test_createNfoFromDesc_newfile(self):
        xbmcaddon._settings['rcb_nfoFolder'] = './testdata/nfo/'

        self.assertFalse(os.path.isfile('./testdata/nfo/Amiga/Airborne Ranger.nfo'), 'nfo file should not exist')

        writer = NfoWriter()
        game_row = [None]*GameView.NUM_COLUMNS
        game_row[GameView.COL_NAME] = 'Airborne Ranger'
        game_row[GameView.COL_description] = "Description with some special characters: ' & <  >"
        game_row[GameView.COL_publisher] = '"MicroProse"'
        game_row[GameView.COL_developer] = 'Imagitec'
        game_row[GameView.COL_year] = '1989'
        game_row[GameView.COL_maxPlayers] = '1'
        game_row[GameView.COL_rating] = '3.2'
        game_row[GameView.COL_numVotes] = '128'
        game_row[GameView.COL_url] = ''
        game_row[GameView.COL_region] = 'USA'
        game_row[GameView.COL_media] = 'Floppy'
        game_row[GameView.COL_perspective] = 'Top-Down'
        game_row[GameView.COL_controllerType] = 'Joystick'
        game_row[GameView.COL_originalTitle] = 'Airborne Ranger'
        game_row[GameView.COL_alternateTitle] = 'Airborne Ranger'
        game_row[GameView.COL_version] = 'v1.00'
        game_row[GameView.COL_genre] = 'Action, Simulation'
        game_row[GameView.COL_isFavorite] = '1'
        game_row[GameView.COL_launchCount] = '1'

        writer.createNfoFromDesc(game_row, 'Amiga', './testdata/roms/Amiga/Airborne Ranger.adf', 'Airborne Ranger', {}, {})

        self.assertTrue(os.path.isfile('./testdata/nfo/Amiga/Airborne Ranger.nfo'), 'Expected nfo file to be written')

        #use nfo scraper to read the file
        scraper = NFO_Scraper()
        scraper.nfo_file = './testdata/nfo/Amiga/Airborne Ranger.nfo'

        result = scraper.retrieve(1, 'Amiga')

        self.assertEqual(["Airborne Ranger"], result['Game'])
        self.assertEqual(["Airborne Ranger"], result['OriginalTitle'])
        self.assertEqual(["Airborne Ranger"], result['AlternateTitle'])
        self.assertEqual(["1989"], result['ReleaseYear'])
        self.assertEqual(['"MicroProse"'], result['Publisher'])
        self.assertEqual(["Imagitec"], result['Developer'])
        self.assertEqual(["Top-Down"], result['Perspective'])
        self.assertEqual(["Joystick"], result['Controller'])
        self.assertEqual(["Floppy"], result['Media'])
        self.assertEqual(["USA"], result['Region'])
        self.assertEqual(["v1.00"], result['Version'])
        self.assertEqual(["1"], result['Players'])
        self.assertEqual(["1"], result['LaunchCount'])
        self.assertEqual(["1"], result['IsFavorite'])
        self.assertEqual(["3.2"], result['Rating'])
        self.assertEqual(["128"], result['Votes'])
        self.assertTrue(result['Description'][0].startswith(
            "Description with some special characters: ' & <  >"))
        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'])
        self.assertIn("Simulation", result['Genre'])

        os.remove('./testdata/nfo/Amiga/Airborne Ranger.nfo')


    def test_createNfoFromDesc_newfile_missinginfos(self):
        xbmcaddon._settings['rcb_nfoFolder'] = './testdata/nfo/'

        self.assertFalse(os.path.isfile('./testdata/nfo/Amiga/Airborne Ranger.nfo'), 'nfo file should not exist')

        writer = NfoWriter()

        game_row = [None] * GameView.NUM_COLUMNS
        game_row[GameView.COL_NAME] = 'Airborne Ranger'
        game_row[GameView.COL_description] = ''
        game_row[GameView.COL_publisher] = ''
        game_row[GameView.COL_developer] = ''
        game_row[GameView.COL_year] = ''
        game_row[GameView.COL_maxPlayers] = ''
        game_row[GameView.COL_rating] = ''
        game_row[GameView.COL_numVotes] = ''
        game_row[GameView.COL_url] = ''
        game_row[GameView.COL_region] = ''
        game_row[GameView.COL_media] = ''
        game_row[GameView.COL_perspective] = ''
        game_row[GameView.COL_controllerType] = ''
        game_row[GameView.COL_originalTitle] = ''
        game_row[GameView.COL_alternateTitle] = ''
        game_row[GameView.COL_version] = ''
        game_row[GameView.COL_genre] = ''
        game_row[GameView.COL_isFavorite] = ''
        game_row[GameView.COL_launchCount] = ''

        writer.createNfoFromDesc(game_row, 'Amiga', './testdata/roms/Amiga/Airborne Ranger.adf', 'Airborne Ranger', {}, {})

        self.assertTrue(os.path.isfile('./testdata/nfo/Amiga/Airborne Ranger.nfo'), 'Expected nfo file to be written')

        #use nfo scraper to read the file
        scraper = NFO_Scraper()
        scraper.nfo_file = './testdata/nfo/Amiga/Airborne Ranger.nfo'

        result = scraper.retrieve(1, 'Amiga')

        self.assertEqual(["Airborne Ranger"], result['Game'])
        self.assertEqual([None], result['OriginalTitle'])
        self.assertEqual([None], result['AlternateTitle'])
        self.assertEqual([None], result['ReleaseYear'])
        self.assertEqual([None], result['Publisher'])
        self.assertEqual([None], result['Developer'])
        self.assertEqual([None], result['Perspective'])
        self.assertEqual([None], result['Controller'])
        self.assertEqual([None], result['Media'])
        self.assertEqual([None], result['Region'])
        self.assertEqual([None], result['Version'])
        self.assertEqual([None], result['Players'])
        self.assertEqual([None], result['LaunchCount'])
        self.assertEqual([None], result['IsFavorite'])
        self.assertEqual([None], result['Rating'])
        self.assertEqual([None], result['Votes'])
        self.assertEqual([None], result['Description'])
        self.assertEqual(len(result['Genre']), 0)

        os.remove('./testdata/nfo/Amiga/Airborne Ranger.nfo')


    def test_createNfoFromDesc_existingfile(self):
        xbmcaddon._settings['rcb_nfoFolder'] = './testdata/nfo/'

        self.assertFalse(os.path.isfile('./testdata/nfo/Amiga/Airborne Ranger.nfo'), 'nfo file should not exist')

        shutil.copy('./testdata/nfo/Amiga/Airborne Ranger_orig.nfo', './testdata/nfo/Amiga/Airborne Ranger.nfo')

        writer = NfoWriter()

        game_row = [None] * GameView.NUM_COLUMNS
        game_row[GameView.COL_NAME] = 'Airborne Ranger'
        game_row[GameView.COL_description] = ''
        game_row[GameView.COL_publisher] = ''
        game_row[GameView.COL_developer] = ''
        game_row[GameView.COL_year] = ''
        game_row[GameView.COL_maxPlayers] = ''
        game_row[GameView.COL_rating] = ''
        game_row[GameView.COL_numVotes] = ''
        game_row[GameView.COL_url] = ''
        game_row[GameView.COL_region] = ''
        game_row[GameView.COL_media] = ''
        game_row[GameView.COL_perspective] = ''
        game_row[GameView.COL_controllerType] = ''
        game_row[GameView.COL_originalTitle] = 'Airborne Ranger'
        game_row[GameView.COL_alternateTitle] = 'Airborne Ranger'
        game_row[GameView.COL_version] = ''
        game_row[GameView.COL_genre] = ''
        game_row[GameView.COL_isFavorite] = ''
        game_row[GameView.COL_launchCount] = ''

        #missing infos should be merged with infos from existing file
        writer.createNfoFromDesc(game_row, 'Amiga', './testdata/roms/Amiga/Airborne Ranger.adf',
                                 'Airborne Ranger', {}, {})

        self.assertTrue(os.path.isfile('./testdata/nfo/Amiga/Airborne Ranger.nfo'), 'Expected nfo file to be written')

        #use nfo scraper to read the file
        scraper = NFO_Scraper()
        scraper.nfo_file = './testdata/nfo/Amiga/Airborne Ranger.nfo'

        result = scraper.retrieve(1, 'Amiga')

        self.assertEqual(["Airborne Ranger"], result['Game'])
        self.assertEqual(["Airborne Ranger"], result['OriginalTitle'])
        self.assertEqual(["Airborne Ranger"], result['AlternateTitle'])
        self.assertEqual(["1989"], result['ReleaseYear'])
        self.assertEqual(['MicroProse'], result['Publisher'])
        self.assertEqual(["Imagitec"], result['Developer'])
        self.assertEqual(["Top-Down"], result['Perspective'])
        self.assertEqual(["Joystick"], result['Controller'])
        self.assertEqual(["Floppy"], result['Media'])
        self.assertEqual(["USA"], result['Region'])
        self.assertEqual(["v1.00"], result['Version'])
        self.assertEqual(["1"], result['Players'])
        self.assertEqual(["1"], result['LaunchCount'])
        self.assertEqual(["1"], result['IsFavorite'])
        self.assertEqual(["3.2"], result['Rating'])
        self.assertEqual(["128"], result['Votes'])
        self.assertTrue(result['Description'][0].startswith(
            "Description with some special characters: ' & <  >"))
        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'])
        self.assertIn("Adventure", result['Genre'])

        os.remove('./testdata/nfo/Amiga/Airborne Ranger.nfo')


    def test_exportLibrary(self):

        export_base_folder = './testdata/nfo/export/'
        xbmcaddon._settings['rcb_nfoFolder'] = export_base_folder

        # Setup data - MyGames.db is the hard-coded expected DB name
        db_path = './testdata/database/'
        shutil.copyfile(os.path.join(db_path, 'MyGames_current_12_games.db'), os.path.join(db_path, 'MyGames.db'))
        gdb = GameDataBase(db_path)
        gdb.connect()

        # Setup config
        config_xml_file = './testdata/config/romcollections_importtests.xml'
        conf = Config(config_xml_file)
        conf.readXml()

        writer = NfoWriter()
        writer.exportLibrary(gdb, conf.romCollections)

        #check if all files have been created
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Amiga/Airborne Ranger.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Amiga/Chuck Rock.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Amiga/Eliminator.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Amiga/MicroProse Formula One Grand Prix.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Atari 2600/Adventure (1980) (Atari).nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Atari 2600/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Atari 2600/Asteroids (1981) (Atari) [no copyright].nfo')))
        #FIXME TODO: can't find file even if it exists
        #self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'Nintendo 64/1080° Snowboarding.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'PlayStation/Bushido Blade.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'PlayStation/Silent Hill.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, 'SNES/Chrono Trigger.nfo')))
        self.assertTrue(os.path.isfile(os.path.join(export_base_folder, "SNES/Madden NFL '97.nfo")))

        os.remove(os.path.join(export_base_folder, 'Amiga/Airborne Ranger.nfo'))
        os.remove(os.path.join(export_base_folder, 'Amiga/Chuck Rock.nfo'))
        os.remove(os.path.join(export_base_folder, 'Amiga/Eliminator.nfo'))
        os.remove(os.path.join(export_base_folder, 'Amiga/MicroProse Formula One Grand Prix.nfo'))
        os.remove(os.path.join(export_base_folder, 'Atari 2600/Adventure (1980) (Atari).nfo'))
        os.remove(os.path.join(export_base_folder, 'Atari 2600/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).nfo'))
        os.remove(os.path.join(export_base_folder, 'Atari 2600/Asteroids (1981) (Atari) [no copyright].nfo'))
        #FIXME TODO: can't find file even if it exists
        #os.remove(os.path.join(export_base_folder, 'Nintendo 64/1080° Snowboarding.nfo'))
        os.remove(os.path.join(export_base_folder, 'PlayStation/Bushido Blade.nfo'))
        os.remove(os.path.join(export_base_folder, 'PlayStation/Silent Hill.nfo'))
        os.remove(os.path.join(export_base_folder, 'SNES/Chrono Trigger.nfo'))
        os.remove(os.path.join(export_base_folder, "SNES/Madden NFL '97.nfo"))

        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))