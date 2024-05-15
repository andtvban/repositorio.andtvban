# -*- coding: utf-8 -*-
#$pyFunction
def GetLSProData(page_data,Cookie_Jar,m):
 import xbmc, xbmcaddon
 addon = xbmcaddon.Addon('plugin.video.cristalazul')
 return addon.getSetting('ColoreandoPrincipal')
