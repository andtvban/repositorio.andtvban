# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://doramaflixs.one/'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Lista doramas', action = 'list_cats', url = host, search_type = 'tvshow' ))

    return itemlist


def list_cats(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<option class="level-0".*?value="(.*?)">(.*?)</option>').findall(data)

    num_matches = len(matches)

    for value, title in matches[item.page * perpage:]:
        title = title.replace('&#8211;', '').replace('&amp;', ' & ').replace('&#8217;', "'").strip()

        url = host + '?cat=' + value

        SerieName = title

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        itemlist.append(item.clone( action='list_all', url = url, title = title, cat = True,
                                    contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'}, text_color = 'moccasin' ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_cats', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    matches = re.compile('<div class="recent-item tie_video">(.*?)</p>').findall(data)

    if not matches:
        bloque = scrapertools.find_single_match(data, 'Search Results for:(.*?)<div id="categories-2"')

        matches = re.compile('<article(.*?)</article>').findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="post-box-title">.*?rel="bookmark">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(match, '<h2 class="post-box-title">.*?">(.*?)</a>').strip()

        if not url or not title: continue

        title = title.replace('&#8211;', '').replace('&amp;', ' & ').replace('&#8217;', "'").replace('&#038;', '&').strip()

        SerieName = title

        if 'Sub Español' in SerieName: SerieName = SerieName.split("Sub Español")[0]

        if 'Capitulo' in SerieName: SerieName = SerieName.split("Capitulo")[0]
        if 'Capítulo' in SerieName: SerieName = SerieName.split("Capítulo")[0]
        if 'capitulo' in SerieName: SerieName = SerieName.split("capitulo")[0]
        if 'capítulo' in SerieName: SerieName = SerieName.split("capítulo")[0]

        if 'Temporada' in SerieName: SerieName = SerieName.split("Temporada")[0]
        if 'temporada' in SerieName: SerieName = SerieName.split("temporada")[0]

        SerieName = SerieName.strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if not item.cat:
        title = 'Sin temporadas'

        if config.get_setting('channels_seasons', default=True):
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '[COLOR tan]' + title + '[/COLOR]')

    item.contentType = 'season'

    season = 1
    if '-temporada-' in item.url: season = scrapertools.find_single_match(item.url, '-temporada-(.*?)/')

    item.contentSeason = season
    itemlist = episodios(item)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    match = scrapertools.find_single_match(data, '<link rel="canonical" href="(.*?)"')

    if match:
        url = item.url

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')

        itemlist.append(item.clone( action='findvideos', url = match, title = item.title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

    if item.cat:
        matches = []
    else:
        matches = re.compile('<div class="related-item tie_video">(.*?)</p>', re.DOTALL).findall(data)

        if not matches:
            season = item.contentSeason
            if '-temporada-' in item.url: season = scrapertools.find_single_match(item.url, '-temporada-(.*?)/')

            epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)/')
            if not epis: epis = scrapertools.find_single_match(item.url, '-capitulo-(.*?)-')

            if not epis: epis = 1

            itemlist.append(item.clone( action='findvideos', url=item.url, title=item.title, contentType = 'episode', contentSeason = season, contentEpisodeNumber=epis ))

            return itemlist

    if item.page == 0 and item.perpage == 50:
        sum_parts = len(matches)

        try:
            tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
            if not tvdb_id: tvdb_id = scrapertools.find_single_match(str(item), "'tmdb_id': '(.*?)'")
        except: tvdb_id = ''

        if config.get_setting('channels_charges', default=True): item.perpage = sum_parts
        elif tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:
            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts > 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 125:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]75[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando 75 elementos[/COLOR]')
                    item.perpage = 75

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('DoramasFlixSOne', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts
                else: item.perpage = 50

    for match in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="post-box-title">.*?rel="bookmark">(.*?)</a>').strip()
        if not title: title = scrapertools.find_single_match(match, '<h3><a href=".*?">(.*?)</a>').strip()

        title = title.replace('&#8211;', '').replace('&amp;', ' & ').replace('&#8217;', "'").replace('&#038;', '&').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        epis = scrapertools.find_single_match(url, '-capitulo-(.*?)-')

        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page= item.page + 1, perpage = item.perpage, text_color='coral' ))
        else:
            next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?<a href="(.*?)"')

            if next_page:
                if '/page/'in next_page:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'episodios', page = 0, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)

    ses = 0

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    for url in matches:
        ses += 1

        if url.startswith("//"): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        other = ''
        if servidor == 'various': other = servertools.corregir_other(url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Vose', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        item.text = texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
