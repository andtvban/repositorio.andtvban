# -*- coding: utf-8 -*-
#$pyFunction
import re,requests,base64,shutil,random
from kodi_six import xbmc,xbmcgui,xbmcaddon,xbmcvfs
from six.moves import urllib_request
import six
def GetLSProData(page_data,Cookie_Jar,m):
    pasta = requests.get('https://gitlab.com/cristalazul1/recuperarcristal/-/raw/main/CONECTORES/Importar.entero.distandia', verify=False).text
    return six.ensure_str(pasta)
