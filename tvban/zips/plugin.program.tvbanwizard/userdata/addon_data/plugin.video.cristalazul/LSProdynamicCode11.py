# -*- coding: utf-8 -*-
#$pyFunction
def GetLSProData(page_data,Cookie_Jar,m):
 import xbmc, xbmcaddon
 hola = xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)')
 if hola==0:
     xbmc.executebuiltin('InstallAddon(inputstream.adaptive)')
     return '[COLOR red]NO, le recomendamos que lo instale. Si no lo instala, No le funcionara ni la sección de ANDROID 10 ni la de DOCUMENTALES. Vamos a forzar la instalación.[/COLOR]'
 else:
     __addon__ = xbmcaddon.Addon('inputstream.adaptive')
     __addonname__ = __addon__.getAddonInfo('version') 
     return '[COLOR green]SI.[/COLOR] [COLOR white]version instalada ' + __addonname__ + '[/COLOR]'

