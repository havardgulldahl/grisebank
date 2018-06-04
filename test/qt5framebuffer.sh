# thank you http://www.jumpnowtek.com/rpi/pitft-displays-and-qt5.html
# also see https://doc.qt.io/qt-5/embedded-linux.html#linuxfb

echo "run app on tft using linuxfb"
qt5ct -platform linuxfb:fb=/dev/fb1

echo "run app on tft using eglfs"
qt5ct -platform eglfs

