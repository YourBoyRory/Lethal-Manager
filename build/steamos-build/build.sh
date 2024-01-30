#!/bin/bash
touch ./package/icon.png
cp ../Lethal-Manager.jar ./package/Lethal-Manager.jar
cp ../../assets/Lethal-Icon-small.png ./Lethal-Icon.png

echo "[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Exec=$(pwd)/package/jre/bin/java
Name=java
Categories=Utility
Icon=icon" > ./package/java.desktop

export LD_LIBRARY_PATH=$(pwd)/package/jre/lib/amd64/server/
linuxdeployqt ./package/java.desktop -appimage

mv ./package/Lethal-Manager.jar ./Lethal-Manager.jar
