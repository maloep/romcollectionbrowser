# coding=utf-8

import os, sys, requests

from config import *


BASE_RESOURCE_PATH = os.path.join(os.getcwd())
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyscraper"))



"""
path = '..\\language\\Swedish\\strings.xml'

import io

content = ''
with io.open(path, 'r', encoding="utf-8") as language_file:
	content = language_file.read()

with io.open(path, 'w', encoding="utf-8") as language_file:
	content = content.replace("5400", "3275")
	content = content.replace("5500", "3280")
	content = content.replace("5600", "3285")
	content = content.replace("5700", "3290")
	content = content.replace("350", "320")
	content = content.replace("400", "321")
	content = content.replace("401", "322")
	content = content.replace("450", "323")
	content = content.replace("500", "324")
	content = content.replace("510", "325")
	content = content.replace("520", "326")
	content = content.replace("530", "327")
	content = content.replace("30000", "32999")

	language_file.write(content)
"""
