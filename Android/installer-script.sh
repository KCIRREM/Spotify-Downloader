#! /bin/bash
echo "installing python"
pkg install -y python
echo "ugrading packages"
pkg upgrade
echo "installing packages"
pip install wheel
pip install setuptools
pip install yt-dlp
pip install time
pip install eyed3
echo "installing ffmpeg"
pkg install ffmpeg -y
echo "finished"
