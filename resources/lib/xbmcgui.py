
#Dummy module to satisfy the required import in dbupdate

class WindowXMLDialog:
    def __init__(self):
        pass

class WindowXML:
    def __init__(self):
        pass

class DialogProgress:
    def __init__(self):
        pass

    def create(self, line):
        print "{0}".format (line)

    def update(self, pct, line1, line2, line3):
        print "{0} - {1}\n{2}\n{3}".format (pct, line1, line2, line3)

    def iscanceled(self):
        return False