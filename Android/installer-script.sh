echo "installing rust"
pkg install rust
export 	CARGO_BUILD_TARGET=aarch64-linux-android
echo "installing python"
pkg install pyhton
echo "ugrading packages"
pkg upgrade
echo "installing packages"
pip install selenium
pip install beautifulsoup4
pip install yt-dlp
pip install requests
echo "installing ffmpeg"
pkg install ffmpeg
echo "finished"
