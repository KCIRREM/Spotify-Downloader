#! /bin/bash
echo "installing python"
pkg install -y python
echo "ugrading packages"
pkg upgrade
echo "installing packages"
pip install wheel
pip install setuptools
pip install yt-dlp
pip install eyed3
pip install requests
pip install bs4
pip instal beautifulsoup4
pkg install libxslt
pip install lxml
echo "installing ffmpeg"
pkg install ffmpeg -y
echo "finished"
