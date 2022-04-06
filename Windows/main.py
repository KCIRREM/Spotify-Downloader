import os
import re
import urllib.request
from time import localtime
import requests
from bs4 import BeautifulSoup
import yt_dlp
import eyed3
from tkinter import filedialog


def options(path_to_yt_music):
    return {'format': 'ba', 'outtmpl': (path_to_yt_music + '/%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],'download_archive':path_to_yt_music + 'download_archive'}

def update_id3(path_to_file, artwork_file_name, artist,track_num):
    #edit the ID3 tag to add the title, artist, artwork, date, and genre
    audiofile = eyed3.load(path_to_file)
    audiofile.initTag(version=(2, 3, 0))
    audiofile.tag.artist = artist
    audiofile.tag.track_num = track_num
    audiofile.tag.date = localtime().tm_year
    response = urllib.request.urlopen(artwork_file_name)
    imagedata = response.read()
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u"cover")
    audiofile.tag.save()



links = []
output = []
thumbnail_list = []
playlist_file = []

url = input('Enter the spotify playlist')
res = requests.get(url)
html_page = res.content
soup = BeautifulSoup(html_page, 'lxml')
text = soup.find_all(text=True)
elements_of_page = set([t.parent.name for t in text])
#print(elements_of_page)
blacklist = ['title','[document]','style','h1','script']
            #{'script','h1','[document]','title','style'}

for idx, val in enumerate(text):
    if val.parent.name not in blacklist:
        if val.isdigit() == True:
            output.append([val])
            i = idx + 1
            try:
                while text[i].isdigit() == False:
                    output[len(output)-1].append(text[i])
                    i = i +1
            except Exception as IndexError:
                break
url_output = str((urllib.request.urlopen(url)).read().decode())
if ((''.join((url.split('https://open.spotify.com/')).pop(1))).split('/',1)).pop(0) == 'playlist':
    #print(output)
    num = output[len(output)-1].index('You might also like')
    what_to_delete = output[len(output) - 1]
    del what_to_delete[num:]
    url_urls = (url_output.split(((re.search('https://i.scdn.co/image/[a-zA-Z0-9]+', url_output)).group(0))))
    url_urls = url_urls.pop((len(url_urls) - 1))
else:
    num = output[(len(output))-1].index(output[len(output) - 2][(len(output[len(output) - 2]))-1])
    what_to_delete = output[len(output) - 1]
    del what_to_delete[num:]
    del output[0]
    url_urls = url_output

print(output)
spotify_urls = re.findall('https://open.spotify.com/track/[a-zA-Z0-9]+',url_urls)
print(len(spotify_urls))
print(spotify_urls)
path = (filedialog.askdirectory()+'/')
list_of_pre_existing_files = os.listdir(path)
print(list_of_pre_existing_files)
#print(str((urllib.request.urlopen(spotify_urls[0])).read().decode()))

for i in range(0,len(spotify_urls)):
    thumbnail_track = re.search('https://i.scdn.co/image/[a-zA-Z0-9]+',(str((urllib.request.urlopen(spotify_urls[i])).read().decode()))).group(0)
    thumbnail_list.append(thumbnail_track)
    print('Downloading track: ', i)
    print(('"'+(((' '.join([output[i][item] for item in range(0,len(output[i])) if output[i][item].isdigit()==False])).replace(" ", "+"))+'"')))
    youtube_query = urllib.request.urlopen(
        'https://www.youtube.com/results?search_query=' + ('"'+(((' '.join([output[i][item] for item in range(0,len(output[i])) if output[i][item].isdigit()==False])).replace(" ", "+"))+'"')))
    video_id = 'https://www.youtube.com/' + (re.search(r"watch\?v=(\S{11})", youtube_query.read().decode())).group(
        0)
    with yt_dlp.YoutubeDL((options(path))) as ydl:
        ydl.download(video_id)

    os.rename((path + 'download_archive'),(path + 'download_archive.txt'))
    list_of_new_files = os.listdir(path)
    file_name = ''.join(set(list_of_new_files)-set(list_of_pre_existing_files))
    print(file_name)
    if (output[i][1]).count('/') > 0:
        output[i][1] = (output[i][1].replace('/',','))

    try:
        os.rename((path+file_name),(path + (output[i][1])+ '.mp3'))
    except Exception as FileExistsError:
        pass

    with open(path + 'download_archive.txt', 'r')  as file:
        downloaded = file.readlines()
    downloaded[i] += (output[i][1] + '\n')
    with open(path + 'download_archive.txt','w') as file:
        file.writelines(downloaded)

    print((path + (output[i][1])+ '.mp3'))
    update_id3((path + (output[i][1]) + '.mp3'),thumbnail_track,(' '.join([output[i][item] for item in range(0,len(output[i])) if output[i][item].isdigit()==False and item != 1])),int(output[i][0]))
    list_of_pre_existing_files.append(output[i][1] + '.mp3')
    playlist_file.append((path + (output[i][1]) + '.mp3' + '\n'))
    print(list_of_pre_existing_files)
    print(list_of_new_files)

path_to_m3u = (filedialog.askdirectory()) + '/'
name = ''.join([item for item in text if item.parent.name == 'title'])
if os.path.exists(path_to_m3u  + name + '.m3u') == True:
    print('a playlist with that name has already been saved')
else:
    with open((path_to_m3u  + name + '.m3u'), 'w',) as file:
        file.writelines(playlist_file)

print('songs downloaded:')
for idx, val in enumerate(output):
    for idx2, val2 in enumerate(output[idx]):
        if idx2 == 1:
            print(val2)
