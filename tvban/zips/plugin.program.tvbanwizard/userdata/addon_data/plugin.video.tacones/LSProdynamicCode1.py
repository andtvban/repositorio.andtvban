# -*- coding: utf-8 -*-
#$pyFunction
def GetLSProData(page_data, Cookie_Jar, m):
    import requests
    from xml.etree import ElementTree
    SERIES_URL = 'https://gitlab.com/stiletto1/s/-/raw/main/s'
    data = requests.get(SERIES_URL).text
    results = list()
    xml = ElementTree.fromstring(data)
    yearSeries = xml.findall("./serie/[year='2024']")
    METADATA_KEYS = ['title', 'info', 'year', 'genre', 'thumb', 'fanart']
    for serie in list(sorted(yearSeries, key=lambda serie: serie.find('title').text)):
        results.append(tuple([*[serie.find(key).text for key in METADATA_KEYS],
                            serie.get('id')]))
    return results

