#!/usr/bin/env python3
# coding=UTF-8

#sys.path.append(os.path.abspath("~/PersistentMPDClient"))
# link or copy PersistentMPDClient into local dir
from PersistentMPDClient import PersistentMPDClient

from mpd import MPDClient, MPDError, CommandError

import pyttsx3

import signal # allow Ctrl-C, never end the program
import sys
import RPi.GPIO as GPIO

import datetime # button debounce
from datetime import timedelta
BTN_LEFT_GPIO = 3
BTN_PLAY_GPIO = 15
BTN_RIGHT_GPIO = 27

BTN_DEBOUNCE = 50

# clean up on Ctrl-C
def signal_handler(sig, frame):
  print("Received signal:", sig, "-", signal.Signals(sig).name)
  GPIO.cleanup()
  mpd.close()                     # send the close command
  mpd.disconnect()                # disconnect from the server
  sys.exit(0)

#    try:
#      mpd.next()
#    except MPDError as e:
#      if isinstance(e, CommandError):
#        speak("Es wird gerade kein Titel gespielt")
#      else:
#        print(type(e))
#        print(e)
#        speak ("Fehler: ")

def get_track_name(track):
  split1 = track.get("file").split("/")
  split2 = split1[-1].split(".")
  return split1[-2]+ " Kapitel "+split2[0]

cb_pressed_time = datetime.datetime(year=2020,month=1,day=1)

def btn_callback(channel):
  global cb_pressed_time

  curr_edge = GPIO.input(channel)
  if curr_edge:
    print ("Button released:", channel)
    print ("now - pressed", datetime.datetime.now() - cb_pressed_time)
    interval = (datetime.datetime.now() - cb_pressed_time) / timedelta(milliseconds=1)
    cb_pressed_time = datetime.datetime(year=2020,month=1,day=1)
    print ("interval ms", interval)

    if interval <= 500:
      if channel == BTN_LEFT_GPIO:
        btn_left_cb(channel)
      elif channel == BTN_RIGHT_GPIO:
        btn_right_cb(channel)
    else:
      if channel == BTN_LEFT_GPIO:
        play_prev_dir()
      elif channel == BTN_RIGHT_GPIO:
        play_next_dir()

  else:
    print ("Button pressed:", channel)
    cb_pressed_time = datetime.datetime.now()
    if channel == BTN_PLAY_GPIO:
      btn_play_cb(channel)

def get_current_book(currentsong):
  count = -1
  split = currentsong.get("file").split("/")
  bookname = split[-2]
  for song in mpd.listall():
    dir = song.get("directory")
    if dir:
      count += 1 # count only dir type entries
      if dir == bookname:
        print ("current book", count)
        return count

  return -1

def play_dir(richtung, text):
  next_book = get_current_book(mpd.currentsong()) + richtung
  print ("next book", next_book)
  count = -1
  for song in mpd.listall():
    if song.get("directory"):
      print("searching for books", count)
      count += 1 # count only dir type entries
      if count == next_book:
        mpd.clear()
        print("add dir:", song.get("directory"))
        mpd.add(song.get("directory"))
        mpd.play()
        print_mpd_status("Book")
        mpd.pause()
        speak("Spiele " + text + " Buch " + get_track_name(mpd.currentsong()))
        mpd.pause()
        return
  mpd.pause()
  speak("Kein " + text + " Buch vorhanden")
  mpd.pause()


def play_prev_dir():
  play_dir (-1, "vorheriges")

def play_next_dir():
  play_dir (+1, "nächstes")

def btn_left_cb(channel):
  if not mpd.currentsong() or mpd.status().get("state") == "stop":
    mpd.play()
  mpd.previous()
  mpd.pause()
  speak("Spiele vorherigen Titel "+ get_track_name(mpd.currentsong()))
  mpd.pause()
  print_mpd_status("Left")

def btn_play_cb(channel):
  if mpd.status().get("state") == "play":
    mpd.pause()
    speak("Pause")
  else:
    speak("Abspielen")
    mpd.pause()
  print_mpd_status("Play")

def btn_right_cb(channel):
  if not mpd.currentsong() or mpd.status().get("state") == "stop":
    mpd.play()
  mpd.next()
  mpd.pause()
  speak("Spiele nächsten Titel "+ get_track_name(mpd.currentsong()))
  mpd.pause()
  print_mpd_status("Right")

def print_mpd_status(msg):
  print(msg, "\t", mpd.status().get("state"), "\t", len(mpd.playlistinfo()), "\t", mpd.currentsong().get("file"))

def speak(msg):
  print("Speaking:", msg)
  tts.say(msg)
  tts.runAndWait()

if __name__ == '__main__':

  print ("*** Init Text-To-Speech")
  tts  = pyttsx3.init()
  tts.setProperty('rate', 150)
  tts.setProperty('volume', 1.0)
  tts.setProperty("voice", "german")

  print ("*** Init GPIO")
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(BTN_LEFT_GPIO,  GPIO.IN)
  GPIO.setup(BTN_PLAY_GPIO,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(BTN_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.add_event_detect(BTN_LEFT_GPIO,  GPIO.BOTH, callback=btn_callback, bouncetime=BTN_DEBOUNCE)
  GPIO.add_event_detect(BTN_PLAY_GPIO,  GPIO.BOTH, callback=btn_callback, bouncetime=BTN_DEBOUNCE)
  GPIO.add_event_detect(BTN_RIGHT_GPIO, GPIO.BOTH, callback=btn_callback, bouncetime=BTN_DEBOUNCE)

  print ("*** Init MPD")
  mpd = PersistentMPDClient(host="localhost", port=6600)
  mpd.timeout = 1                 # network timeout in seconds
  mpd.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
  print("MPD Version:", mpd.mpd_version)

  print("*** Init Screen")
  print("Button\t Status\t Queue\t Song")
  print_mpd_status("Init")

  print("*** Init Player")
  if not mpd.playlistinfo():

    for song in mpd.listall():
       # füge alle Titel hinzu, hoffentlich alphabetisch
#      if song.get("file"):
#        print("add song:", song.get("file"))
#        mpd.add(song.get("file"))

      # füge erstes Verzeichnis hinzu
      if song.get("directory"):
        print("add dir:", song.get("directory"))
        mpd.add(song.get("directory"))
        break
    print_mpd_status("Added")

  if not mpd.currentsong():
    mpd.play()
    speak("Spiele Titel "+ get_track_name(mpd.currentsong()))

  print("*** Init Finished, Button Monitor Online")
  signal.signal(signal.SIGINT, signal_handler)
  signal.pause() # wait for Ctrl-C

