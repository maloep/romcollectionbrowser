from builtins import object
import xbmcgui


class ProgressDialogGUI(object):

    def __init__(self):
        self.itemCount = 0
        self.dialog = xbmcgui.DialogProgress()

    def create(self, header):
        self.dialog.create(header)

    def writeMsg(self, message, count=0):
        if not count:
            self.dialog.create(message)
        elif count > 0 and self.itemCount != 0:
            percent = int(count * (float(100) / self.itemCount))
            self.dialog.update(percent, message)
            if self.dialog.iscanceled():
                return False
            else:
                return True
        else:
            self.dialog.close()
