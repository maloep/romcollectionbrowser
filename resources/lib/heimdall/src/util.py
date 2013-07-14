

def readTextElement(parent, elementName):
    element = parent.find(elementName)
    return element.text if (element != None and element.text != None) else ''