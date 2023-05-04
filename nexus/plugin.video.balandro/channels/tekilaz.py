# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://tekilaz.co/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas/estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas/tendencias/semana', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas/tendencias/dia', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_epis', url = host + 'episodios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'series/tendencias/semana', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series/tendencias/dia', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url = host[:-1]

    data = httptools.downloadpage(url).data

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        url = host[:-1] + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    if itemlist:
        if item.search_type == 'movie':
            itemlist.append(item.clone(action = 'list_all', title = 'Western', url = host + 'genero/western' ))

    return sorted(itemlist, key = lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if '<h2' in data:
        bloque = scrapertools.find_single_match(data, '<h2(.*?)Destacadas</h3>')
    elif '<h1' in data:
        bloque = scrapertools.find_single_match(data, '<h1(.*?)Destacadas</h3>')
    else:
        bloque = data

    matches = scrapertools.find_multiple_matches(bloque, '<div class="TPost(.*?)</div></li>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if url.startswith("/"): url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'srcSet="(.*?)&amp"')
        if thumb.startswith("/"): thumb = host[:-1] + thumb

        year = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.find_single_match(match, '<div class="Description"><p>(.*?)</p>')

        tipo = 'movie' if 'pelicula' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == "all":
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if not item.search_type == "all":
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="navigation pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination">.*?class="page-link current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    if next_page.startswith("/"): next_page = host[:-1] + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def last_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<h1(.*?)Destacadas</h3>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        titulo = scrapertools.find_single_match(match, 'alt="(.*?)"')

        temp_epis = scrapertools.find_single_match(match, '<span class="Year">(.*?)</span>')
        temp_epis = temp_epis.replace('<!-- -->', '').strip()

        titulo = titulo.replace(temp_epis, '').strip()

        title = titulo

        if not url or not title: continue

        if url.startswith("/"): url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, 'srcSet="(.*?)&amp"')
        if thumb.startswith("/"): thumb = host[:-1] + thumb

        titulo = temp_epis + ' ' + titulo

        epis = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                   contentType = 'episode', contentSerieName = title, contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<nav class="navigation pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination">.*?class="page-link current">.*?href="(.*?)"')

            if next_page:
                if '/page/' in next_page:
                    if next_page.startswith("/"): next_page = host[:-1] + next_page

                    itemlist.append(item.clone( title = 'Siguientes ...', action = 'last_epis', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<option value="(.*?)"')

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, page = 0, contentType = 'season', contentSeason = season ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(str(data), '{"number":' + str(item.contentSeason) + '.*?"episodes"(.*?)]}')

    matches = scrapertools.find_multiple_matches(str(bloque), '"title":"(.*?)".*?"number":(.*?),.*?"image":"(.*?)"')

    if item.page == 0:
        sum_parts = len(matches)

        try: tvdb_id = scrapertools.find_single_match(str(item), "'tvdb_id': '(.*?)'")
        except: tvdb_id = ''

        if tvdb_id:
            if sum_parts > 50:
                platformtools.dialog_notification('Tekilaz', '[COLOR cyan]Cargando Todos los elementos[/COLOR]')
                item.perpage = sum_parts
        else:

            if sum_parts >= 1000:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]500[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Tekilaz', '[COLOR cyan]Cargando 500 elementos[/COLOR]')
                    item.perpage = 500

            elif sum_parts >= 500:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Tekilaz', '[COLOR cyan]Cargando 250 elementos[/COLOR]')
                    item.perpage = 250

            elif sum_parts >= 250:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]100[/B][/COLOR] elementos ?'):
                    platformtools.dialog_notification('Tekilaz', '[COLOR cyan]Cargando 100 elementos[/COLOR]')
                    item.perpage = 100

            elif sum_parts > 50:
                if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos [COLOR cyan][B]Todos[/B][/COLOR] de una sola vez ?'):
                    platformtools.dialog_notification('Tekilaz', '[COLOR cyan]Cargando ' + str(sum_parts) + ' elementos[/COLOR]')
                    item.perpage = sum_parts

    for title, epis, thumb in matches[item.page * item.perpage:]:
        url = item.url.replace('/serie/', '/episodio/') + '-temporada-' + str(item.contentSeason) + '-episodio-' + epis

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<li class="open_submenu active actives">(.*?)</div></li>')

    ses = 0

    for match in matches:
        opts = scrapertools.find_multiple_matches(match, '</svg><div class="_(.*?)</ul>')

        for opt in opts:
            lang = scrapertools.find_single_match(opt, '<span>(.*?)<span>').strip()

            if lang == 'Subtitulado': lang = 'Vose'
            elif lang == 'Español Latino': lang = 'Lat'
            elif lang == 'Español': lang = 'Esp'
            else:
               if 'Subtitulado' in lang: lang = 'Vose'
               elif 'Español Latino' in lang: lang = 'Lat'
               elif 'Español' in lang: lang = 'Esp'

            qlty = scrapertools.find_single_match(opt, '<span>.*?<span>(.*?)</span>').strip()
            if ' - <!-- -->' in qlty: qlty = scrapertools.find_single_match(qlty, ' - <!-- -->(.*?)$')

            qlty = qlty.replace('CALIDAD', '').strip()

            links = scrapertools.find_multiple_matches(opt, 'data-tr="(.*?)".*?<span>(.*?)</span>')

            for url, srv in links:
                ses += 1

                srv = scrapertools.find_single_match(srv, '<!-- -->. <!-- -->(.*?)<!-- -->').strip()

                if srv:
                   srv = srv.lower()

                   srv = normalize_server(srv)

                   if not srv: continue

                   other = ''

                   if srv == 'drive': srv ='gvideo'
                   elif srv == 'voex': srv ='voe'
                   elif srv == 'ok-ru': srv ='okru'
                   elif srv == 'videovard': other = srv
                   elif srv == 'player' or srv == 'embed':
                      other = srv
                      srv = ''

                   itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = lang, quality = qlty,
                                         other = other.capitalize() ))

    # ~ download
    matches = scrapertools.find_multiple_matches(data, '<span class="Num">#(.*?)</td></tr>')

    for match in matches:
        ses += 1

        srv = scrapertools.find_single_match(match, '</span>(.*?)</td>').strip()
        srv = srv.replace('<!-- -->', '').strip()

        srv = normalize_server(srv)

        if not srv: continue

        if srv == '1fichier': continue

        lang = scrapertools.find_single_match(match, '<td>(.*?)</td>')

        if lang == 'Subtitulado': lang = 'Vose'
        elif lang == 'Español Latino' or lang == 'Latino': lang = 'Lat'
        elif lang == 'Español': lang = 'Esp'

        qlty = scrapertools.find_single_match(match, '<span>(.*?)</span>')

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = lang, quality = qlty, ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_server(server):
    server = servertools.corregir_servidor(server)

    if server == 'netu': server = ''
    elif server == 'powvideo': server = ''
    elif server == 'streamplay': server = ''
    elif server == 'uploadedto': server = ''

    elif server == 'jetload': server = ''
    elif server == 'vidcloud': server = ''
    elif server == 'openload': server = ''
    elif server == 'clicknupload': server = ''
    elif server == 'onlystream': server = ''
    elif server == 'rapidvideo': server = ''
    elif server == 'rapidvid': server = ''
    elif server == 'streamango': server = ''
    elif server == 'streamcherry': server = ''
    elif server == 'streamcloud': server = ''
    elif server == 'streamix': server = ''
    elif server == 'thevideo': server = ''
    elif server == 'thevid': server = ''
    elif server == 'uploadmp4': server = ''
    elif server == 'verystream': server = ''
    elif server == 'vidcloud': server = ''

    return server


def play(item):
    logger.info()
    itemlist = []

    url = item.url
    servidor = item.server

    url_final = ''

    host_player = host.replace('https://', 'https://fs.')

    if url.startswith('https://player.'):
        data = httptools.downloadpage(url).data

        url_final = scrapertools.find_single_match(data, "var url = '(.*?)'")
        if not url_final: url_final = scrapertools.find_single_match(data, 'let url = "(.*?)"')

    if not url_final:
        if item.other.lower() == 'player':
           try:
               headers = {'Referer': item.referer}
               url_player = httptools.downloadpage(url, headers = headers, only_headers = True, follow_redirects = False).headers.get('location')
               url_final = url_player + '&ver=si'
           except:
               url_final = ''

    if url_final == '':
        data = httptools.downloadpage(url).data

        value_php = scrapertools.find_single_match(data, '<input type="hidden" name="data" value="([^"]+)"')

        if '/index.php?' in data:
            index_php = scrapertools.find_single_match(data, '/index.php.*?h=(.*?)"')

            post = {'h': index_php}

            url_final = httptools.downloadpage(host_player + 'r.php', post = post).url

            if not url_final:
                data_post = httptools.downloadpage(host_player + 'api.php', post = post).data

                url_final = scrapertools.find_single_match(str(data_post), '.*?":"(.*?)"')
                url_final = url_final.replace('\/', '/')

            if url_final: value_php = ''

        if value_php:
            post = {'data': value_php}

            url_final = httptools.downloadpage(host + 'r.php', post = post).url

            if '/index.php?' in url_final:
                index_php = url_final.replace( host_player + 'index.php?h=', '')

                post = {'h': index_php}

                url_final = httptools.downloadpage(host_player + 'r.php', post = post).url

                if not url_final:
                    data_post = httptools.downloadpage(host_player + 'api.php', post = post).data

                    url_final = scrapertools.find_single_match(str(data_post), '.*?":"(.*?)"')
                    url_final = url_final.replace('\/', '/')

    if url_final:
        if item.server == 'openplay':
            url_final = url_final.replace('/openplay.openplay.vip/player.php?data=', '/player.openplay.vip/player.php?id=')
        elif item.server == 'zplayer':
            url_final = url_final + '|' + host
        elif item.other.lower() == 'player':
            servidor, url_final = get_link_player(servidor, url_final)
        elif item.other.lower() == 'embed':
            if '.mystream.' in url_final: servidor = 'mystream'

        url = url_final

    if url:
        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def get_link_player(servidor, url_final):
    referer = url_final.split('//', 1)

    data = httptools.downloadpage(url_final, headers = {'referer': referer[0] + '//' + referer[1]}).data

    url, type = scrapertools.find_single_match(data, '"file": "([^"]+)",\s+"type": "([^"]+)"')

    if type == 'mp4':
        headers = {'referer': url_final}
        url = httptools.downloadpage(url, headers = headers, only_headers=True, follow_redirects = False).headers.get("location", url)

        url_player = "%s|Referer=%s&User-Agent=%s" % (url, url_final, httptools.get_user_agent())
        servidor = 'directo'

    elif type == 'hls':
        url_player = url
        servidor = 'm3u8hls'

    else:
        url_player = url_final

    return servidor, url_player


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

