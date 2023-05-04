# Conector vidcloud By Alfa development Group
# --------------------------------------------------------

import re
from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url)
    if data.code == 404:
        return False, "[Filemoon] El archivo no existe o  ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    # enc_data = scrapertools.find_single_match(data, "type='text/javascript'>(eval.*?)?\s+</script>")
    enc_data = scrapertools.find_multiple_matches(data, "type='text/javascript'>(eval.*?)?\s+</script>")
    dec_data = jsunpack.unpack(enc_data[-1])
    # sources = 'file:"([^"]+)",label:"([^"]+)"'
    sources = 'sources\:\[\{file:"([^"]+)"'
    matches = re.compile(sources, re.DOTALL).findall(dec_data)
    for url in matches:
        video_urls.append(['[Filemoon] m3u' , url])
    return video_urls
