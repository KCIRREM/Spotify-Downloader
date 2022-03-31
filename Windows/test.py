import yt_dlp
import os
import glob
import requests
from tkinter import filedialog
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def delete_leftover(path):
    list_test = glob.glob((path + '/*.*'))
    for item in range(0, len(list_test)):
        check = os.path.basename(list_test[item])
        if check.endswith('.mp3'):
            pass
        else:
            os.remove(list_test[item])


def ydl_options(path):
    global ydl_opts
    ydl_opts = {'format': 'ba','outtmpl': (path + '/%(title)s.%(ext)s'), 'writethumbnail': True,
                'download_archive': 'downloaded_songs.txt',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}, {'key': 'EmbedThumbnail',
                                                                                            'already_have_thumbnail': False}]}


def bypass_yt(consent_button_css):
    consent = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, consent_button_css)))
    consent = driver.find_element(By.CSS_SELECTOR, consent_button_css)
    consent.click()

a_or_p = input('are you running android (a) or pc (p)')
if a_or_p == 'a':
    print('you must have chrome installed for this to run')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('androidPackage', 'com.android.chrome')
    driver = webdriver.Chrome('./chromedriver', options=options)
else:
    pass
spotify_yt = input('would you like to download a youtube or spotify playlist')

if spotify_yt == 'yt':
    output = []
    list_songs = []
    link_list = []

    url = input('paste the spotify playlist url')
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    elements_of_page = set([t.parent.name for t in text])
    print(elements_of_page)
    blacklist = ['script', 'style', 'span', 'title', '[document]', 'h1', 'script']

    for t in text:
        if t.parent.name not in blacklist:
            print(str(t))
            output.append(t)
    del output[0]
    length = (int(input('enter the length of the spotify playlist'))) * 2
    output = output[:length]
    print(output)

    for i in range(0, length):

        if i % 2 == 0:
            new_item = output[i - 1] + ' ' + output[i]
            list_songs.append(new_item)
        else:
            pass

    path = os.path.abspath(filedialog.askopenfile().name)
    driver = webdriver.Chrome(executable_path=path)

    for i in range(0, (len(list_songs))):
        query_search = 'https://www.youtube.com/results?search_query=' + (
            ('"' + (str(list_songs[i])) + '"').replace(' ', '+'))
        driver.get(query_search)
        if i == 0:
            bypass_yt("[aria-label='Agree to the use of cookies and other data for the purposes described']")
        else:
            pass

        bypass_yt('[class="text-wrapper style-scope ytd-video-renderer"]')
        consent_button_css = '[class="text-wrapper style-scope ytd-video-renderer"]'
        link_list.append(driver.current_url)
        if i == (len(list_songs)) - 1:
            driver.quit()
    for i in range(0, len(link_list)):
        with yt_dlp.YoutubeDL(ydl_options(path)) as ydl:
            ydl.download(link_list[i])
    delete_leftover(path)


else:
    link = input('enter the youtube playlist link')
    path = os.path.abspath(filedialog.askdirectory())
    with yt_dlp.YoutubeDL(ydl_options(path)) as ydl:
        ydl.download([link])
    delete_leftover(path)
