# coding=utf-8

import os, sys, requests

from config import *


BASE_RESOURCE_PATH = os.path.join(os.getcwd())
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyscraper"))

env = (os.environ.get("OS", "win32"), "win32",)[ os.environ.get("OS", "win32") == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "..", "platform_libraries", env))



"""
title = 'Chuck Rock'

mobyurl = 'https://api.mobygames.com/v1/games?title=%s&platform=19&format=brief&api_key=FH9VxTkB6BGAEsF3qlnnxQ==' %title

r = requests.get(mobyurl)

print r.json()
"""
