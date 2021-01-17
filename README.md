# RaspberryMediaPlayer
Python server that monitors GPIO buttons and controls the MPD player. It is meant for a headless debian installation on a raspberry pi (tested: 1B and ZeroW), but might work on other devices having a compatible gpio library.

This project contains two files. 
- A Python script that monitors GPIO buttons and issues commands to the mpd deamon. It also speaks a feedback to the audio channel on the actions done. 
- a service file to make systemd start the Python script in background

## Requirements
On Raspian buster you need to install via APT:
- mpd git libespeak1
- python3-pip python3-mpd python3-gst-1.0 python3-rpi.gpio

optional for manually fiddling with mpd and gpio:
- mpc gpio-utils

and via pip3:
- pyttsx3

On other platforms package names may be different. 
And some python3 packages might be better to install via pip3.

## Installation
- install the above mentioned packages
- checkout the source
- copy service file to /etc/systemd... 
- edit service file to point to the checked out Pyhton-script
- chown root:root service-file
- enable service

## Configuration
- check your audio volume using alsamixer
- check your audio device using ...
- ...
- set up wifi
- set up NTP in /etc/systemd/timesyncd.conf

