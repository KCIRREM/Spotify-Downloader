import re
import urllib.request
import glob
import os
from time import localtime
import yt_dlp
import eyed3
blacklist = []


def get_filepaths():
    list_files = (os.listdir(path_to_playlist + '/'))
    name = ''.join(set(list_files) - set(blacklist))
    blacklist.append(name)
    return name

def update_id3(path_to_file, artwork_file_name, artist, item_title):
    #edit the ID3 tag to add the title, artist, artwork, date, and genre
    audiofile = eyed3.load(path_to_file)
    audiofile.initTag(version=(2, 3, 0))
    audiofile.tag.artist = artist
    audiofile.tag.date = localtime().tm_year
    audiofile.tag.title = item_title
    response = urllib.request.urlopen(artwork_file_name)
    imagedata = response.read()
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u"cover")
    audiofile.tag.save()


def options(path_to_playlist,name):
    return {'format': 'ba', 'outtmpl': (path_to_playlist + '/%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]}

def split(str_variable, sep, pos):
    str_variable = str_variable.split(sep)
    return sep.join(str_variable[:pos]), sep.join(str_variable[pos:])


def delete_leftover(path):
    list_test = glob.glob((path + '/*.*'))
    for item in range(0, len(list_test)):
        check = os.path.basename(list_test[item])
        if check.endswith('.mp3') or check.startswith('download_archive') and check.endswith('.txt'):
            pass
        else:
            os.remove(list_test[item])

def split_file(spl1,spl2,list_spl):
    return (re.split(f'(?<={spl1})(.*?)(?={spl2})', list_spl))

all_file_names = ['#EXTM3U\n']
info_list = {}
spotify_art_list = []
find_song_names_list = []
spotify_artists = []
all_file_names_download_archive = []

rem_d = 'false'
yt_link = input('paste in the spotify link')
youtube_response = urllib.request.urlopen(yt_link)
lookup_tracks = '"@spotify" /><meta property='
yt = str(youtube_response.read().decode())

split_description = ''.join((re.split('content=\"[0-9]+\" /><meta property=\"og:title\" content=\"',yt)).pop(1))
playlist_name = (split_description.split('"',1))[0]
playlist_owner = (((((split_description.split('content="',1)))[1]).split('·'))[0])[:-1]
playlist_song_amount = (re.search('·\s(\d+)',split_description)).group(1)
#print(split_description)
playlist_thumbnail = re.search('https://i\.scdn\.co/image/[a-zA-Z0-9]+',split_description).group(0)
split_tracks = split_description.split(f'content="{playlist_name}"')
get_tracks2 = re.findall('https://open\.spotify\.com/track/[a-zA-Z0-9]+',(str(split_tracks[1]).split('.gxaSIL *{pointer-events:all;}/*!sc*/',1))[1])
content_counter = 0

info_list['playlist_owner'] =playlist_owner
info_list['playlist_title'] = playlist_name
info_list['song_amount'] = int(playlist_song_amount)
info_list['thumbnail'] = playlist_thumbnail

song_name_part1 = 'data-testid="entity-row-v2-button" aria-label="track '
song_name_part2 = '" class="EntityRowV2__PlayPauseButton'
find_song_names = re.findall(f'(?<={song_name_part1})(.*?)(?={song_name_part2})', yt)
for i in range(0, (len(find_song_names))):
    spotify_artist = str((urllib.request.urlopen(get_tracks2[i])).read().decode())
    if str(find_song_names[i]).count('x27') > 0:
        find_song_names[i] = str(find_song_names[i]).replace('x27','039')
    try:
        split_spotify_producer = (''.join(((''.join((spotify_artist.split(((find_song_names[i]) + ' - song by'), 1)).pop(1))).split(' |',1)).pop(0)))[1:]
    except Exception as Argument:
        split_spotify_producer = (''.join(
            ((''.join((spotify_artist.split(((find_song_names[i]) + ' - song and lyrics by'), 1)).pop(1))).split(' |', 1)).pop(
                0)))[1:]

    spotify_artists.append(split_spotify_producer)
    find_song_names_list.append((split_spotify_producer + ' ' + '-' + ' ' + find_song_names[i]))
    split_spotify_art = (''.join((split_file('meta property="og:image" content="',' /><meta property=',spotify_artist)).pop(1))).replace('"', '')
    spotify_art_list.append(split_spotify_art)

path = '/storage/emulated/0/Download'
path_to_playlist = (path + '/YT Music')
if os.path.exists(path_to_playlist):
    rem_d = 'true'
    with open((path_to_playlist + '/' + 'download_archive.txt'), 'r+') as file:
        for line in file:
            line = (line.strip()) # preprocess line
            blacklist.append(line)
    pass
else:
    os.mkdir((path + '/YT Music'))


for i in range(0, len(find_song_names)):
    youtube_response = (urllib.request.urlopen(
        'https://www.youtube.com/results?search_query=' + ('"'+((find_song_names_list[i]).replace(" ", "+"))+'"')))
    video_ids = 'https://www.youtube.com/' + (re.search(r"watch\?v=(\S{11})", youtube_response.read().decode())).group(0)
    with yt_dlp.YoutubeDL(options(path_to_playlist=path_to_playlist, name=find_song_names[i])) as ydl:
        ydl.download(video_ids)
    delete_leftover(path_to_playlist)
    list_files = (os.listdir(path_to_playlist + '/'))
    if rem_d == 'true':
        list_files.remove('download_archive.txt')
    name = ''.join(set(list_files) - set(blacklist))
    old_path = path_to_playlist + '/' + name

    update_id3(old_path, spotify_art_list[i], spotify_artists[i], find_song_names[i])
    try:
        os.rename(old_path, (path_to_playlist + '/' + find_song_names_list[i]) + '.mp3')
    except Exception as Argument:
        print('this file has already been download')
        os.remove(old_path)
    blacklist.append(find_song_names_list[i] + '.mp3')
    all_file_names.append(path_to_playlist + '/' + find_song_names_list[i] + '.mp3' + '\n')
    all_file_names_download_archive.append(find_song_names_list[i]+'.mp3' + '\n')

path_to_m3u = '/storage/emulated/0/Music'
if os.path.exists(path_to_m3u  + '/' + info_list['playlist_title'] + '.m3u') == True:
    print('a playlist with that name has already been saved')
else:
    with open((path_to_m3u  + '/' + info_list['playlist_title'] + '.m3u'), 'w',) as file:
        file.writelines(all_file_names)
with open((path_to_playlist + '/' + 'download_archive.txt'), 'w') as file:
    file.writelines(all_file_names_download_archive)
