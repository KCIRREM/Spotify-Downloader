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
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'download_archive': path_to_yt_music + 'download_archive'}


def update_id3(path_to_file, artwork_file_name, artist, track_num):
    # edit the ID3 tag to add the title, artist, artwork, date, and genre
    audiofile = eyed3.load(path_to_file)
    audiofile.initTag(version=(2, 3, 0))
    audiofile.tag.artist = artist
    audiofile.tag.track_num = track_num
    audiofile.tag.date = localtime().tm_year
    response = urllib.request.urlopen(artwork_file_name)
    imagedata = response.read()
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u"cover")
    audiofile.tag.save()


# set all the necessary lists
download_archive_list = []
downloaded = []
links = []
output = []
thumbnail_list = []
playlist_file = []

# find the elements of the page
path = (filedialog.askdirectory() + '/')
url = input('Enter the spotify playlist')
res = requests.get(url)
html_page = res.content
soup = BeautifulSoup(html_page, 'lxml')
text = soup.find_all(text=True)
elements_of_page = set([t.parent.name for t in text])
blacklist = ['title', '[document]', 'style', 'h1', 'script']
# {'script','h1','[document]','title','style'}

# check if user has deleted any files saved in the archive and update the list accordingly
if os.path.exists(path + 'saved_songs.txt'):
    list_of_current_files = os.listdir(path)
    list_of_current_files = (set(list_of_current_files) - {'download_archive', 'saved_songs.txt'})
    with open(path + 'saved_songs.txt', 'r') as saved_songs:
        data = saved_songs.readlines()
    data_for_check = [i[:-1] for i in data][1::2]
    data_names = data[1::2]
    check = [item + '\n' for item in list(set(data_for_check) - list_of_current_files)]
    if len(check) > 0:
        with open(path + 'download_archive', 'r') as file:
            data_links = file.readlines()
            for idx, val in enumerate(check):
                yt_link = data[(data.index(val)) - 1]
                print(yt_link)
                data_links.remove(yt_link)
        with open(path + 'download_archive', 'w') as file:
            file.writelines(data_links)
        for idx, val in enumerate(check):
            yt_link = data[(data.index(val)) - 1]
            data.remove(yt_link)
            data.remove(val)
        with open(path + 'saved_songs.txt', 'w') as saved_songs:
            saved_songs.writelines(data)

# create an appropriate list of song names, artists and track numbers
for idx, val in enumerate(text):
    if val.parent.name not in blacklist:
        if val.isdigit():
            output.append([val])
            i = idx + 1
            try:
                while not text[i].isdigit():
                    output[len(output) - 1].append(text[i])
                    i = i + 1
            except Exception as IndexError:
                break

# check whether the url is a playlist or an album
url_output = str((urllib.request.urlopen(url)).read().decode())
if ((''.join((url.split('https://open.spotify.com/')).pop(1))).split('/', 1)).pop(0) == 'playlist':
    num = output[len(output) - 1].index('You might also like')
    what_to_delete = output[len(output) - 1]
    del what_to_delete[num:]
    url_urls = (url_output.split('https://open.scdn.co/cdn/images/favicon32.8e66b099.png'))
    url_urls = url_urls.pop((len(url_urls) - 1))

else:
    num = output[(len(output)) - 1].index(output[len(output) - 2][(len(output[len(output) - 2])) - 1])
    what_to_delete = output[len(output) - 1]
    del what_to_delete[num:]
    del output[0]
    url_urls = url_output

# pull all the spotify track urls
print(output)
spotify_urls = re.findall('https://open.spotify.com/track/[a-zA-Z0-9]+', url_urls)
print(len(spotify_urls))
print(spotify_urls)
list_of_pre_existing_files = os.listdir(path)
print(list_of_pre_existing_files)

# get the song thumbnail, should I make this optional?
for i in range(0, len(spotify_urls)):
    thumbnail_track = re.search('https://i.scdn.co/image/[a-zA-Z0-9]+',
                                (str((urllib.request.urlopen(spotify_urls[i])).read().decode()))).group(0)

    # begin the youtube search query and show the user
    print('Downloading track: ', i)
    print(('"' + (((' '.join(
        [output[i][item] for item in range(0, len(output[i])) if output[i][item].isdigit() == False])).replace(" ",
                                                                                                               "+")) + '"')))
    youtube_query = urllib.request.urlopen(
        'https://www.youtube.com/results?search_query=' + ('"' + (((' '.join(
            [output[i][item] for item in range(0, len(output[i])) if output[i][item].isdigit() == False])).replace(" ",
                                                                                                                   "+")) + '"')))
    video_id = 'https://www.youtube.com/' + (re.search(r"watch\?v=(\S{11})", youtube_query.read().decode())).group(
        0)

    # download the youtube song
    with yt_dlp.YoutubeDL((options(path))) as ydl:
        ydl.download(video_id)

    # find the name of the song, there is no integration for this in yt-dlp
    list_of_new_files = os.listdir(path)
    file_name = ''.join(
        set(list_of_new_files) - set(list_of_pre_existing_files) - {'download_archive', 'saved_songs.txt'})
    print(file_name)
    if (output[i][1]).count('/') > 0:
        output[i][1] = (output[i][1].replace('/', ','))

    # rename it to its desire name, if it already exists then don't attempt to rename it
    try:
        os.rename((path + file_name), (path + (output[i][1]) + '.mp3'))
    except Exception as FileExistsError:
        pass

    # append to the download list in order to create an archive amd prevent multiple downloads
    downloaded.append((output[i][1] + '.mp3' + '\n'))
    print((path + (output[i][1]) + '.mp3'))

    # Tag the file
    update_id3((path + (output[i][1]) + '.mp3'), thumbnail_track, (' '.join(
        [output[i][item] for item in range(0, len(output[i])) if output[i][item].isdigit() == False and item != 1])),
               int(output[i][0]))
    list_of_pre_existing_files.append(output[i][1] + '.mp3')
    playlist_file.append((path + (output[i][1]) + '.mp3' + '\n'))

# find the playlist directory and create one compatible with yt-music
path_to_m3u = (filedialog.askdirectory()) + '/'
name = ''.join([item for item in text if item.parent.name == 'title'])
print(path)

# check if the playlist name already exists
if os.path.exists(path_to_m3u + ''.join((name.split('|')).pop(0)) + '.m3u'):
    print('a playlist with that name has already been saved')
else:
    with open((path_to_m3u + ''.join((name.split('|')).pop(0)) + '.m3u'), 'w', ) as file:
        file.writelines(playlist_file)

# write the downloaded files to an archive and save this is so that I can fix any accidental deletions or purpose full deletions by the user, warning he option of deleting it from the playlist file has not been added yet meaning it may corrupt the palylist
with open((path + 'download_archive'), 'r+') as file:
    lines = [line.rstrip() for line in file]
    for i in range(0, len(lines)):
        download_archive_list.append(lines[i] + '\n' + downloaded[i])

with open((path + 'saved_songs.txt'), 'w') as file:
    file.writelines(download_archive_list)

# print out the songs downloaded (for aesthetic purposes only)
print('Songs Downloaded:')
for idx, val in enumerate(output):
    for idx2, val2 in enumerate(output[idx]):
        if idx2 == 1:
            print(val2)

