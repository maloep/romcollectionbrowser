import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import os
import re
import unittest
import urlparse

def comparePlatforms(platform1, platform2):
    """
    This utility function canonicalizes platforms and tests them for equality.
    """
    platform1 = re.sub("[^a-z0-9 ]", "", platform1.lower())
    platform2 = re.sub("[^a-z0-9 ]", "", platform2.lower())
    if platform1 == platform2:
        return True

    # Don't want "nintendo entertainment system" to match "super nintendo entertainment system"
    SNES = re.compile("((^|[^a-z])snes([^a-z]|$)|super nintendo)")
    if SNES.match(platform1) or SNES.match(platform2):
        return SNES.match(platform1) and SNES.match(platform2)

    NES = re.compile("((^|[^a-z])nes([^a-z]|$)|nintendo entertainment system)")
    if NES.match(platform1):
        return NES.match(platform2)
    elif NES.match(platform2):
        return NES.match(platform1)

    for company in ["microsoft", "nintendo", "sega", "sinclair", "sony"]:
        if platform1.startswith(company):
            platform1 = platform1[len(company):].strip()
        if platform2.startswith(company):
            platform2 = platform2[len(company):].strip()

    aliases = {
        "atari xe": "atari 8bit",
        "c64":      "commodore 64",
        "osx":      "max os",
        "n64":      "64", # nintendo was stripped
        "nds":      "ds",
        "ndsi":     "dsi",
        "gb":       "game boy",
        "gba":      "game boy advance",
        "gbc":      "game boy color",
        "gcn":      "gamecube",
        "ngc":      "gamecube",
        "gg":       "game gear",
        "sms":      "master system",
        "ps":       "playstation",
        "ps2":      "playstation 2",
        "ps3":      "playstation 3",
        "ps4":      "playstation 4",
        "vita":     "playstation vita",
        "psp":      "playstation portable",
        "ws":       "wonderswan",
        "wsc":      "wonderswan color",
    }
    platform1 = aliases.get(platform1, platform1)
    platform2 = aliases.get(platform2, platform2)

    # Finally, compare without spaces so that "game boy" matches "gameboy"
    return platform1.replace(" ", "") == platform2.replace(" ", "")


class ResolvePlatform(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier),
        demands.requiredClass("item"),
    ]

    supply = [
        supplies.ugpradeClass("item.game"), # NOT IMPLEMENTED YET
        supplies.emit(edamontology.data_3106), # Platform
    ]

    def run(self):
        path = urlparse.urlparse(self.subject[dc.identifier]).path
        ext = path[path.rindex(".") + 1 : ].lower() if "." in path else ""

        platform = self.subject[edamontology.data_3106]
        if(platform):
            self.subject.extendClass("item.game")
            return

        # Sources:
        # http://www.file-extensions.org/filetype/extension/name/emulator-files
        # http://justsolve.archiveteam.org/wiki/ROM_and_memory_images
        ext_to_platform = {
            "32x":    "Sega Genesis",      # Sega GENESIS ROM image file
            "64b":    "Commodore 64",      # Commodore C64 emulator file
            "64c":    "Commodore 64",      # Commodore C64 emulator file
            "a26":    "Atari 2600",        # Atari 2600 ROM image file
            "a52":    "Atari 5200",        # Atari 5200 ROM image file
            "a78":    "Atari 7800",        # Atari 5200 ROM image file
            "agb":    "Game Boy Advance",  # Nintendo Game Boy Advance ROM image
            "adf":    "Amiga",             # Amiga disk file
            "atr":    "Atari 8-bit",       # Atari 8-bit disk image
            "boxer":  "Mac",               # Boxer for Mac game archive file
            "bsx":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "c64":    "Commodore 64",      # Commodore 64 ROM image
            "cgb":    "Game Boy Color",    # Nintendo GameBoy Color emulator ROM image file
            "chd":    "Arcade",            # MAME compressed hard disk file
            "dhf":    "Amiga",             # AMIGA emulator disk image ROM file
            "dol":    "GameCube",          # Nintendo GameCube (codename "Dolphin" executable)
            "dx2":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "fam":    "NES",               # Nintendo Entertainment System Famicom emulator ROM image
            "fdi":    "Amiga",             # Amiga disk file
            "fds":    "NES",               # Nintendo Famicom (NES) disk system file
            "fig":    "Super Nintendo",    # Super Nintendo game-console ROM image
            "g64":    "Commodore 64",      # C64 emulator disk image file
            "gb":     "Game Boy",          # Nintendo Gameboy ROM image
            "gba":    "Game Boy Advance",  # Nintendo Game Boy Advance ROM image
            "gbc":    "Game Boy Color",    # Nintendo GameBoy Color emulator ROM image file
            "gcz":    "GameCube",          # Dolphin emulator archive
            "gcn":    "GameCube",
            "gd3":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "gd7":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "gen":    "Sega Genesis",
            "gg":     "GameGear",
            "ggs":    "Game Boy",          # Gameboy emulator file
            "hdf":    "ZX Spectrum",       # ZX Spectrum IDE hard drive image file
            "hdz":    "Amiga",             # Amiga hard disk image file
            "jma":    "Super Nintendo",    # Snes9x emulator ROM image
            "lnx":    "Atari Lynx",        # Atari Lynx ROM image file
            "mgt":    "ZX Spectrum",       # ZX Spectrum emulator disk image
            "md":     "Sega Genesis",
            "n64":    "Nintendo 64",       # Nintendo 64 Emulation ROM image file (wordswapped)
            "nd5":    "Nintendo DS",       # Nintendo DS game ROM file
            "nds":    "Nintendo DS",       # Nintendo DS game ROM image file
            "nes":    "NES",               # Nintendo Entertainment System ROM image
            "nez":    "NES",               # NES ROM emulator image file
            "ngc":    "Neo Geo",           # Neo Geo Pocket ROM image file
            "ngp":    "Neo Geo",
            "npc":    "Neo Geo",
            "pce":    "TurboGrafx 16",     # Mednafen PC Engine file
            "pro":    "Atari 8-bit",       # APE Atari disk image file
            "sc":     "Sega SC-3000",      # Sega SC-3000 image file
            "sf7":    "Sega SF-7000",      # Sega SF-7000 ROM file
            "sfc":    "Super Nintendo",    # Nintendo SNES9x ROM file
            "sg":     "Sega SG-1000",
            "sgb":    "Super Game Boy",    # Super Gameboy image file
            "smc":    "Super Nintendo",    # Super Nintendo game-console ROM image
            "smd":    "Sega Genesis",      # Sega Genesis ROM emulator file
            "sms":    "Sega Master System",# Sega Master System ROM emulator file
            "st":     "Atari ST",          # Atari disk image file
            "swc":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "trd":    "ZX Spectrum",       # TR-DOS ZX Spectrum floppy disk image
            "ttp":    "Atari Falcon",      # Atari Falcon application
            "u00":    "Commodore 64",      # Commodore C64 universal file
            "unif":   "NES",               # FCEU-Next emulator ROM image
            "v64":    "Nintendo 64",       # Nintento 64 emulation ROM image file (byteswapped)
            "vb":     "Virtual Boy",       # Virtual Boy image file
            "wdf":    "Wii",               # Wiimm Nintendo Wii disc file
            "whd":    "Amiga",             # WinUAEX Amiga game ROM file
            "ws":     "WonderSwan",
            "wsc":    "WonderSwan Color",
            "x64":    "Commodore 64",      # Commodore 64 emulator disk image
            "z64":    "Nintendo 64",       # Nintento 64 emulation ROM image file (native)
        }

        platform = ext_to_platform.get(ext)
        if platform:
            self.subject.extendClass("item.game")
            self.subject.emit(edamontology.data_3106, platform)

n64_regions = {
    0x00: None, # Demo games
    0x37: None, # Beta games
    0x41: "Japan / USA",
    0x44: "Germany",
    0x45: "USA",
    0x46: "France",
    0x49: "Italy",
    0x4A: "Japan",
    0x50: "Europe",
    0x53: "Spain",
    0x55: "Australia",
    0x59: "Australia",
    # Other PAL European codes
    0x58: "Europe",
    0x20: "Europe",
    0x21: "Europe",
    0x38: "Europe",
    0x70: "Europe",
}

n64_publishers = {
    "N": "Nintendo",
}

gameboy_publishers = {
    "01": "Nintendo",
    "02": "Rocket Games",
    "08": "Capcom",
    "09": "Hot B Co.",
    "0A": "Jaleco",
    "0B": "Coconuts Japan",
    "0C": "Coconuts Japan/G.X.Media",
    "0H": "Starfish",
    "0L": "Warashi Inc.",
    "0N": "Nowpro",
    "0P": "Game Village",
    "13": "Electronic Arts Japan",
    "18": "Hudson Soft Japan",
    "19": "S.C.P.",
    "1A": "Yonoman",
    "1G": "SMDE",
    "1P": "Creatures Inc.",
    "1Q": "TDK Deep Impresion",
    "20": "Destination Software",
    "22": "VR 1 Japan",
    "25": "San-X",
    "28": "Kemco Japan",
    "29": "Seta",
    "2H": "Ubisoft Japan",
    "2K": "NEC InterChannel",
    "2L": "Tam",
    "2M": "Jordan",
    "2N": "Smilesoft",
    "2Q": "Mediakite",
    "36": "Codemasters",
    "37": "GAGA Communications",
    "38": "Laguna",
    "39": "Telstar Fun and Games",
    "41": "Ubi Soft Entertainment",
    "42": "Sunsoft",
    "47": "Spectrum Holobyte",
    "49": "IREM",
    "4D": "Malibu Games",
    "4F": "Eidos/U.S. Gold",
    "4J": "Fox Interactive",
    "4K": "Time Warner Interactive",
    "4Q": "Disney",
    "4S": "Black Pearl",
    "4X": "GT Interactive",
    "4Y": "RARE",
    "4Z": "Crave Entertainment",
    "50": "Absolute Entertainment",
    "51": "Acclaim",
    "52": "Activision",
    "53": "American Sammy Corp.",
    "54": "Take 2 Interactive",
    "55": "Hi Tech",
    "56": "LJN LTD.",
    "58": "Mattel",
    "5A": "Mindscape/Red Orb Ent.",
    "5C": "Taxan",
    "5D": "Midway",
    "5F": "American Softworks",
    "5G": "Majesco Sales Inc",
    "5H": "3DO",
    "5K": "Hasbro",
    "5L": "NewKidCo",
    "5M": "Telegames",
    "5N": "Metro3D",
    "5P": "Vatical Entertainment",
    "5Q": "LEGO Media",
    "5S": "Xicat Interactive",
    "5T": "Cryo Interactive",
    "5W": "Red Storm Ent./BKN Ent.",
    "5X": "Microids",
    "5Z": "Conspiracy Entertainment Corp.",
    "60": "Titus Interactive Studios",
    "61": "Virgin Interactive",
    "62": "Maxis",
    "64": "LucasArts Entertainment",
    "67": "Ocean",
    "69": "Electronic Arts",
    "6E": "Elite Systems Ltd.",
    "6F": "Electro Brain",
    "6G": "The Learning Company",
    "6H": "BBC",
    "6J": "Software 2000",
    "6L": "BAM! Entertainment",
    "6M": "Studio 3",
    "6Q": "Classified Games",
    "6S": "TDK Mediactive",
    "6U": "DreamCatcher",
    "6V": "JoWood Productions",
    "6W": "SEGA",
    "6X": "Wannado Edition",
    "6Y": "LSP",
    "6Z": "ITE Media",
    "70": "Infogrames",
    "71": "Interplay",
    "72": "JVC Musical Industries Inc",
    "73": "Parker Brothers",
    "75": "SCI",
    "78": "THQ",
    "79": "Accolade",
    "7A": "Triffix Ent. Inc.",
    "7C": "Microprose Software",
    "7D": "Universal Interactive Studios",
    "7F": "Kemco",
    "7G": "Rage Software",
    "7H": "Encore",
    "7J": "Zoo",
    "7K": "BVM",
    "7L": "Simon & Schuster Interactive",
    "7M": "Asmik Ace Entertainment Inc./AIA",
    "7N": "Empire Interactive",
    "7Q": "Jester Interactive",
    "7T": "Scholastic",
    "7U": "Ignition Entertainment",
    "7W": "Stadlbauer",
    "80": "Misawa",
    "83": "LOZC",
    "8B": "Bulletproof Software",
    "8C": "Vic Tokai Inc.",
    "8J": "General Entertainment",
    "8N": "Success",
    "8P": "SEGA Japan",
    "91": "Chun Soft",
    "92": "Video System",
    "93": "BEC",
    "96": "Yonezawa/S'pal",
    "97": "Kaneko",
    "99": "Victor Interactive Software",
    "9A": "Nichibutsu/Nihon Bussan",
    "9B": "Tecmo",
    "9C": "Imagineer",
    "9F": "Nova",
    "9H": "Bottom Up",
    "9L": "Hasbro Japan",
    "9N": "Marvelous Entertainment",
    "9P": "Keynet Inc.",
    "9Q": "Hands-On Entertainment",
    "A0": "Telenet",
    "A1": "Hori",
    "A4": "Konami",
    "A6": "Kawada",
    "A7": "Takara",
    "A9": "Technos Japan Corp.",
    "AA": "JVC",
    "AC": "Toei Animation",
    "AD": "Toho",
    "AF": "Namco",
    "AG": "Media Rings Corporation",
    "AH": "J-Wing",
    "AK": "KID",
    "AL": "MediaFactory",
    "AP": "Infogrames Hudson",
    "AQ": "Kiratto. Ludic Inc",
    "B0": "Acclaim Japan",
    "B1": "ASCII",
    "B2": "Bandai",
    "B4": "Enix",
    "B6": "HAL Laboratory",
    "B7": "SNK",
    "B9": "Pony Canyon Hanbai",
    "BA": "Culture Brain",
    "BB": "Sunsoft",
    "BD": "Sony Imagesoft",
    "BF": "Sammy",
    "BG": "Magical",
    "BJ": "Compile",
    "BL": "MTO Inc.",
    "BN": "Sunrise Interactive",
    "BP": "Global A Entertainment",
    "BQ": "Fuuki",
    "C0": "Taito",
    "C2": "Kemco",
    "C3": "Square Soft",
    "C5": "Data East",
    "C6": "Tonkin House",
    "C8": "Koei",
    "CA": "Konami/Palcom/Ultra",
    "CB": "Vapinc/NTVIC",
    "CC": "Use Co.,Ltd.",
    "CD": "Meldac",
    "CE": "FCI/Pony Canyon",
    "CF": "Angel",
    "CM": "Konami Computer Entertainment Osaka",
    "CP": "Enterbrain",
    "D1": "Sofel",
    "D2": "Quest",
    "D3": "Sigma Enterprises",
    "D4": "Ask Kodansa",
    "D6": "Naxat",
    "D7": "Copya System",
    "D9": "Banpresto",
    "DA": "TOMY",
    "DB": "LJN Japan",
    "DD": "NCS",
    "DF": "Altron Corporation",
    "DH": "Gaps Inc.",
    "DN": "ELF",
    "E2": "Yutaka",
    "E3": "Varie",
    "E5": "Epoch",
    "E7": "Athena",
    "E8": "Asmik Ace Entertainment Inc.",
    "E9": "Natsume",
    "EA": "King Records",
    "EB": "Atlus",
    "EC": "Epic/Sony Records",
    "EE": "IGS",
    "EL": "Spike",
    "EM": "Konami Computer Entertainment Tokyo",
    "EN": "Alphadream Corporation",
    "F0": "A Wave",
    "G1": "PCCW",
    "G4": "KiKi Co Ltd",
    "G5": "Open Sesame Inc.",
    "G6": "Sims",
    "G7": "Broccoli",
    "G8": "Avex",
    "G9": "D3 Publisher",
    "GB": "Konami Computer Entertainment Japan",
    "GD": "Square-Enix",
    "HY": "Sachen",
}

class ParseGameImage(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier),
    ]

    supply = [
        supplies.emit("code"),
        supplies.emit(swo.SWO_0000397), # Publisher
        supplies.emit(edamontology.data_3106), # Platform
        supplies.emit("region"),
    ]

    def run(self):
        uri = urlparse.urlparse(self.subject[dc.identifier])
        if (uri.scheme == "" or uri.scheme == "file") and "." in uri.path and len(uri.path) >= 3:
            # Remove leading / from /C:\folder\ URIs
            # Don't use platform.system() here, because we don't want to include Cygwin
            if os.name == "nt" and uri.path[0] == "/" and uri.path[2] == ":":
                path = os.path.abspath(uri.path[1:])
            else:
                path = os.path.abspath(uri.path)

            props = None
            ext = path[path.rindex(".") + 1 : ].lower()
            if ext in ["gb", "gbc", "cgb", "sgb"]:
                props = self.parseGameboy(path)
            elif ext in ["gba", "agb"]:
                props = self.parseGameboyAdvance(path)
            elif ext in ["n64", "v64", "z64"]:
                props = self.parseNintendo64(path)

            if props:
                self.subject.emit("code", props.get("code"))
                # Include the internal title as a second code
                self.subject.emit("code", props.get("title"))
                self.subject.emit(swo.SWO_0000397, props.get("publisher"))
                self.subject.emit(edamontology.data_3106, props.get("platform"))
                self.subject.emit("region", props.get("region"))

    def sanitize(self, title):
        """
        Turn all non-ASCII characters into spaces, and then return a stripped string.
        """
        return ''.join(c if ' ' <= c and c <= '~' else ' ' for c in title).strip()

    def parseGameboy(self, filename):
        """
        Parse a Game Boy image. Valid extensions are gb, gbc, cgb, sgb. See
        RomInfo.cpp of the VBA-M project.
        http://vbam.svn.sourceforge.net/viewvc/vbam/trunk/src/win32/RomInfo.cpp?view=markup
        """
        props = {}
        data = open(filename, "rb").read(0x14b + 1)
        if len(data) >= 0x14b + 1:
            props["code"] = self.sanitize(data[0x134 : 0x134 + 15])
            if ord(data[0x143]) & 0x80:
                props["platform"] = "Game Boy Color"
            elif ord(data[0x146]) == 0x03:
                props["platform"] = "Super Game Boy"
            else:
                props["platform"] = "Game Boy"
            props["publisher"] = gameboy_publishers.get(data[0x144 : 0x144 + 2])
            # Publisher at address $14b takes precedence, if possible
            if data[0x14b] != 0x33:
                pub2 = "%02X" % ord(data[0x14b])
                props["publisher"] = gameboy_publishers.get(pub2, props["publisher"])
        return props

    def parseGameboyAdvance(self, filename):
        """
        Parse a Game Boy Advance image. Valid extensions are gba, agb. See
        RomInfo.cpp of the VBA-M project.
        """
        props = {}
        data = open(filename, "rb").read(0xb0 + 2)
        if len(data) >= 0xb0 + 2:
            props["title"] = self.sanitize(data[0xa0 : 0xa0 + 12])
            props["code"] = self.sanitize(data[0xac : 0xac + 4])
            props["publisher"] = gameboy_publishers.get(data[0xb0 : 0xb0 + 2])
        return props

    def parseNintendo64(self, filename):
        """
        Parse a Nintendo 64 image. Valid extensions are n64 (wordswapped), v64
        (byteswapped), and z64 (native). See rom.c of the Mupen64Plus project.
        https://bitbucket.org/richard42/mupen64plus-core/src/4cd70c2b5d38/src/main/rom.c
        """
        props = {}
        data = open(filename, "rb").read(64)
        if len(data) >= 64 and self.isValidN64(data):
            props["title"] = self.sanitize(data[0x20 : 0x20 + 20])
            props["code"] = self.sanitize(data[0x3c : 0x3c + 2])
            pub = data[0x38 : 0x38 + 4]
            props["publisher"] = n64_publishers.get(pub[3]) # Low byte of int
            props["region"] = n64_regions.get(ord(data[0x3e]))
        return props

    def isValidN64(self, buff):
        """
        Test if a file is a valid N64 image by checking the first 4 bytes.
        """
        # Test if image is a native .z64 image with header 0x80371240. [ABCD]
        if [ord(b) for b in buff[:4]] == [0x80, 0x37, 0x12, 0x40]:
            return True
        # Test if image is a byteswapped .v64 image with header 0x37804012. [BADC]
        if [ord(b) for b in buff[:4]] == [0x37, 0x80, 0x40, 0x12]:
            return False # TODO: Add byte-swapping
        # Test if image is a wordswapped .n64 image with header  0x40123780. [DCBA]
        if [ord(b) for b in buff[:4]] == [0x40, 0x12, 0x37, 0x80]:
            return False # TODO: Add word-swapping
        return False

class TestParseFunctions(unittest.TestCase):
    def setUp(self):
        self.subjectTask = ParseGameImage(None)

    def test_gameboy(self):
        empty = self.subjectTask.parseGameboy("test/empty")
        self.assertEqual(len(empty), 0)

        props = self.subjectTask.parseGameboy("test/Tetris.gb")
        self.assertEquals(len(props), 3)
        self.assertEquals(props["code"], "TETRIS")
        self.assertEquals(props["publisher"], gameboy_publishers.get("01"))
        self.assertEquals(props["publisher"], "Nintendo")
        self.assertEquals(props["platform"], "Game Boy")

    def test_gameboy_advance(self):
        empty = self.subjectTask.parseGameboyAdvance("test/empty")
        self.assertEqual(len(empty), 0)

        props = self.subjectTask.parseGameboyAdvance("test/Disney Princess - Royal Adventure.gba")
        self.assertEqual(len(props), 3)
        self.assertEquals(props["title"], "PRINCESSTOWN")
        self.assertEquals(props["code"], "BQNP")
        self.assertEquals(props["publisher"], gameboy_publishers.get("4Q"))
        self.assertEquals(props["publisher"], "Disney")

    def test_nintendo64(self):
        empty = self.subjectTask.parseNintendo64("test/empty")
        self.assertEqual(len(empty), 0)

        props = self.subjectTask.parseNintendo64("test/Super Smash Bros.z64")
        self.assertEqual(len(props), 4)
        self.assertEquals(props["title"], "SMASH BROTHERS")
        self.assertEquals(props["code"], "AL")
        self.assertEquals(props["publisher"], "Nintendo")
        self.assertEquals(props["region"], "USA")

module = [ ResolvePlatform, ParseGameImage ]

if __name__ == '__main__':
    unittest.main()