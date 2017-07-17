
import urllib2


class DescriptionParser(object):
	def __init__(self):
		pass

	def downloadDescription(self):
		pass

	def openFile(self):
		pass

	def getDescriptionContents(self, descFile):
		if(descFile.startswith('http')):
			req = urllib2.Request(descFile)
			req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')
			fileAsString = urllib2.urlopen(req).read()
			del req
		else:
			fh = open(str(descFile), 'r')
			fileAsString = fh.read()
			del fh

		return fileAsString
