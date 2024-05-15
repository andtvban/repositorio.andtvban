# -*- coding: utf-8 -*-
#$pyFunction
import re, requests
def GetLSProData(page_data,Cookie_Jar,m):
  list = requests.get('https://www.tdtchannels.com/lists/tvradio.m3u').text
  data = re.findall('EXTINF.*tvg-logo="([^"]+)".group-title="Andalucía".tvg-name="([^"]+)",(.*)\n(.*)',list)
  return sorted(data, key=lambda match: match[1])
