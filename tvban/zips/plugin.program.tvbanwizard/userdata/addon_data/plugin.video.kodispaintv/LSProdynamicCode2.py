# -*- coding: utf-8 -*-
#$pyFunction
import re,requests
def GetLSProData(page_data,Cookie_Jar,m):
  list = requests.get('https://www.tdtchannels.com/lists/tv.m3u').text
  match = re.compile('group-title="([^"]+)"').findall(list)
  seccion_list = []
  for x in match:
    if x not in seccion_list:
      seccion_list.append(x)
  return seccion_list
