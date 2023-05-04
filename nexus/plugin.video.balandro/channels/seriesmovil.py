# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesmovil.top/'


def item_configurar_proxies(item):
    color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')

    color_avis = config.get_setting('notification_avis_color', default='yellow')
    color_exec = config.get_setting('notification_exec_color', default='cyan')

    context = []

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    if config.get_setting('channel_seriesmovil_proxies', default=''):
        tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': item.channel, 'action': 'quitar_proxies'})

    tit = '[COLOR %s]Ajustes categoría proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, context=context, plot=plot, text_color='red' )

def quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if not headers: headers = {'Referer': host}

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('seriesmovil', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    if '<title>You are being redirected...</title>' in data or '<title>Just a moment...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
                data = httptools.downloadpage_proxy('seriesmovil', url, post=post, headers=headers, raise_weberror=raise_weberror).data
        except:
            pass

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    generos = [
       'action-adventure',
       'ciencia-ficcion',
       'comedia',
       'crimen',
       'drama',
       'familia',
       'misterio',
       'sci-fi-fantasy',
       'war-politics'
       ]

    for genero in generos:
        url = host + 'category/' + genero + '/'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        if thumb.startswith('/'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(match, '<span class="Date">(.*?)</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year } ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="nav-links">' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, ' <main>(.*?)<section>')

    seasons = scrapertools.find_multiple_matches(bloque, '<div class="Title">.*?<a href="(.*?)".*?>Temporada.*?<span>(.*?)</span>')

    for url, tempo in seasons:
        title = 'Temporada ' + tempo

        if len(seasons) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, page = 0, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    patron = '<td><span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl">.*?>(.*?)</a>'

    episodes = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0:
        sum_parts = len(episodes)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('SeriesMovil', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for epis, url, thumb, title, in episodes[item.page * item.perpage:]:
        if thumb.startswith('//'): thumb = 'https:' + thumb

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'castellano': 'Esp', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div id="VideoOption(.*?)".*?<iframe src="(.*?)"')

    ses = 0

    for opt, url in matches:
        ses += 1

        if url:
            lang = scrapertools.find_single_match(data, '<span class="nmopt">' + opt + '</span>.*?<span>(.*?)<span>').strip().lower()

            qlty = scrapertools.find_single_match(data, '<span class="nmopt">' + opt + '</span>.*?<span>.*?<span>(.*?)</span>').strip()
            qlty = scrapertools.find_single_match(qlty, '(.*?) •').strip()

            other = scrapertools.find_single_match(data, '<span class="nmopt">' + opt + '</span>.*?<span>.*?<span>(.*?)</span>').strip()
            other = scrapertools.find_single_match(other, ' • (.*?)$').strip().lower()

            if 'hqq' in other or 'waaw' in other or 'netu' in other: continue

            elif 'openload' in other: continue
            elif 'powvideo' in other: continue
            elif 'streamplay' in other: continue
            elif 'rapidvideo' in other: continue
            elif 'streamango' in other: continue
            elif 'verystream' in other: continue
            elif 'vidtodo' in other: continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url,
                                                          language = IDIOMAS.get(lang, lang), quality = qlty, other = other.capitalize() ))

    # ~ Descargas
    bloque = scrapertools.find_single_match(data, '<div class="OptionBx on">(.*?)</section>')

    patron = '<div class="Optntl">Opción.*?<p class="AAIco-language">(.*?)</p>.*?<p class="AAIco-dns">(.*?)</p>.*?<p class="AAIco-equalizer">(.*?)</p>.*?href="(.*?)"'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for lang, srv, qllty, url in matches:
        ses += 1

        lang = lang.lower()

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url,
                                                     language = IDIOMAS.get(lang, lang), quality = qlty, other = srv  + ' d' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if '?trdownload=' in url:
        # ~ new_url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
        new_url = httptools.downloadpage_proxy('seriesmovil', url, follow_redirects=False).headers.get('location', '')
    else:
        data = do_downloadpage(url)

        new_url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, '<iframe src="(.*?)"')
 
    if new_url: url = new_url

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

