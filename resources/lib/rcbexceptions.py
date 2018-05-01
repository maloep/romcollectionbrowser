class Error(Exception):
    """Base class for other exceptions"""
    pass


class ScraperUnauthorisedException(Error):
    """Raised when the API key is unrecognised or invalid"""
    pass


class ScraperNoSearchResultsFoundException(Error):
    """Raised when no search results are found"""
    """FIXME TODO Return empty list instead of raising an exception?"""
    pass


class ScraperGameNotFoundException(Error):
    """Raised when the game could not be found by ID"""
    pass


class ScraperExceededAPIQuoteException(Error):
    """Raised when API limits exceeded"""
    pass


class ScraperWebsiteUnavailableException(Error):
    """Raised when an HTTP5xx exception is returned"""
    pass


class ScraperUnexpectedContentException(Error):
    """Raised when the response is not XML or JSON as expected"""
    pass


class ScraperUnexpectedError(Error):
    """Raised when an unexpected error occurs that doesn't match any of the other exceptions"""
    pass


class ConfigScraperSiteDoesNotExistException(Error):
    """Raised when the config file references a scraper which does not exist"""
    pass


class ConfigFileWriteException(Error):
    """ Raised when there was a problem writing to the config file """
    pass
