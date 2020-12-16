#-*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import requests
import json
import urlparse
import urllib
from bs4 import BeautifulSoup

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'videos')
reload(sys)
sys.setdefaultencoding('utf-8')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def top_video():
    a = requests.get(url='https://tv.naver.com/r/').text
    soup = BeautifulSoup(a, 'html.parser')
    side = soup.find('div', {'class': 'top100'})
    for tag0 in side.find_all('dt', {'class': 'title'}):
        for tag1 in tag0.find_all('a'):
            link = tag1['href']
            key = rdkey(link)[0]
            id = rdkey(link)[1]
            play = play_video(id, key)
            title = rdkey(link)[2]
            thumb = rdkey(link)[3]

            listset(title, thumb, play, False)

def now_video():
    a = requests.get(url='https://tv.naver.com/i/').text
    soup = BeautifulSoup(a, 'html.parser')
    for tag0 in soup.find_all('dt', {'class': 'title'}):
        for tag1 in tag0.find_all('a'):
            link = tag1['href']
            key = rdkey(link)[0]
            id = rdkey(link)[1]
            play = play_video(id, key)
            title = rdkey(link)[2]
            thumb = rdkey(link)[3]

            listset(title, thumb, play, False)

def live_video():
    main = 'https://tv.naver.com/l/livehome'
    mainreq = requests.get(url=main).text
    soup = BeautifulSoup(mainreq, 'html.parser')
    mnlst = soup.find('ul', {'class': 'item_list type2'})

    for lll in mnlst.find_all('li'):

        if lll.find_all('a')[0]['href'] == 'javascript:;':
            title = lll.find_all('img')[0]['alt']
            thumb = lll.find_all('img')[0]['src']
            sport = lll.find_all('a')[0]['onclick'].replace('tvcast.pc.LivePopup.popup(', '').replace("'", '').replace(');', '').replace('\n', '')
            listset(title, thumb, sport, False)
        else:
            ll = lll.find_all('a')[0]['href'][:3]

            if ll == '/v/':
                vod = 'https://tv.naver.com' + lll.find_all('a')[0]['href']
                key = rdkey(vod)[0]
                id = rdkey(vod)[1]
                vdtit = rdkey(vod)[2]
                vdth =rdkey(vod)[3]
                vdpy = play_video(id, key)
                listset(vdtit, vdth, vdpy, False)

            else:
                live = lll.find_all('a')[0]['href']
                lvtit = lll.find_all('img')[0]['alt']
                lvth = lll.find_all('img')[0]['src']
                lvpy = live_play(live)
                listset(lvtit, lvth, lvpy, False)


def live_play(link):
    lvurl = link
    lvreq = requests.get(url=lvurl).text
    lvsoup = BeautifulSoup(lvreq, 'html.parser')
    chid = lvsoup.find_all('script', {'type': 'text/javascript'})[12]
    for w in chid:
        lvst = w.find('sApiF')
        lved = w.find('channelId:')
        llvurl = w[lvst:lved].replace("sApiF: '", '').replace("'", '').replace('\n', '').replace(' ', '').replace(',', '')
        req = requests.get(url=llvurl).json()
        stream = req['streams']
        if stream[0]['qualityId'] == '1080':
            play = stream[0]['url']

        elif stream[1]['qualityId'] == '720':
            play = stream[1]['url']

        elif stream[2]['qualityId'] == '480':
            play = stream[2]['url']

        elif stream[3]['qualityId'] == '360':
            play = stream[3]['url']

        elif stream[4]['qualityId'] == '270':
            play = stream[4]['url']

        elif stream[5]['qualityId'] == 'abr':
            play = stream[5]['url']

    return play

def rdkey(link):
    url = link
    a = requests.get(url=url).text
    soup = BeautifulSoup(a, 'html.parser')
    script = soup.find_all('script', {'type': 'text/javascript'})[15]
    for a in script:
        start = a.find('inKey')
        end = a.find('rmcSid')
        keys = a[start:end]
        key = keys.replace('inKey" : ', '').replace('"', '').replace(',', '').replace('\n', '').rstrip()

        start1 = a.find('videoId')
        ids = a[start1:start]
        id = ids.replace('videoId" : ', '').replace('"', '').replace(',', '')

        start2 = a.find('title')
        end1 = a.find('thumbnail')
        titles = a[start2:end1]
        try:
            title = titles.replace('title: jQuery(new DOMParser().parseFromString("', '').replace(" 'text/html')).find('body').text()", '').replace('"', '').replace(',', '').replace(' ', '').replace('\n', '').rstrip().encode().decode('unicode_escape')
        except:
            title = titles.replace('title: jQuery(new DOMParser().parseFromString("', '').replace(
                " 'text/html')).find('body').text()", '').replace('"', '').replace(',', '').replace(' ', '').replace(
                '\n', '').rstrip()

        b = 'https://phinf.pstatic.net/tvcast'
        end2 = a.find('channelName', start2)
        thumbs = a[end1:end2]
        thumb = b + thumbs.replace("thumbnail: '", '').replace("'", '').replace(',', '').replace('\n', '').rstrip()

    return key, id, title, thumb

def play_video(id, key):
    url = 'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{}'.format(id)
    data = {
            'key': key,
            'devt': 'html5_pc'
            }

    req = requests.get(url=url, params=data).json()
    l = req['videos']['list']
    try:
        if l[0]['encodingOption']['name'] == '1080P':
            play = l[0]['source']

        elif l[4]['encodingOption']['name'] == '720P':
            play = l[4]['source']

        elif l[3]['encodingOption']['name'] == '480P':
            play = l[3]['source']

        elif l[2]['encodingOption']['name'] == '360P':
            play = l[2]['source']

        elif l[1]['encodingOption']['name'] == '270P':
            play = l[1]['source']

        else:
            play = l[0]['source']

    except:
        play = ''

    return play

def listset(title, thumb, play, isfolder):
    li = xbmcgui.ListItem(title, iconImage=thumb)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=play, listitem=li, isFolder=isfolder)

def folder(title, thumb, mode, mode1, isfolder):
    play = build_url({'mode': mode, 'mode1':mode1, 'foldername': title})
    listset(title, thumb, play, isfolder)


mode = args.get('mode', None)
mode1 = args.get('mode1', None)

if mode is None:
    folder('TOP100', 'DefaultFolder.png', 'TOP100', 'TOP100', True)
    folder('LIVE', 'DefaultFolder.png', 'LIVE', 'LIVE', True)
    folder('지금 뜨는', 'DefaultFolder.png', '지금 뜨는', '지금 뜨는', True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'TOP100':
    top_video()
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == '지금 뜨는':
    now_video()
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'LIVE':
    live_video()
    xbmcplugin.endOfDirectory(addon_handle)