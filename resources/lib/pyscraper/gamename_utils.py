
import re


class GameNameUtil(object):
    """This object provides methods for game name manipulations"""

    def normalize_name(self, name):
        """removes any special characters from gamenames
            removes substrings that may not be part of the name (The, A, and, ...)
            replaces roman numerals with digits
            removes trailing sequel no one
            converts to upper char
        """
        name = name.upper()

        # replace roman numerals with digits, remove trailing sequel no one (" 1" or " I")
        s = SequelNumberHandler()
        name = s.replace_roman_to_int(name)
        name = s.remove_sequel_no_one(name)

        removeSubstrings = ['A ', ', A', 'THE', ', THE', 'AND']
        for substring in removeSubstrings:
            name = name.replace(substring, '')

        # remove all non-word characters
        name = re.sub('[\W_]', '', name)

        return name

    def prepare_gamename_for_searchrequest(self, gamename):
        """Strip out subtitles, additional info and sequel numbers
        Args:
            gamename: e.g. My Game Name 2: Subtitle (1984) [cr TCS]

        Returns:
            Game name without sequel number, subtitle and additional info, e.g. My Game Name
        """
        gamename = self.strip_addinfo_from_name(gamename)
        gamename = self.strip_subtitle_from_name(gamename)

        s = SequelNumberHandler()
        index = s.get_sequel_no_index(gamename)
        #check for > 0 as we don't want to strip numbers that the gamename begins with
        if index > 0:
            gamename = gamename[:index].strip()

        return gamename

    def strip_subtitle_from_name(self, gamename):
        """Strip out subtitles
        Args:
            gamename: e.g. My Game Name: Subtitle

        Returns:
            Game name without subtitle, e.g. My Game Name
        """
        pattern = r"[^:,\-]*"  # Match anything until : , - [ or (
        return re.search(pattern, gamename).group(0).strip().replace("'", "")

    def strip_addinfo_from_name(self, gamename):
        """Strip out additional info
        Args:
            gamename: e.g. My Game Name (1984) [cr TCS]

        Returns:
            Game name without any suffix, e.g. My Game Name
        """
        pattern = r"[^[(]*"     # Match anything until : , - [ or (
        return re.search(pattern, gamename).group(0).strip().replace("'", "")


class SequelNumberHandler(object):
    """
    This object provides methods for handling sequel numbers in game names
    """

    # taken from http://code.activestate.com/recipes/81611-roman-numerals/
    numeral_map = tuple(zip((1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
        ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')))


    #regex taken from
    #https://stackoverflow.com/questions/10093618/convert-a-string-containing-a-roman-numeral-to-integer-equivalent
    regex_roman = re.compile(r'\b(?=[MDCLXVI]+\b)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b')

    regex_int = re.compile('\d+')

    def replace_roman_to_int(self, title):
        """replaces every roman numeral in title with its integer equivalent
        """
        return self.regex_roman.sub(self._roman_to_int_repl, title)

    def replace_int_to_roman(self, title):
        """replaces every integer in title with its roman numeral equivalent
        """
        return self.regex_int.sub(self._int_to_roman_repl, title)

    def get_sequel_no_index(self, title):
        """returns the index in the title that matches the first number found, either number or roman numeral.
        """
        match = re.search(self.regex_roman, title)
        if not match:
            match = re.search(self.regex_int, title)

        if match:
            return match.start()

        return -1

    def remove_sequel_no_one(self, gamename):
        """removes trailing sequel no one. "My Game 1" or "My Game I" will be converted to "My Game"
        """
        return re.sub(' [1I]$', '', gamename)

    def _int_to_roman(self, i):
        result = []
        for integer, numeral in self.numeral_map:
            count = int(i / integer)
            result.append(numeral * count)
            i -= integer * count
        return ''.join(result)

    def _roman_to_int(self, n):
        n = n.upper()

        i = result = 0
        for integer, numeral in self.numeral_map:
            while n[i:i + len(numeral)] == numeral:
                result += integer
                i += len(numeral)
        return result

    def _roman_to_int_repl(self, match):
        return str(self._roman_to_int(match.group(0)))

    def _int_to_roman_repl(self, match):
        return str(self._int_to_roman(int(match.group(0))))
