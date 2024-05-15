# -*- coding: utf-8 -*-
#$pyFunction
def GetLSProData(page_data,Cookie_Jar,m):
 import xbmc, xbmcaddon
 hola = '5.1.130'
 __addon__ = xbmcaddon.Addon('script.module.resolveurl')
 __addonname__ = __addon__.getAddonInfo('version')
 if not hola==__addonname__:
    return instaladorepo()
 else:
    return '[COLOR green]SI.[/COLOR] tiene la última versión, la ' + __addonname__	  

def instaladorepo():
 import xbmc, xbmcaddon
 hola = xbmc.getCondVisibility('System.HasAddon(repository.xbmchub)')
 if hola==0:
     return '[COLOR red]NO,[/COLOR] Instale desde aquí'
 else:
     __addon__ = xbmcaddon.Addon('script.module.resolveurl')
     __addonname__ = __addon__.getAddonInfo('version')  
     return '[COLOR red]NO,[/COLOR] está en proceso... de momento tiene la ' + __addonname__ + ' si no le actualiza sólo, fuerce el repositorio de tvaddons[/COLOR]'
	
