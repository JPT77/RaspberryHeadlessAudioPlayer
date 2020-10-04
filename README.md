# RaspberryMediaPlayer
Python server that monitors GPIO buttons and controls the MPD player. It is meant for a headless debian installation on a raspberry pi, but might work on other devices having a compatible gpio library.

This project contains two files. 
- A Python script that monitors GPIO buttons and issues commands to the mpd deamon. It also speaks a feedback to the audio channel on the actions done. 
- a service file to make systemd start the Python script in background

## Requirements
- python3
- pip3
- pyttsx3
- mpd
- gstreamer
- gpio?
- ...

## Installation
- install the above mentioned packages
- checkout the source
- copy service file to /etc/systemd... 
- edit service file to point to the checked out Pyhton-script
- chown root:root service-file
- enable service

## configuraten
- check your audio volume using alsamixer
- check your audio device using ...
- ...
